from rest_framework.permissions import BasePermission

from disturbance.helpers import (
    is_internal,
)

class InternalCompliancePermission(BasePermission):
    """
    Compliance permission for internal users, essentially any member of 
    any of the existing internal system groups
    """

    def has_permission(self, request, view):
        return is_internal(request)