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


def custom_response(data, message, status_code, status_text=None):
    response_data = {
        "status_code": status_code,
        "message": message,
        "data": data,
    }

    if status_text is not None:
        response_data["status"] = status_text

    return Response(response_data, status=status_code)


class UserRegistrationView(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token

                user_serializer = ProfileSerializer(user)
                data = {
                    'access_token': str(access_token),
                    'user': user_serializer.data,
                }
                return custom_response(data, "User created successfully", status.HTTP_201_CREATED, "success")

            return custom_response(serializer.errors, "Bad request", status
                                   .HTTP_400_BAD_REQUEST, "error")
        except Exception as e:
            data = {
                "error_message": f"An error occurred during registration: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


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



