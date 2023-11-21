import pyotp
from django.http import Http404
from django.utils import timezone
from rest_framework.generics import get_object_or_404
from accounts.models import OTP


def get_or_generate_otp_secret(user):
    try:
        otp_secret = get_object_or_404(OTP, user=user)
        otp_secret.created = timezone.now()
        otp_secret.save()
    except Http404:
        otp_secret = OTP.objects.create(user=user, secret=pyotp.random_base32())

    return otp_secret


def generate_otp(secret, interval=600):
    totp = pyotp.TOTP(secret, interval=interval)
    return totp.now()
