from uuid import uuid4
from django.contrib.auth.models import User

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from .validators import validate_date


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

AUTH_PROVIDERS = {'google': 'google',
                  'email': 'email'}

class User(AbstractUser):
    MALE = 'M'
    FEMALE = 'F'

    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    ]
    email = models.EmailField(unique=True)
    auth_provider = models.CharField(max_length=255, blank=False, null=False, default=AUTH_PROVIDERS.get('email'))
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    fullname = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')], blank=True)
    birthday = models.DateField(blank=True, null=True, validators=[validate_date])
    username = models.CharField(max_length=30, unique=True, default='')
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['gender', 'birthday']

    def __str__(self):
        return self.fullname


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=30, unique=True, default='')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True)
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)

    def __str__(self):
        return self.user.username


class OTP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    secret = models.CharField(max_length=6)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OTPSecret for {self.user.username}"
