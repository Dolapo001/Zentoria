from django.urls import path
from .views import (
    UserRegistrationView,
    LoginView,
    RefreshTokenView,
    Logout,
    ProfileView,
    ChangePasswordView,
    RequestEmailChangeCodeView,
    ResendEmailVerificationView,
    SendOTPView,
    ResendOTPSerializerView,
    ChangeEmailView,
    RequestNewPasswordCodeView
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token-refresh'),
    path('logout/', Logout.as_view(), name='user-logout'),
    path('profile/', ProfileView.as_view(), name='user-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('request-email-change-code/', RequestEmailChangeCodeView.as_view(), name='request-email-change-code'),
    path('resend-email-verification/', ResendEmailVerificationView.as_view(), name='resend-email-verification'),
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('resend-otp/', ResendOTPSerializerView.as_view(), name='resend-otp'),
    path('change-email/', ChangeEmailView.as_view(), name='change-email'),
    path('request-new-password-code/', RequestNewPasswordCodeView.as_view(), name='request-new-password-code'),
]