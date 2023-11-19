from django.urls import path
from .views import UserRegistrationView, LoginView, Logout, RefreshTokenView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('token/refresh/', RefreshTokenView.as_view(), name="refresh_token"),
]
