from rest_framework import serializers
from .models import Profile, User
from .validators import (
    validate_code, validate_email_format, validate_phone_number, validate_image_size
)
import pyotp
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist


class BaseSerializer(serializers.Serializer):
    def validate_email_format(self, value):
        validate_email_format(value)


class ChangeEmailSerializer(BaseSerializer):
    code = serializers.IntegerField(validators=[validate_code])
    email = serializers.EmailField()

    def validate(self, attrs):
        code = attrs.get('code')
        email = attrs.get('email')

        if not code:
            raise serializers.ValidationError({"message": "Code is required", "status": "failed"})
        validate_email_format(email)

        return attrs


class LoginSerializer(BaseSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=150, min_length=6, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        self.validate_email_format(email)

        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class ProfileSerializer(serializers.Serializer):
    email = serializers.EmailField(source="user.email")
    username = serializers.CharField(source="user.username")
    full_name = serializers.CharField(source="user.fullname")
    gender = serializers.ChoiceField(choices=User.GENDER_CHOICES, source="user.gender")
    birthday = serializers.DateField(source="user.birthday")
    phone_number = serializers.CharField
    profile_picture = serializers.ImageField(source="user.profile_picture")
    address = serializers.CharField

    def validate_phone_number(self, value):
        validate_phone_number(value)
        return value

    def validate_profile_picture(self, attrs):
        picture = attrs.get('profile_picture')
        validate_image_size(picture)
        return attrs


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    fullname = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=30, write_only=True)
    password = serializers.CharField(max_length=50, min_length=6, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        fullname = attrs.get('fullname')
        username = attrs.get('username')
        password = attrs.get('password')

        existing_email = User.objects.filter(email=email)
        if existing_email.exists():
            raise serializers.ValidationError({"message": "Email already registered"})

        existing_username = Profile.objects.filter(username=username)
        if existing_username.exists():
            raise serializers.ValidationError({"message": "Username already exists"})

        validate_email_format(email)

        if not fullname:
            raise serializers.ValidationError({"message": "Full Name required"})

        return attrs


class RequestEmailChangeCodeSerializer(BaseSerializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get('email')
        validate_email_format(email)
        return attrs


class ResendEmailVerificationSerializer(BaseSerializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get('email')
        validate_email_format(email)
        return attrs


class RequestNewPasswordCodeSerializer(BaseSerializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get('email')
        validate_email_format(email)
        return attrs


class UpdateProfileSerializer(serializers.Serializer):
    email = serializers.EmailField(read_only=True)
    username = serializers.CharField(max_length=255)
    full_name = serializers.CharField(max_length=255)
    gender = serializers.ChoiceField(choices="user.gender")
    birthday = serializers.DateField()
    phone_number = serializers.CharField(max_length=20)
    profile_picture = serializers.ImageField(validators=[validate_image_size])

    def validate_phone_number(self, value):
        validate_phone_number(value)
        return value

    def validate_profile_picture(self, attrs):
        picture = attrs.get('profile_picture')
        validate_image_size(picture)
        return attrs

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
            instance.save()
        return instance


class SendOTPSerializer(BaseSerializer):
    email = serializers.EmailField(required=True, validators=[validate_email_format])

    def create(self, validated_data):
        email = validated_data['email']

        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            raise serializers.ValidationError({'email': 'User not found'})

        user.totpdevice_set.all().delete()

        totp = pyotp.TOTP(pyotp.random_base32())
        otp = totp.now()

        user.totpdevice_set.create(secret_key=totp.secret)

        return {'message': 'OTP sent successfully'}


class ResendOTPSerializer(BaseSerializer):
    email = serializers.EmailField(validators=[validate_email_format])

    def send_otp(self, user, otp):
        subject = 'OTP for Email Verification'
        message = f'Your OTP for email verification is: {otp}'
        from_email = 'adedolapovictoria927@gmail.com'
        recipient_list = [user.email]

        send_mail(subject, message, from_email, recipient_list)

        return {'message': 'OTP resent successfully'}


class VerificationSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)
    otp = serializers.CharField(max_length=6, required=True)
