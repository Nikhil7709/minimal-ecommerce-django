from rest_framework import permissions

class IsAdminOrProductCreator(permissions.BasePermission):
    """
    Custom permission to only allow admins or the creator of a product to edit or delete it.
    """
    def has_object_permission(self, request, view, obj):
        # Allow access if the user is an admin or the creator of the product
        return request.user.is_admin or obj.created_by == request.user.email

