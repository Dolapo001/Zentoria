from django.urls import path
from .views import UserRegistrationView, LoginView, RefreshTokenView, Logout

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh-token/', RefreshTokenView.as_view(), name='refresh-token'),
    path('logout/', Logout.as_view(), name='logout'),
]
