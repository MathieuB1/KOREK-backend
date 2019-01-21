from rest_framework import permissions
from django.conf import settings

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_permission(self, request, view):
        if settings.PRIVACY_MODE[0].startswith('PRIVATE'):
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet
        return obj.owner == request.user



class IsAuthentificatedOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet
        return obj.owner == request.user

class RegisterPermission(permissions.BasePermission):
    """
    Custom permission to deny allow owners to POST method
    """
    def has_permission(self, request, view):
        if request.method == 'POST':
            if request.user.is_authenticated:
                return False
            else:
                return True

        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet
        return obj.username == request.user.username


class PasswordPermission(permissions.BasePermission):
    """
    Custom permission to deny allow owners to POST method
    """
    def has_permission(self, request, view):
        if request.method == 'POST':
            if request.user.is_authenticated:
                return False
            else:
                return True

        return False

    def has_object_permission(self, request, view, obj):
        return True


class GroupPermission(permissions.BasePermission):
    """
    Custom permission to deny allow owners to POST method
    """
    def has_permission(self, request, view):
        if request.method == 'POST' or request.method == 'DELETE' or  request.method == 'PATCH':
            return False

        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            if settings.PRIVACY_MODE[0].startswith('PUBLIC'):
                return False
            return True

        # Write permissions are only allowed to the owner of the snippet
        return obj.username == request.user.username


class GroupAcknowlegmentPermission(permissions.BasePermission):
    """
    Custom permission to deny allow owners to POST method
    """
    def has_permission(self, request, view):
        if settings.PRIVACY_MODE[0] == 'PUBLIC' or settings.PRIVACY_MODE[0] == 'PRIVATE':
            return False

        if request.method == 'POST' or request.method == 'DELETE' or  request.method == 'PATCH':
            return False

        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only PUT method allowed 
        return True