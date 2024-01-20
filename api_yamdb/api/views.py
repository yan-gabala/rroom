from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as myfilters
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from reviews.models import Categories, Comment, Genres, Review, Title
from users.models import User
from users.registration.confirmation import send_confirmation_code
from users.registration.token_generator import get_token_for_user
from .filters import TitleFilter
from .mixins import GetListCreateDeleteMixin
from .permissions import IsAdminOrReadOnly, IsAdmin, IsAuthorOrReadOnly
from .serializers import (CategoriesSerializer, CommentSerializer,
                          CreateUpdateTitleSerializer, ShowTitlesSerializer,
                          GenresSerializer, GetAuthTokenSerializer,
                          ReviewSerializer, SignUpSerializer,
                          UserProfileSerializer, UserSerializer)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Получить список всех отзывов.
    Добавление нового отзыва.
    Получение отзыва по id.
    Обновление отзыва по id.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """
    Получить список всех комментариев.
    Добавление нового комментария к отзыву.
    Получить комментарий по id.
    Обновление комментария по id.
    Удаление комментария.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def get_reviews(self):
        return get_object_or_404(Review, pk=self.kwargs.get('reviews_id'))

    def get_queryset(self):
        return self.get_reviews().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, reviews=self.get_reviews())


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведения(ий)."""
    queryset = Title.objects.all()
    serializer_class = CreateUpdateTitleSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (myfilters.DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        """
        Выбор нужного сериализатора:
        - создать произведение, обновить;
        - показать рейтинг произведения.
        """
        if self.action in ['list', 'retrieve']:
            return ShowTitlesSerializer
        return CreateUpdateTitleSerializer


class CategoriesViewSet(GetListCreateDeleteMixin):
    """Вьюсет для категории."""
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenresViewSet(GetListCreateDeleteMixin):
    """Вьюсет для жанра."""
    queryset = Genres.objects.all()
    serializer_class = GenresSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class UserViewSet(ModelViewSet):
    """Вьюсет модели User."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    search_fields = ('username',)
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'delete', 'patch']

    @action(
        methods=['patch', 'get'],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        serializer = UserProfileSerializer(
            request.user, partial=True, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        if request.method == "PATCH":
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetAuthTokenApiView(APIView):
    """CBV для получения и обновления токена."""
    def post(self, request):
        serializer = GetAuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if not default_token_generator.check_token(user, confirmation_code):
            return Response(
                {'confirmation_code': ['Неверный код подтверждения']},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(get_token_for_user(user), status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def sign_up(request):
    """Добавление нового пользователя"""
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data['email']
    username = serializer.data['username']
    user, _ = User.objects.get_or_create(email=email, username=username)
    send_confirmation_code(user)
    return Response(serializer.data, status=status.HTTP_200_OK)
