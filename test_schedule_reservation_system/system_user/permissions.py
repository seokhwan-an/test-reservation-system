from rest_framework.permissions import BasePermission


class IsCorporateUser(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and not request.user.is_staff
