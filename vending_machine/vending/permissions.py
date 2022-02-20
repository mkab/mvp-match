from rest_framework import permissions
from vending.choices import UserRole


class IsBuyer(permissions.BasePermission):
    message = "Action not allowed"

    def has_permission(self, request, view):
        return request.user.role == UserRole.BUYER


class IsSeller(permissions.BasePermission):
    message = "Action not allowed"

    def has_permission(self, request, view):
        return request.user.role == UserRole.SELLER


class ProductAlterPermission(permissions.BasePermission):
    message = "Action not allowed"

    def has_object_permission(self, request, view, obj):
        return request.user == obj.seller_id


class UserIsSelf(permissions.BasePermission):
    message = "Cannot perform action on a different User"

    def has_object_permission(self, request, view, obj):
        return request.user == obj
