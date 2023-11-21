from django.core.exceptions import ValidationError
import re
from django.core.validators import validate_email
from django.utils import timezone


def validate_email_format(value):
    try:
        validate_email(value)
    except ValidationError:
        raise ValidationError("Invalid email format")


def validate_code(value):
    if not re.match("^[0-9]{6}$", str(value)):
        raise ValidationError("Code must be a 6-digit number")


def validate_phone_number(value):
    if not value.startwith('+'):
        raise ValidationError("Phone number must start with as plus sign (+)")
    if not value[1:].isdigit():
        raise ValidationError("Phone number must only contain digits after the plus sign (+)")


def validate_image_size(value):
    max_size = 5 * 1024 * 1024
    if value.size > max_size:
        raise ValidationError("Image size should be less than 5MB")


def validate_date(value):
    if value is not None and value > timezone.now().date():
        raise ValidationError("Birthday must be in the past.")
