from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError

username_validator = UnicodeUsernameValidator()


def username_not_me_validator(value):
    """Запрещает использовать 'me' в качестве username."""
    if value.lower() == 'me':
        raise ValidationError(
            'Вы не можете использовать "me" в качестве username.'
        )
    return value
