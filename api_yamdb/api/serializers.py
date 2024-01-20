from django.db.models import Avg
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Categories, Comment, Genres, Review, Title
from users.constants import CONF_CODE_MAX_LEN, EMAIL_MAX_LEN, USERNAME_MAX_LEN
from users.models import User
from users.validators import username_not_me_validator, username_validator


class CategoriesSerializer(serializers.ModelSerializer):
    """Сериализатор для категории."""
    class Meta:
        model = Categories
        fields = (
            'name',
            'slug',
        )


class GenresSerializer(serializers.ModelSerializer):
    """Сериализатор для жанра."""
    class Meta:
        model = Genres
        fields = (
            'name',
            'slug',
        )


class CreateUpdateTitleSerializer(serializers.ModelSerializer):
    """Сериализатор для произведения."""
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Categories.objects.all(),
        required=True,
    )

    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genres.objects.all(),
        many=True,
        required=False,
    )

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category',
        )


class ShowTitlesSerializer(serializers.ModelSerializer):
    """Сериализатор показа рейтинга для произведений."""
    category = CategoriesSerializer(read_only=True)
    genre = GenresSerializer(many=True, required=False)
    rating = serializers.SerializerMethodField()

    class Meta:
        "Класс дополнен полем 'rating'."
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
        )

    def get_rating(self, instance):
        "Метод расчета рейтинга произведения."
        avg = instance.reviews.aggregate(Avg('score'))
        rating = avg['score__avg']
        if rating:
            rating = int(rating)
        else:
            rating = None
        return rating


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ревью."""
    author = SlugRelatedField(slug_field='username', read_only=True,
                              default=serializers.CurrentUserDefault())

    class Meta:
        fields = ('id', 'author', 'text', 'pub_date', 'score')
        model = Review

    def validate(self, data):
        if self.context['request'].method == 'POST':
            reviewer = self.context['request'].user
            title_id = self.context['view'].kwargs['title_id']
            if Review.objects.filter(author=reviewer,
                                     title_id=title_id).exists():
                raise serializers.ValidationError('Повторное ревью запрещено')
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели комментария."""
    author = SlugRelatedField(slug_field='username', read_only=True,
                              default=serializers.CurrentUserDefault())

    class Meta:
        fields = ('id', 'author', 'text', 'pub_date')
        model = Comment


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели User."""
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


class UserProfileSerializer(UserSerializer):
    """Сериализатор модели User для профиля пользователя."""
    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class SignUpSerializer(serializers.Serializer):
    """Сериализатор для регистрации."""
    username = serializers.CharField(
        max_length=USERNAME_MAX_LEN,
        required=True,
        validators=[username_not_me_validator, username_validator],
    )
    email = serializers.EmailField(
        max_length=EMAIL_MAX_LEN,
        required=True,
    )

    def validate(self, data):
        """Запрещает пользователям присваивать себе имя me
        и использовать повторные username и email."""

        if not User.objects.filter(
            username=data.get('username'), email=data.get('email')
        ).exists():
            if User.objects.filter(username=data.get('username')):
                raise serializers.ValidationError(
                    'Пользователь с таким username уже существует'
                )

            if User.objects.filter(email=data.get('email')):
                raise serializers.ValidationError(
                    'Пользователь с таким email уже существует'
                )

        return data


class GetAuthTokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""
    username = serializers.CharField(
        max_length=USERNAME_MAX_LEN,
        required=True,
        validators=[username_not_me_validator, username_validator],
    )
    confirmation_code = serializers.CharField(
        required=True, max_length=CONF_CODE_MAX_LEN
    )
