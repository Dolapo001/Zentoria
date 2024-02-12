import string
import random
from django.utils import timezone
from datetime import timedelta
import pyotp
from .utils import RequestError, ErrorCode, CustomResponse
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
from utils import custom_response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .emails import send_verification_code_email, send_otp_email
from .models import User, Profile
from .otp_utils import get_or_generate_otp_secret, generate_otp, validate_otp, generate_verification_code
from .serializers import (
    RegisterSerializer,
    ResendOTPSerializer,
    VerifySerializer,
    ResendEmailVerificationSerializer,
    ProfileSerializer,
    ChangeEmailSerializer,
    ChangePasswordSerializer,
    RequestEmailChangeCodeSerializer,
    LoginSerializer,
    SendOTPSerializer,
    GoogleSocialAuthSerializer
)


class UserRegistrationView(APIView):

    """
    API endpoint for user registration.

    - Receives user registration data.
    - Creates a new uer, generates a verification code, and sends and sends an email for verification.
    """
    serializer_class = RegisterSerializer

    def post(self, request):
        """
        Handles POST requests for user registration

        :param request: The HTTP request object.

        :returns: JSON response indicating the status of the user creation process.

        """

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        password = validated_data.pop('password', None)
        try:
            user = User.objects.create_user(email=validated_data['email'],
                                            username=validated_data['username'],
                                            password=password,
                                            fullname=validated_data['fullname'])

            verification_code = generate_verification_code()
            user_profile = Profile.objects.create(user=user, verification_code=verification_code)

            send_verification_code_email(user_profile, verification_code)

            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response({"message": "An error occurred during user creation"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(TokenObtainPairView):
    """
    API endpoint for user login.

    - Authenticates user credentials and provides JWT tokens
    """
    serializer_class = TokenObtainPairSerializer

    def post(self, request, **kwargs):

        """
        Handles POST requests for user login.

        :param: request: The HTTP request object.

        :returns: JSON response indicating the status of the login process

        """
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
    """
    API endpoint for refreshing JWT tokens.

    - Allows users to refresh their expired access tokens.

    """
    serializer_class = TokenRefreshSerializer

    def post(self, request, **kwargs):
        """
        Handles POST requests for refreshing JWT tokens.

        :param request: The HTTP request object.
        :return: JSON response indicating the status of the token refresh process.
        """

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
    """
    API endpoint for user registration

    - Blacklists the user's JWT token upon logout.

    """
    serializer_class = TokenBlacklistSerializer

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests for user logout.

        :param request: The HTTP request object.

        :return: JSON response indicating the status of the logout process.

        """

        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return custom_response("Logged out successfully.", status.HTTP_200_OK, "success")
        except TokenError:
            return custom_response("Token is blacklisted.", status.HTTP_400_BAD_REQUEST, "failed")


class ProfileView(APIView):
    """
    API endpoint for user profile management.

    - Requires user authentication.
    - Allows user to retrieve and update their profile.

    """
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get(self, request):

        """

        Handles GET requests for retrieving user profile.

        :param request: The HTTP request object.

        :return: JSON response containing the user's profile data.

        """
        user_profile = Profile.objects.get(user=request.user)
        serializer = self.serializer_class(user_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        """
        Handles PATCH requests for updating user profile.

        :param request: The HTTP request object.

        :return: JSON response that indicates the status of the profile update process

        """
        user_profile = Profile.objects.get(user=request.user)
        serializer = self.serializer_class(user_profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):

    """
    API endpoint for changing user password.

    - Requires user authentication.
    - Allows users to change their passwords.

    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        """
        Handles POST requests for changing user password.

        :param request: The HTTP request object.

        :return: JSON response indicating the status of the password change process.

        """

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
    """
    API endpoint for requesting an email change verification code.

    - Requires user authentication.
    - Allows users to request a code for changing their email address.

    """
    permission_classes = [IsAuthenticated]
    serializer_class = RequestEmailChangeCodeSerializer

    def post(self, request):

        """
        Handles POST requests for requesting an email change verification code.

        :param request: The HTTP request objeect.

        :return: JSON response indicating the status of the email change otp request.
        """

        try:
            serializer = RequestEmailChangeCodeSerializer(data=request.data)
            if serializer.is_valid():
                user = request.user
                new_email = serializer.validated_data['email']

                otp_secret = get_or_generate_otp_secret(user)
                otp = generate_otp(otp_secret.secret)

                user.email_change_code = otp
                user.save()

                send_otp_email(user, email=new_email, template='email_change_verification.html')

                return Response({'message': 'Email change code sent successfully'}, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            data = {
                "error_message": f"An error occurred while requesting email change code: {str(e)}",
            }
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResendEmailVerificationView(APIView):
    """

    """
    permission_classes = [IsAuthenticated]
    serializer_class = ResendEmailVerificationSerializer

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
                message = render_to_string('email_verification.html', context)
                plain_message = strip_tags(message)

                send_verification_code_email(subject, plain_message)

                return Response({'message': 'Email verification resent successfully'}, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            data = {
                "error_message": f"An error occurred while resending email verification: {str(e)}",
            }
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SendOTPView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SendOTPSerializer

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


class ResendOTPView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ResendOTPSerializer

    def post(self, request):
        try:
            serializer = ResendOTPSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
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
            expiration_time = otp.created + timedelta()

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


class VerificationView(APIView):
    serializer_class = VerifySerializer

    def post(self, request):
        try:
            serializer = VerifySerializer(data=request.data)
            if serializer.is_valid():
                user = request.user
                verification_code = serializer.validated_data['code']

                if user.profile.verification_code == verification_code:

                    user.profile.is_verified = True
                    user.profile.save()

                    return Response({'message': 'Account successfully verified'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            data = {
                "error_message": f"An error occurred during account verification: {str(e)}",
            }
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GoogleSocialAuthView(APIView):
    serializer_class = GoogleSocialAuthSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = (serializer.validated_data['auth_token'])
        return Response(data, status=status.HTTP_200_OK)

