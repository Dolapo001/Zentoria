from django.template.loader import render_to_string
from .otp_utils import get_or_generate_otp_secret, generate_otp
from django.core.mail import send_mail


def send_email(subject, recipient_list, message, from_email=None, html_message=None):

    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False,
        html_message=html_message,
    )


def send_otp_email(user, email=None, template=None):

    otp_secret = get_or_generate_otp_secret(user)
    otp = generate_otp(otp_secret.secret)

    subject = 'One-Time Password (OTP) Verification'
    recipient = [email or user.email]
    context = {'fullname': user.fullname, 'otp': otp}
    message = render_to_string(template, context)

    send_email(subject, recipient, message=message, template=template, context=context)
