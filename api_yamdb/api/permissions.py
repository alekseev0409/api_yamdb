from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS, BasePermission

User = get_user_model()


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return (request.user in SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (
            request.user == obj.author
            or request.user.is_moderator
            or request.user.is_admin
        )


class IsAdminUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated and request.user.is_admin)


class IsAdminPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin
