from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            # Allow safe methods (GET, HEAD, OPTIONS) for all users, even if not authenticated.
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Allow the author of the object to edit it.
        return obj.author == request.user
