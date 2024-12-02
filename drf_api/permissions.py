from rest_framework import permissions

"""
Custom permission classes for API access control.

Classes:
    IsOwnerOrReadOnly: Grants read-only access for any user, but restricts
                       write access to the owner of the object.
    IsAdminOrCreateOnly: Allows any authenticated user to create objects,
                         but restricts other actions to admin users only.
"""


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsAdminOrCreateOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_authenticated
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff
