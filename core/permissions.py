from rest_framework.permissions import BasePermission


class IsAdminOrOwnerOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        """
        Defines if the user has permission to access the object.
        Used for the detail view.
        """
        return (
                request.user.is_authenticated and
                (request.user.is_staff or obj.owner == request.user)
        )
