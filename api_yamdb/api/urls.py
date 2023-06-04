from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (TokenView, UserViewSet, SignUpView,
                    CategoryViewSet, GenreViewSet, TitleViewSet,
                    ReviewViewSet, CommentViewSet)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'genres', GenreViewSet)
router.register(r'titles', TitleViewSet)
router.register(r'titles/(?P<title_id>\d+)/reviews',
                ReviewViewSet, basename='reviews')
router.register(r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)'
                r'/comments', CommentViewSet, basename='comments')
router.register('users', UserViewSet, basename='users')

token_patterns = [
    path('token/', TokenView.as_view(), name='token'),
    path('signup/', SignUpView.as_view(), name='signup'),
]

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/', include(token_patterns)),
]
