import string
from django.db import IntegrityError
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.utils.html import strip_tags
from pyotp import random
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Profile
from .serializers import (
    RegisterSerializer,
    ResendOTPSerializer,
    ResendEmailVerificationSerializer,
    ProfileSerializer,
    ChangeEmailSerializer,
    ChangePasswordSerializer,
    RequestEmailChangeCodeSerializer,
    RequestNewPasswordCodeSerializer,
    UpdateProfileSerializer,
    LoginSerializer,
    SendOTPSerializer
)
from django.http import JsonResponse



def custom_response(data, message, status_code, status_text=None, tokens=None):
    # Convert status_code to integer
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

    return JsonResponse(response_data, status=status_code)


class UserRegistrationView(APIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        password = validated_data.pop('password1', None)

        try:
            user, created = User.objects.get_or_create(username=validated_data['username'],
                                                       defaults={'password': password})
            if created:
                return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

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
            return custom_response("Invalid credentials", status.HTTP_400_BAD_REQUEST)


class RefreshTokenView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        access_token = validated_data.get('access')  # Use get method to safely access the 'access' key

        return Response({
            "message": "Refreshed successfully",
            "token": access_token,
            "status": "success"
        }, status=status.HTTP_200_OK)

class Logout(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')

            if not refresh_token:
                return custom_response({}, 'Refresh token not provided', status.HTTP_400_BAD_REQUEST, 'error')
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()

                return custom_response({}, "Logout successful", status.HTTP_200_OK, "success")
            except Exception as e:
                return custom_response({}, f"Invalid refresh token: {str(e)}", status.HTTP_401_UNAUTHORIZED, "error")

        except Exception as e:
            data = {
                "error_message": f"An error occurred during logout: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class ChangeEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = ChangeEmailSerializer(data=request.data)
            if serializer.is_valid():
                # Your logic for changing email
                return custom_response(None, 'Email changed successfully', status.HTTP_200_OK, 'success')

            return custom_response(serializer.errors, 'Invalid data provided', status.HTTP_400_BAD_REQUEST,
                                   'bad request')
        except Exception as e:
            data = {
                "error_message": f"An error occurred while changing email: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, 'error')

# Your existing ChangePasswordView...
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = ChangePasswordSerializer(data=request.data)
            if serializer.is_valid():
                # Your logic for changing password
                return custom_response(None, 'Password changed successfully', status.HTTP_200_OK, 'success')

            return custom_response(serializer.errors, 'Invalid data provided', status.HTTP_400_BAD_REQUEST,
                                   'bad request')
        except Exception as e:
            data = {
                "error_message": f"An error occurred while changing password: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, 'error')

# Your existing ProfileView...
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            serializer = ProfileSerializer(user)
            return custom_response(serializer.data, 'Profile retrieved successfully', status.HTTP_200_OK, 'success')
        except Exception as e:
            data = {
                "error_message": f"An error occurred while retrieving profile: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, 'error')

    def put(self, request):
        user = request.user
        serializer = UpdateProfileSerializer(user, data=request.data)
        try:
            if serializer.is_valid():
                serializer.save()
                return custom_response(serializer.data, 'Profile updated successfully', status.HTTP_200_OK, 'success')
            return custom_response(serializer.errors, 'Invalid data provided', status.HTTP_400_BAD_REQUEST,
                                   'bad request')
        except Exception as e:
            data = {
                "error_message": f"An error occurred while updating profile: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, 'error')

# Your existing RequestEmailChangeCodeView...
class RequestEmailChangeCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = RequestEmailChangeCodeSerializer(data=request.data)
            if serializer.is_valid():
                user = request.user
                new_email = serializer.validated_data['email']

                # Generate a random 6-digit code
                email_change_code = ''.join(random.choices(string.digits, k=6))

                # Save the code to the user model
                user.email_change_code = email_change_code
                user.save()

                # Send the code to the user's email
                subject = 'Email Change Verification Code'
                message = f'Your verification code is: {email_change_code}'
                from_email = 'your@example.com'  # Set your sending email address
                recipient_list = [new_email]

                send_mail(subject, message, from_email, recipient_list)

                return Response({'message': 'Email change code sent successfully'}, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            data = {
                "error_message": f"An error occurred while requesting email change code: {str(e)}",
            }
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Your existing ResendEmailVerificationView...
class ResendEmailVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = ResendEmailVerificationSerializer(data=request.data)
            if serializer.is_valid():
                user = request.user

                # Generate a new verification token
                new_verification_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

                # Update the user's verification token in the database
                user.profile.verification_token = new_verification_token
                user.profile.save()

                # Send the verification email to the user
                subject = 'Email Verification'
                context = {'user': user, 'verification_token': new_verification_token}
                from django.template.loader import render_to_string
                message = render_to_string('email_verification_template.html', context)
                plain_message = strip_tags(message)
                from_email = 'your@example.com'  # Set your sending email address
                recipient_list = [user.email]

                send_mail(subject, plain_message, from_email, recipient_list, html_message=message)

                return Response({'message': 'Email verification resent successfully'}, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            data = {
                "error_message": f"An error occurred while resending email verification: {str(e)}",
            }
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Your existing SendOTPSerializerView...
class SendOTPSerializerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = SendOTPSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()  # This will trigger the logic in SendOTPSerializer

                return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            data = {
                "error_message": f"An error occurred while sending OTP: {str(e)}",
            }
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Your existing ResendOTPSerializerView...
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

# Your existing RequestNewPasswordCodeView...
class RequestNewPasswordCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = RequestNewPasswordCodeSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data['email']

                # Call your existing logic for sending a new password code
                send_otp_serializer = SendOTPSerializer(data={'email': email})
                if send_otp_serializer.is_valid():
                    send_otp_serializer.save()  # This will trigger the logic in SendOTPSerializer

                    return Response({'message': 'New password code sent successfully'}, status=status.HTTP_200_OK)
                else:
                    return Response(send_otp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            data = {
                "error_message": f"An error occurred while requesting new password code: {str(e)}",
            }
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            serializer = ProfileSerializer(user)
            return custom_response(serializer.data, 'Profile retrieved successfully', status.HTTP_200_OK, 'success')
        except Exception as e:
            data = {
                "error_message": f"An error occurred while retrieving profile: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, 'error')

# Your new UpdateProfileView...
class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = UpdateProfileSerializer(user, data=request.data)
        try:
            if serializer.is_valid():
                serializer.save()
                return custom_response(serializer.data, 'Profile updated successfully', status.HTTP_200_OK, 'success')
            return custom_response(serializer.errors, 'Invalid data provided', status.HTTP_400_BAD_REQUEST,
                                   'bad request')
        except Exception as e:
            data = {
                "error_message": f"An error occurred while updating profile: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, 'error')