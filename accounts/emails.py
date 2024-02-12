from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.html import strip_tags


def send_verification_code_email(user, verification_code):
    subject = 'Account Verification'

    html_message = render_to_string('email_verification.html',
                                    {'user': user, 'verification_code': verification_code})

    plain_message = strip_tags(html_message)

    from_email = 'zentoria@admin.com'
    recipient_list = [user.email]

    send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)


def send_otp_email(user, email, otp, template='email_change_verification.html'):
    subject = 'OTP Verification'
    context = {'user': user, 'otp': otp}
    message_html = render_to_string(template, context)
    message_plain = strip_tags(message_html)
    from_email = 'zentoria@admin.com'
    recipient_list = [email]
    send_mail(subject, message_plain, from_email, recipient_list, html_message=message_html)
