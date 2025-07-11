from django.template.loader import render_to_string
from django.core.mail import send_mail, BadHeaderError
from django.utils.html import strip_tags

User = get_user_model()
def send_verification_code_email(user: User, verification_code: str) -> None:
    subject = 'Account Verification'
    html_message = render_to_string('email_verification.html', {'user': user, 'verification_code': verification_code})
    plain_message = strip_tags(html_message)
    from_email = 'zentoria@admin.com'
    recipient_list = [user.email]
    try:
        send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)
    except BadHeaderError as e:
        print(f"Error occurred while sending verification email: {e}")


def send_otp_email(user, otp, template='email_change_verification.html'):
    subject = 'OTP Verification'
    message_html = render_to_string(template, {'user': user, 'otp': otp})
    message_plain = strip_tags(message_html)
    from_email = 'zentoria@admin.com'
    recipient_list = [user.email]
    try:
        send_mail(subject, message_plain, from_email, recipient_list, html_message=message_html)
    except BadHeaderError as e:
        print(f"Error occurred while sending OTP email: {e}")
