from rest_framework import serializers
from django.contrib.auth import get_user_model
from reviews.models import Category, Comment, Genre, Review, Title
from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework.serializers import IntegerField
import re
User = get_user_model()


class TokenSerializer(serializers.ModelSerializer):
    """Сериализация токена."""
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class UserSerializer(serializers.ModelSerializer):
    """Сериализация пользователя."""
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания нового пользователя."""
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=150,
        required=True
    )

    email = serializers.EmailField(
        max_length=254,
        required=True,
    )

    class Meta:
        model = User
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                  'bio',
                  'role')

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Имя пользователя "me" запрещено.'
            )
        if not re.match(r'^[\w.@+-]+$', value):
            raise serializers.ValidationError(
                'Некорректное имя пользователя.'
            )
        return value

    def validate_email(self, value):
        if not re.match(r'^[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', value):
            invalid_chars = re.findall(r'[^\w.%+-@]+', value)
            raise serializers.ValidationError(
                f'Некорректный email-адрес. Символы'
                f'{", ".join(invalid_chars)} не допускаются.'
            )
        return value


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя."""
    class Meta:
        model = User
        fields = ['email', 'username']

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Имя пользователя "me" запрещено.'
            )
        return value


class CategorySerializer(serializers.ModelSerializer):
    """Сериализтор для категорий."""
    class Meta:
        fields = ('name', 'slug')
        model = Category
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""
    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitleCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для произведений."""
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        model = Title
        fields = '__all__'


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения информации о произведение."""
    category = CategorySerializer(
        read_only=True
    )
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    rating = serializers.IntegerField(
        source='reviews__score__avg',
        read_only=True
    )

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
    )

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    score = IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    def validate(self, data):
        request = self.context.get('request')
        score = data['score']
        if request.method == 'POST':
            review = Review.objects.filter(
                title=self.context['view'].kwargs.get('title_id'),
                author=self.context['request'].user
            )
            if review.exists():
                raise serializers.ValidationError(
                    'Отзыв уже существует'
                )
            if 10 < score < 0:
                raise serializers.ValidationError('Оценка меньше 0 '
                                                  'или больше 10')
        return data

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев."""
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date', 'review')
