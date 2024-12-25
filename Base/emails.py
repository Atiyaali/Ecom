
from django.conf import settings
from django.core.mail import send_mail

def send_email_account_activation(email, email_token):
    subject = "Account Activation"
    message_from = settings.EMAIL_HOST_USER
    message = f"Click on the Link to activate account http://127.0.0.1:8000/accounts/activate/{email_token}"
    send_mail(subject, message, message_from, [email])