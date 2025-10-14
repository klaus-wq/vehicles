from rest_framework import permissions

from authentication.models import Manager
from vehicle.models import Enterprise
from django.contrib import admin

class ManagerPermissionAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return request.user.is_staff and (request.user.is_superuser or hasattr(request.user, 'manager'))

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

class IsManagerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if not request.user.is_authenticated:
            return False

        try:
            manager = request.user.manager
            if hasattr(obj, 'enterprise'):
                return obj.enterprise in manager.enterprises.all()
            elif isinstance(obj, Enterprise):
                return obj in manager.enterprises.all()
            return False
        except (Manager.DoesNotExist, AttributeError):
            return False