from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

from ..models import User


def send_confirmation_code(user: User):
    """Посылает письмо с кодом подтверждения на эл. почту пользователя.
    Возвращает строку с кодом подтверждения.
    """
    confirmation_code = default_token_generator.make_token(user)
    email_message = (
        'Вы получили это письмо, потому что пытались зарегистрироваться \n'
        'или обновить токен на ресурсе YAMDB.\n'
        f'Ваше имя пользователя: {user.username}\n'
        'Используйте этот код подтверждения:\n'
        f'"{confirmation_code}"'
    )
    send_mail(
        'Регистрация',
        email_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
