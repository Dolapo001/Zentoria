from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import login
from rest_framework.authtoken.models import Token
from .serializers import (
    ChangeEmailSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    ProfileSerializer,
    RegisterSerializer,
    RequestEmailChangeCodeSerializer,
    ResendEmailVerificationSerializer,
    RequestNewPasswordCodeSerializer,
    UpdateProfileSerializer,
    SendOTPSerializer,
    ResendOTPSerializer,
)

def custom_response(data, message, status_code, status_text):
    response_data = {
        "status_code": status_code,
        "message": message,
        "data": data,
        "status": status_text,
    }
    return Response(response_data, status=status_code)

class ChangeEmailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            serializer = ChangeEmailSerializer(data=request.data)
            if serializer.is_valid():
                # Your logic for changing email
                return custom_response(None, 'Email changed successfully', status.HTTP_200_OK, 'success')

            return custom_response(serializer.errors, 'Invalid data provided', status.HTTP_400_BAD_REQUEST, 'bad request')
        except Exception as e:
            data = {
                "error_message": f"An error occurred while changing email: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, 'error')

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                # Your logic for login
                return custom_response(None, 'Login success', status.HTTP_200_OK, 'success')

            return custom_response(None, 'Login failed', status.HTTP_401_UNAUTHORIZED, 'Unauthorized')
        except Exception as e:
            data = {
                "error_message": f"An error occurred during login: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, 'error')

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            serializer = ChangePasswordSerializer(data=request.data)
            if serializer.is_valid():
                # Your logic for changing password
                return custom_response(None, 'Password changed successfully', status.HTTP_200_OK, 'success')

            return custom_response(serializer.errors, 'Invalid data provided', status.HTTP_400_BAD_REQUEST, 'bad request')
        except Exception as e:
            data = {
                "error_message": f"An error occurred while changing password: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, 'error')

class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

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
            return custom_response(serializer.errors, 'Invalid data provided', status.HTTP_400_BAD_REQUEST, 'bad request')
        except Exception as e:
            data = {
                "error_message": f"An error occurred while updating profile: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, 'error')

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                # Your logic for registration
                return custom_response(None, 'Registration success', status.HTTP_201_CREATED, 'success')

            return custom_response(serializer.errors, 'Invalid data provided', status.HTTP_400_BAD_REQUEST, 'bad request')
        except Exception as e:
            data = {
                "error_message": f"An error occurred during registration: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, 'error')

class RequestEmailChangeCodeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            serializer = RequestEmailChangeCodeSerializer(data=request.data)
            if serializer.is_valid():
                # Your logic for requesting email change code
                return custom_response(None, 'Email change code sent successfully', status.HTTP_200_OK, 'success')

            return custom_response(serializer.errors, 'Invalid data provided', status.HTTP_400_BAD_REQUEST, 'bad request')
        except Exception as e:
            data = {
                "error_message": f"An error occurred while requesting email change code: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, 'error')

class ResendEmailVerificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            serializer = ResendEmailVerificationSerializer(data=request.data)
            if serializer.is_valid():
                # Your logic for resending email verification
                return custom_response(None, 'Email verification resent successfully', status.HTTP_200_OK, 'success')

            return custom_response(serializer.errors, 'Invalid data provided', status.HTTP_400_BAD_REQUEST, 'bad request')
        except Exception as e:
            data = {
                "error_message": f"An error occurred while resending email verification: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, 'error')

class RequestNewPasswordCodeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            serializer = RequestNewPasswordCodeSerializer(data=request.data)
            if serializer.is_valid():
                # Your logic for requesting new password code
                return custom_response(None, 'New password code sent successfully', status.HTTP_200_OK, 'success')

            return custom_response(serializer.errors, 'Invalid data provided', status.HTTP_400_BAD_REQUEST, 'bad request')
        except Exception as e:
            data = {
                "error_message": f"An error occurred while requesting new password code: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, 'error')

class SendOTPSerializerView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            serializer = SendOTPSerializer(data=request.data)
            if serializer.is_valid():
                # Your logic for sending OTP
                return custom_response(None, 'OTP sent successfully', status.HTTP_200_OK, 'success')

            return custom_response(serializer.errors, 'Invalid data provided', status.HTTP_400_BAD_REQUEST, 'bad request')
        except Exception as e:
            data = {
                "error_message": f"An error occurred while sending OTP: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, 'error')

class ResendOTPSerializerView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            serializer = ResendOTPSerializer(data=request.data)
            if serializer.is_valid():
                # Your logic for resending OTP
                return custom_response(None, 'OTP resent successfully', status.HTTP_200_OK, 'success')

            return custom_response(serializer.errors, 'Invalid data provided', status.HTTP_400_BAD_REQUEST, 'bad request')
        except Exception as e:
            data = {
                "error_message": f"An error occurred while resending OTP: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, 'error')

class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                token, created = Token.objects.get_or_create(user=user)
                user_serializer = ProfileSerializer(user)
                response_data = {
                    'token': token.key,
                    'user': user_serializer.data,
                }
                return Response(response_data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            data = {
                "error_message": f"An error occurred during registration: {str(e)}",
            }
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Add other views for remaining serializers in a similar manner
