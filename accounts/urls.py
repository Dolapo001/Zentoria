from django.urls import path
from .views import UserRegistrationView, LoginView, Logout, RefreshTokenView, ChangeEmailView, ProfileView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('token/refresh/', RefreshTokenView.as_view(), name="refresh_token"),
    path('change-email/', ChangeEmailView.as_view(), name="change_email"),
    path('profile/', ProfileView.as_view(), name="profile"),


]
