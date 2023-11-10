from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from .serializers import UserSerializer, UserRegistrationSerializer
from django.db.models import Q
from social_django.utils import psa
from social_core.exceptions import AuthFailed


def custom_response(data, message, status_code, status_text):
    response_data = {
        "status_code": status_code,
        "message": message,
        "data": data,
        "status": status_text,
    }
    return Response(response_data, status=status_code)


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            user = request.user
            serializer = UserSerializer(user)
            return custom_response(serializer.data, 'User profile retrieved successfully', status.HTTP_200_OK, 'Success')
        except Exception as e:
            data = {
                "error_message": f"An error occurred while retrieving user profile: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, 'error')

    def put(self, request, pk):
        user = request.user
        serializer = UserSerializer(user, data=request.data)
        try:
            if serializer.is_valid():
                serializer.save()
                return custom_response(serializer.data, 'User profile updated successfully', status.HTTP_200_OK,
                                       'success')
            return custom_response(serializer.errors, 'Invalid data provided', status.HTTP_400_BAD_REQUEST,
                                   'bad request')
        except Exception as e:
            data = {
                "error_message": f"An error occurred while updating the user profile: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, 'error')


class CustomLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            identifier = request.data.get('identifier')
            password = request.data.get('password')

            user = User.objects.filter(Q(email=identifier) | Q(username=identifier)).first()

            if user is not None and user.check_password(password):
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                response_data = {
                    'token': token.key,
                    'user_id': user.id
                }
                return custom_response(response_data, 'Login Success', status.HTTP_200_OK, 'success')

            return custom_response(None, 'Login failed', status.HTTP_401_UNAUTHORIZED, 'Unauthorized')
        except Exception as e:
            data = {
                "error_message": f"An error occurred during login: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, 'error')


class CustomLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            logout(request)
            return custom_response(None, 'Logout successful', status.HTTP_200_OK, 'Success')
        except Exception as e:
            data = {
                "error_message": f"An error occurred while logging out: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, 'error')


class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                token, created = Token.objects.get_or_create(user=user)
                user_serializer = UserSerializer(user)
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


class GoogleAuthView(APIView):
    permission_classes = [permissions.AllowAny]

    @psa('social:complete')
    def post(self, request, backend):
        try:
            user = request.backend.do_auth(request.data['access_token'])
            if user:
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                response_data = {
                    'token': token.key,
                    'user_id': user.id
                }
                return custom_response(response_data, 'Login Success', status.HTTP_200_OK, 'success')
            return custom_response(None, 'Login failed', status.HTTP_401_UNAUTHORIZED, 'Unauthorized')
        except AuthFailed as e:
            data = {
                "error_message": f"An error occurred during Google authentication: {str(e)}",
            }
            return custom_response(data, "Authentication failed", status.HTTP_401_UNAUTHORIZED, 'Unauthorized')
        except Exception as e:
            data = {
                "error_message": f"An error occurred during Google authentication: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, 'error')
