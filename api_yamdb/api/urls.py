from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import TokenView, UserViewSet, SignUpView

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/token/', TokenView.as_view(), name='token'),
    path('v1/auth/signup/', SignUpView.as_view(), name='signup'),
]
