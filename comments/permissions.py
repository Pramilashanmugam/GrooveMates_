# permissions.py
from rest_framework import permissions

class IsCommentOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a comment to delete or update it.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the request is a DELETE or PUT/PATCH request
        if request.method in permissions.SAFE_METHODS:
            return True  # Allow GET requests for everyone
        return obj.owner == request.user  # Only allow the owner to delete or update
