from rest_framework.permissions import BasePermission

from disturbance.helpers import (
    is_internal,
    is_org_request_assessor,
)

class InternalOrganisationPermission(BasePermission):
    """
    Organisation permission for internal users, essentially any member of 
    any of the existing internal system groups

    Intended to be non-specific
    """

    def has_permission(self, request, view):
        return is_internal(request)

class OrganisationRequestAssessorPermission(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_superuser or is_org_request_assessor(request) 