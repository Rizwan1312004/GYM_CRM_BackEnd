from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow administrators to edit or delete it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')
