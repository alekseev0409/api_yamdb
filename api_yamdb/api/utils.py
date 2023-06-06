from rest_framework_simplejwt.tokens import RefreshToken
import uuid

from django.conf import settings
from django.core.mail import send_mail


def create_token(user):
    refresh = RefreshToken.for_user(user)
    return {
        "token": str(refresh.access_token)
    }


def new_code():
    return str(uuid.uuid4())[0:16]


def send_message(username, code, email):
    send_mail(
        'Регистрация',
        f'Привет, {username}. Ваш код: {code}',
        settings.FROM_EMAIL,
        [email],
        fail_silently=False,
    )
