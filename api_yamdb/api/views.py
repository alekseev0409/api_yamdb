from rest_framework import permissions
from django.db.models import Avg
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from .serializers import (TokenSerializer,
                          UserSerializer,
                          SignUpSerializer,
                          CategorySerializer,
                          CommentSerializer,
                          GenreSerializer,
                          ReviewSerializer,
                          TitleCreateSerializer,
                          TitleReadSerializer,
                          UserCreateSerializer)
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .utils import new_code, send_message
from rest_framework import (viewsets, filters, status)
from .permissions import (IsModerator,
                          IsAdminUserOrReadOnly, IsAdminPermission)
from rest_framework.permissions import AllowAny
from rest_framework.pagination import LimitOffsetPagination
from reviews.models import Category, Genre, Review, Title
from .mixins import ModelMixinSet
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from django.contrib.auth.tokens import default_token_generator
from api.filters import TitleFilter

User = get_user_model()


class TokenView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data['username']
        user = get_object_or_404(User, username=username)
        confirmation_code = serializer.data['confirmation_code']
        if not default_token_generator.check_token(user, confirmation_code):
            raise ValidationError('Неверный код')
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminPermission,)
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'username'
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete']
    pagination_class = LimitOffsetPagination

    @action(detail=False, methods=['get', 'patch'], url_path='me',
            url_name='me', permission_classes=(permissions.IsAuthenticated,))
    def about_me(self, request):
        if request.method == 'PATCH':
            serializer = UserCreateSerializer(
                request.user, data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserCreateSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SignUpView(APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = SignUpSerializer

    def post(self, request, *args, **kwargs):
        user = None
        if 'username' in request.data:
            user = User.objects.filter(
                username=request.data["username"]
            ).first()
        if not user:
            serializer = SignUpSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data['email']
            name = serializer.validated_data['username']
            confirmation_code = new_code()
            send_message(name, confirmation_code, email)
            serializer.save(confirmation_code=confirmation_code)
            return Response(serializer.data)
        if user.email != request.data['email']:
            return Response(status=400)
        serializer = UserSerializer()
        return Response(serializer.data)


class CategoryViewSet(ModelMixinSet):
    """Получить список всех категорий без токена."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )
    lookup_field = 'slug'
    pagination_class = LimitOffsetPagination


class GenreViewSet(ModelMixinSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminUserOrReadOnly, )
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['name', ]
    lookup_field = 'slug'
    pagination_class = PageNumberPagination



class TitleViewSet(viewsets.ModelViewSet):
    """Получить список всех объектов без токена."""
    queryset = Title.objects.all().annotate(Avg("reviews__score")).order_by(
        "name"
    )
    serializer_class = TitleCreateSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleCreateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        user = self.request.user
        serializer.save(author=user, title=title)

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            return (AllowAny(),)
        return (IsModerator(),)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        review_id = int(self.kwargs.get('review_id'))
        review = get_object_or_404(Review.objects.prefetch_related('comments'), id=review_id)
        return review.comments.all()

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            return (AllowAny(),)
        return (IsModerator(),)

    def perform_create(self, serializer):
        review_id = int(self.kwargs.get('review_id'))
        review = get_object_or_404(Review, id=review_id)
        user = self.request.user
        serializer.save(author=user, review=review)
