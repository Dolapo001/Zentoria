# urls.py
from django.urls import path
from .views import UserProfileView, CustomLoginView, CustomLogoutView, CustomRegisterView

urlpatterns = [
    path('profile/<int:pk>', UserProfileView.as_view(), name='user-profile'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', CustomRegisterView.as_view(), name='register'),
]
