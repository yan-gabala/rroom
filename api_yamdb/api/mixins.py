from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.viewsets import GenericViewSet


class GetListCreateDeleteMixin(
    GenericViewSet, CreateModelMixin, ListModelMixin, DestroyModelMixin
):
    """Кастомный класс для жанров и категорий."""

    pass
