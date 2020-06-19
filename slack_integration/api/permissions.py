from rest_framework.permissions import BasePermission


class IsDeveloper(BasePermission):
    """
    Checks if a user is a member of the group.
    """
    def has_permission(self, request, view):
        user = request.user
        return user.groups.filter(name='Developer').exists()
