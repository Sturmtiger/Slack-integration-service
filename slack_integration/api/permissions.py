from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """
    Checks if a user is a member of the Admin group.
    """
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Admin').exists()


class IsDeveloper(BasePermission):
    """
    Checks if a user is a member of the Developer group.
    """
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Developer').exists()
