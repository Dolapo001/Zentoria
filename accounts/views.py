from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer


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
            email = request.data.get('email')
            password = request.data.get('password')
            user = User.objects.filter(email=email).first()

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
                "error_message": f"An error occurred while retrieving user profile: {str(e)}",
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


class CustomRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            data = request.data
            serializer = UserSerializer(data=data)

            if serializer.is_valid():
                user = serializer.save()
                token, created = Token.objects.get_or_create(user=user)
                response_data = {
                    'token': token.key,
                    'user_id': user.id
                }
                return custom_response(response_data, 'Registration successful', status.HTTP_201_CREATED, 'Created')
            return custom_response(serializer.errors, 'Invalid data provided', status.HTTP_400_BAD_REQUEST,
                                   'Bad Request')
        except Exception as e:
            data = {
                "error_message": f"An error occurred during registration: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, 'error')