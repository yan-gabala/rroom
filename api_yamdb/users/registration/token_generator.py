from rest_framework_simplejwt.tokens import RefreshToken


def get_token_for_user(user):
    """Возвращает словарь вида {token: access_token}."""
    refresh = RefreshToken.for_user(user)

    return {'token': str(refresh.access_token)}
