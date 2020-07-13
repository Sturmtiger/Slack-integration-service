from rest_framework import permissions

from slack_integration.api.permissions import IsAdmin, IsDeveloper


class AdminDeveloperPermissionsMixin:
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            permissions_classes = (IsAdmin | IsDeveloper,)
        else:
            permissions_classes = (IsAdmin,)
        return (permission() for permission in permissions_classes)
