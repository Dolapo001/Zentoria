import string
import random
from django.utils import timezone
from datetime import timedelta
import pyotp
from .utils import RequestError, ErrorCode, Response, CustomResponse
from django.db import IntegrityError
from django.contrib.auth import authenticate
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView
)
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
    TokenBlacklistSerializer
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .emails import send_mail, send_otp_email
from .models import OTP, User, Profile
from .otp_utils import get_or_generate_otp_secret, generate_otp, validate_otp
from .serializers import (
    RegisterSerializer,
    ResendOTPSerializer,
    VerificationSerializer,
    ResendEmailVerificationSerializer,
    ProfileSerializer,
    ChangeEmailSerializer,
    ChangePasswordSerializer,
    RequestEmailChangeCodeSerializer,
    RequestNewPasswordCodeSerializer,
    LoginSerializer,
    SendOTPSerializer
)


def custom_response(data, message, status_code, status_text=None, tokens=None):
    status_code = int(status_code)

    response_data = {
        "status_code": status_code,
        "message": message,
        "data": data,
    }

    if status_text is not None:
        response_data["status"] = status_text

    if tokens is not None:
        response_data["tokens"] = tokens

    return Response(response_data, status=status_code)


class UserRegistrationView(APIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        password = validated_data.pop('password', None)
        try:
            user = User.objects.create_user(email=validated_data['email'],
                                            username=validated_data['username'],
                                            password=password,
                                            fullname=validated_data['fullname'])
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response({"message": "An error occurred during user creation"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        email = validated_data["email"]
        password = validated_data["password"]
        user = authenticate(request, email=email, password=password)

        if user:
            tokens = super().post(request)
            data = {"email": user.email, "fullname": user.fullname}

            return custom_response(
                data=data,
                message="Logged in successfully",
                status_code=status.HTTP_200_OK,
                status_text="success",
                tokens=tokens.data
            )
        else:
            return custom_response(
                data="Invalid credentials",
                message="Invalid credentials",
                status_code=status.HTTP_400_BAD_REQUEST,
                status_text="error"
            )


class RefreshTokenView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        access_token = validated_data.get('access')
        return Response({
            "message": "Refreshed successfully",
            "token": access_token,
            "status": "success"
        }, status=status.HTTP_200_OK)


class Logout(TokenBlacklistView):
    serializer_class = TokenBlacklistSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return custom_response("Logged out successfully.", status.HTTP_200_OK, "success")
        except TokenError:
            return custom_response("Token is blacklisted.", status.HTTP_400_BAD_REQUEST, "failed")


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get(self, request):
        user_profile = Profile.objects.get(user=request.user)
        serializer = self.serializer_class(user_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        user_profile = Profile.objects.get(user=request.user)
        serializer = self.serializer_class(user_profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            old_password = validated_data.get("old_password")
            new_password = validated_data.get("new_password")

            user = authenticate(request, old_password=old_password)

            if user:
                user.set_password(new_password)
                user.save()
                return custom_response(None, 'Password changed successfully', status.HTTP_200_OK, 'success')
            else:
                return custom_response(None, 'Invalid old password', status.HTTP_400_BAD_REQUEST, 'error')

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RequestEmailChangeCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = RequestEmailChangeCodeSerializer(data=request.data)
            if serializer.is_valid():
                user = request.user
                new_email = serializer.validated_data['email']

                otp_secret = get_or_generate_otp_secret(user)
                otp = generate_otp(otp_secret.secret)

                user.email_change_code = otp
                user.save()

                send_otp_email(user, email=new_email, template='email_change_verification_template.html')

                return Response({'message': 'Email change code sent successfully'}, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            data = {
                "error_message": f"An error occurred while requesting email change code: {str(e)}",
            }
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResendEmailVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = ResendEmailVerificationSerializer(data=request.data)
            if serializer.is_valid():
                user = request.user

                new_verification_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

                user.profile.verification_token = new_verification_token
                user.profile.save()

                subject = 'Email Verification'
                context = {'user': user, 'verification_token': new_verification_token}
                message = render_to_string('email_verification_template.html', context)
                plain_message = strip_tags(message)
                from_email = 'your@example.com'
                recipient_list = [user.email]

                send_mail(subject, plain_message, from_email, recipient_list, html_message=message)

                return Response({'message': 'Email verification resent successfully'}, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            data = {
                "error_message": f"An error occurred while resending email verification: {str(e)}",
            }
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SendOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = SendOTPSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            data = {
                "error_message": f"An error occurred while sending OTP: {str(e)}",
            }
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ResendOTPSerializerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = ResendOTPSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()  # This will trigger the logic in ResendOTPSerializer

                return Response({'message': 'OTP resent successfully'}, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            data = {
                "error_message": f"An error occurred while resending OTP: {str(e)}",
            }
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChangeEmailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangeEmailSerializer

    def post(self, request):
        try:
            serializer = self.serializer_class(data=self.request.data)
            serializer.is_valid(raise_exception=True)
            new_email = serializer.validated_data.get('email')
            code = self.request.data.get('code')
            user = self.request.user
            otp = get_or_generate_otp_secret(user)

            current_time = timezone.now()
            expiration_time = otp.created + timedelta(mintues=10)

            if current_time > expiration_time:
                raise RequestError(err_code=ErrorCode.EXPIRED_OTP, err_msg="OTP has expired",
                                       status_code=status.HTTP_400_BAD_REQUEST)

            totp = pyotp.TOTP(otp.secret, interval=600)
            if not totp.verify(code):
                raise RequestError(err_code=ErrorCode.INCORRECT_OTP, err_msg="Invalid OTP",
                                       status_code=status.HTTP_400_BAD_REQUEST)

            if user.email == new_email:
                raise RequestError(err_code=ErrorCode.OLD_EMAIL, err_msg="You can't use your previous email")
            user.email = new_email
            user.email_changed = True
            user.save()
            otp.delete()

            return CustomResponse.success(message="Email changed successfully.")

        except RequestError as re:
            return Response({'error_message': str(re)}, status=re.status_code)

        except Exception as e:
            data = {
                "error_message": f"An error occurred while changing email: {str(e)}",
            }
            return custom_response(data, status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class AccountVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = VerificationSerializer(data=request.data)
            if serializer.is_valid():
                user = request.user
                verification_code = serializer.validated_data['verification_code']
                otp = serializer.validated_data['otp']

                if user.profile.verification_code == verification_code and validate_otp(user, otp):
                    user.profile.is_verified = True
                    user.profile.save()

                    return Response({'message': 'Account successfully verified'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid verification code or OTP'}, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            data = {
                "error_message": f"An error occurred during account verification: {str(e)}",
            }
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)