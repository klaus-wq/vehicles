from django.contrib import admin

from authentication.models import Manager, CustomUser
from .models import Vehicle, Brand, Enterprise, Driver, DriverVehicle
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db.models import Q

from .permissions import ManagerPermissionAdmin

class ManagerInline(admin.StackedInline):
    model = Manager
    can_delete = False
    verbose_name_plural = 'Менеджер'
    fk_name = 'user'
    filter_horizontal = ('enterprises',)

class ManagerAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_enterprises')
    filter_horizontal = ('enterprises',)  # Удобный виджет для ManyToMany

    def get_enterprises(self, obj):
        return ", ".join([e.name for e in obj.enterprises.all()])

    get_enterprises.short_description = 'Предприятия'

class CustomUserAdmin(UserAdmin):
    inlines = (ManagerInline,)
    list_display = ('username', 'first_name', 'last_name', 'is_staff', 'is_manager')
    list_select_related = True

    def is_manager(self, user):
        return hasattr(user, 'manager')

    is_manager.boolean = True
    is_manager.short_description = 'Менеджер'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

class EnterpriseAdmin(ManagerPermissionAdmin):
    list_display = ('id', 'name', 'city', 'address', 'phone')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Суперпользователь видит все
        if request.user.is_superuser:
            return qs
        try:
            # Обычный менеджер видит только свои предприятия
            manager = Manager.objects.get(user=request.user)
            return qs.filter(managers=manager)
        except (Manager.DoesNotExist, AttributeError):
            return qs.none()

    def has_add_permission(self, request):
        return request.user.is_superuser or hasattr(request.user, 'manager')

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        try:
            if obj is not None:
                return obj.managers.filter(user=request.user).exists()
            return True
        except (Manager.DoesNotExist, AttributeError):
            return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or hasattr(request.user, 'manager')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            if hasattr(request.user, 'manager'):
                obj.managers.add(request.user.manager)

class VehicleAdmin(ManagerPermissionAdmin):
    list_display = ('id', 'car_number', 'enterprise', 'brand', 'price', 'year', 'mileage', 'fuel_type', 'transmission',
                    'color', 'created_at', 'get_drivers', 'get_active_driver')

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or hasattr(request.user, 'manager')

    def get_drivers(self, obj):
        drivers = obj.drivers.all()[:3]
        drivers_list = [f"{driver.last_name} {driver.first_name}" for driver in drivers]
        if obj.drivers.count() > 3:
            return ", ".join(drivers_list) + ", ..."
        return ", ".join(drivers_list) or "Нет водителей"

    get_drivers.short_description = 'Водители'

    def get_active_driver(self, obj):
        try:
            active_driver = obj.drivers.all().filter(id=(obj.vehicle_drivers.filter(is_active=True).first()).driver.id).first()
            if active_driver:
                return f"{active_driver.last_name} {active_driver.first_name}"
            return "Нет активного водителя"
        except:
            return "Нет активного водителя"

    get_active_driver.short_description = 'Активный водитель'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs.prefetch_related('drivers')
        try:
            manager = request.user.manager
            return qs.filter(enterprise__managers=manager).prefetch_related('drivers')
        except (Manager.DoesNotExist, AttributeError):
            return qs.none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "enterprise" and not request.user.is_superuser:
            try:
                manager = request.user.manager
                kwargs["queryset"] = Enterprise.objects.filter(managers=manager)
            except (Manager.DoesNotExist, AttributeError):
                kwargs["queryset"] = Enterprise.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class DriverAdmin(ManagerPermissionAdmin):
    list_display = ('id', 'enterprise', 'first_name', 'last_name', 'license_number', 'salary')

    def full_name(self, obj):
        return f"{obj.id} {obj.enterprise} {obj.last_name} {obj.first_name}"

    full_name.short_description = 'ФИО'

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or hasattr(request.user, 'manager')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            manager = request.user.manager
            return qs.filter(enterprise__managers=manager)
        except (Manager.DoesNotExist, AttributeError):
            return qs.none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "enterprise" and not request.user.is_superuser:
            try:
                manager = request.user.manager
                kwargs["queryset"] = Enterprise.objects.filter(managers=manager)
            except (Manager.DoesNotExist, AttributeError):
                kwargs["queryset"] = Enterprise.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class DriverVehicleAdmin(ManagerPermissionAdmin):
    list_display = ('driver', 'vehicle', 'is_active')

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or hasattr(request.user, 'manager')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            manager = Manager.objects.filter(user=request.user).first()
            return qs.filter(
                Q(driver__enterprise__managers=manager) &
                Q(vehicle__enterprise__managers=manager)
            )
        except (Manager.DoesNotExist, AttributeError):
            return qs.none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "driver" and not request.user.is_superuser:
            try:
                manager = Manager.objects.filter(user=request.user).first()
                kwargs["queryset"] = Driver.objects.filter(enterprise__managers=manager)
            except (Manager.DoesNotExist, AttributeError):
                kwargs["queryset"] = Driver.objects.none()
        elif db_field.name == "vehicle" and not request.user.is_superuser:
            try:
                manager = Manager.objects.filter(user=request.user).first()
                kwargs["queryset"] = Vehicle.objects.filter(enterprise__managers=manager)
            except (Manager.DoesNotExist, AttributeError):
                kwargs["queryset"] = Vehicle.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Enterprise, EnterpriseAdmin)
admin.site.register(Brand)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(DriverVehicle, DriverVehicleAdmin)
admin.site.register(Manager, ManagerAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
