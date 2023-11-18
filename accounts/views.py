import string

from .models import User

from django.core.mail import send_mail
from django.utils.html import strip_tags
from pyotp import random
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import \
    RegisterSerializer, \
    ResendOTPSerializer, \
    ResendEmailVerificationSerializer,\
    ProfileSerializer, \
    ChangeEmailSerializer, \
    ChangePasswordSerializer, \
    RequestEmailChangeCodeSerializer, \
    RequestNewPasswordCodeSerializer, \
    UpdateProfileSerializer, \
    LoginSerializer, \
    SendOTPSerializer
from django.http import JsonResponse


def custom_response(data, message, status_code, status_text=None):
    # Convert status_code to integer
    status_code = int(status_code)

    response_data = {
        "status_code": status_code,
        "message": message,
        "data": data,
    }

    if status_text is not None:
        response_data["status"] = status_text

    return JsonResponse(response_data, status=status_code)



class UserRegistrationView(APIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        User.objects.create_user(**validated_data)
        return custom_response("User created successfully", status.HTTP_201_CREATED, "success")


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)

            if response.status_code == status.HTTP_200_OK:

                user = response.data.get('user', {})
                access_token = response.data.get('access_token', '')

                custom_data = {
                    'user_id': user.get('id', ''),
                    'username': user.get('username', ''),
                    'last_login': user.get('last_login', ''),

                }

                custom_response_data = {
                    'access_token': access_token,
                    'user': custom_data,
                }

                return custom_response(custom_response_data, "Login successful", status.HTTP_200_OK, "success")

            return response

        except TokenError as e:
            data = {
                'error_message': f"Token error: {str(e)}",
            }
            return custom_response(data, "Token error", status.HTTP_401_UNAUTHORIZED, "error")

        except Exception as e:
            data = {
                'error_message': f"An error occurred during login: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class RefreshTokenView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)

            if response.status_code == status.HTTP_200_OK:
                user = response.data['user']
                refresh = RefreshToken(response.data['refresh'])
                access_token = refresh.access_token
                response.data = {
                    'access_token': str(access_token),
                    'user': user,
                }

            return response

        except TokenError as e:
            data = {
                "error_message": f"An error occurred during token refresh: {str(e)}",
            }
            return custom_response(data, status.HTTP_401_UNAUTHORIZED, "error")


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

            return custom_response(serializer.errors, 'Invalid data provided', status.HTTP_400_BAD_REQUEST, 'bad request')
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

            return custom_response(serializer.errors, 'Invalid data provided', status.HTTP_400_BAD_REQUEST, 'bad request')
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
            return custom_response(serializer.errors, 'Invalid data provided', status.HTTP_400_BAD_REQUEST, 'bad request')
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
            return custom_response(serializer.errors, 'Invalid data provided', status.HTTP_400_BAD_REQUEST, 'bad request')
        except Exception as e:
            data = {
                "error_message": f"An error occurred while updating profile: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, 'error')