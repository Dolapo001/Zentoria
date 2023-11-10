# urls.py
from django.urls import path
from .views import UserProfileView, CustomLoginView, CustomLogoutView, \
    UserRegistrationView, GoogleAuthView

urlpatterns = [
    path('profile/<int:pk>', UserProfileView.as_view(), name='user-profile'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('auth/google/', GoogleAuthView.as_view(), name='google-auth'),
]
