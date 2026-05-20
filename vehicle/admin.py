import uuid
from datetime import datetime

import pytz
from django.contrib import admin
from django.contrib.gis.geos import Point
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin, ExportActionMixin
from import_export.widgets import ForeignKeyWidget

from authentication.models import Manager, CustomUser
from telemetry.models import TelemetryTrip, TelemetryPoint
from telemetry.utils.geocoder import get_address, get_coordinates
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

class EnterpriseResource(resources.ModelResource):
    guid = fields.Field(column_name="guid", attribute="guid")

    class Meta:
        model = Enterprise
        fields = (
            "guid",
            "name",
            "city",
            "address",
            "phone",
            "timezone",
        )

class EnterpriseAdmin(ManagerPermissionAdmin, ImportExportModelAdmin, ExportActionMixin):
    resource_class = EnterpriseResource
    list_display = ('id', 'name', 'city', 'address', 'phone', 'timezone')

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

class VehicleResource(resources.ModelResource):
    guid = fields.Field(default=uuid.uuid4, column_name="guid",
                        attribute="guid", )

    enterprise_guid = fields.Field(
        column_name="enterprise_guid",
        attribute="enterprise",
        widget=ForeignKeyWidget(Enterprise, "guid"),
    )

    brand_guid = fields.Field(
        column_name="brand_guid",
        attribute="brand",
        widget=ForeignKeyWidget(Brand, "guid"),
    )

    def __init__(self, manager=None):
        super().__init__()
        self.manager = manager

    class Meta:
        model = Vehicle
        fields = (
            "guid",
            "car_number",
            "price",
            "year",
            "mileage",
            "fuel_type",
            "transmission",
            "color",
            "created_at",
            "brand_guid",
            "transmission",
            "enterprise_guid",
            "purchase_datetime",
        )

class VehicleAdmin(ManagerPermissionAdmin, ImportExportModelAdmin, ExportActionMixin):
    resource_class = VehicleResource
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

class TelemetryPointResource(resources.ModelResource):
    trip_guid = fields.Field(
        column_name='trip_guid',
        attribute='trip_guid',
        readonly=True
    )
    points = fields.Field(column_name='points', readonly=True)

    def dehydrate_points(self, trip):
        points = TelemetryPoint.objects.filter(
            vehicle=trip.vehicle,
            timestamp__range=(trip.start_time, trip.end_time)
        ).order_by('timestamp').values('timestamp', 'location')

        result = []
        for p in points:
            loc = p['location']
            if loc:
                coords = [loc.x, loc.y]  # lng, lat
            else:
                coords = None
            result.append({
                'timestamp': p['timestamp'].isoformat(),
                'location': coords,
            })
        return result

    def dehydrate_trip_guid(self, obj):
        trip = TelemetryTrip.objects.filter(
            vehicle=obj.vehicle,
            start_time__lte=obj.timestamp,
            end_time__gte=obj.timestamp
        ).first()
        return trip.guid if trip else None

    class Meta:
        model = TelemetryPoint
        fields = (
            'id',
            'guid',
            'vehicle',
            'timestamp',
            'speed',
            'location',
            'trip_guid',
            'points'
        )

class TelemetryTripResource(resources.ModelResource):
    guid = fields.Field(column_name="guid", attribute="guid")

    vehicle = fields.Field(
        column_name="vehicle_guid",
        attribute="vehicle",
        widget=ForeignKeyWidget(Vehicle, "guid"),
    )

    def __init__(self, user=None):
        super().__init__()
        self.user = user

    class Meta:
        model = TelemetryTrip
        skip_unchanged = True
        # import_id_fields = ('id',)
        fields = (
            "guid",
            "vehicle",
            "start_time",
            "end_time",
            "start_point",
            "end_point",
        )

    def dehydrate_start_point(self, trip):
        if trip.start_point and trip.start_point.location:
            return get_address(trip.start_point.location.y, trip.start_point.location.x)
        return None

    def dehydrate_end_point(self, trip):
        if trip.end_point and trip.end_point.location:
            return get_address(trip.end_point.location.y, trip.end_point.location.x)
        return None

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        manager = Manager.objects.get(user=request.user)
        return qs.filter(vehicle__enterprise__in=manager.enterprises.all())


class TelemetryTripAdmin(ImportExportModelAdmin, ExportActionMixin):
    resource_class = TelemetryTripResource
    model = TelemetryTrip
    list_display = [
        "id",
        "vehicle",
        "start_point",
        "end_point",
        "start_time",
        "end_time",
    ]

    def start_time(self, obj):
        if obj.start_time:
            return obj.start_time.strftime("%Y-%m-%d %H:%M:%S")
        return None

    def end_time(self, obj):
        if obj.end_time:
            return obj.end_time.strftime("%Y-%m-%d %H:%M:%S")
        return None

    def start_point(self, obj):
        if not obj.start_point or not obj.start_point.point:
            return None
        lat, lng = obj.start_point.point.y, obj.start_point.point.x
        start_address = get_address(lat, lng)
        return start_address

    def end_point(self, obj):
        if not obj.end_point or not obj.end_point.point:
            return None
        lat, lng = obj.end_point.point.y, obj.end_point.point.x
        end_address = get_address(lat, lng)
        return end_address

    start_time.short_description = "Время начала поездки"
    end_time.short_description = "Время окончания поездки"
    start_point.short_description = "Начальная точка"
    end_point.short_description = "Конечная точка"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        manager = Manager.objects.get(user=request.user)
        return qs.filter(vehicle__enterprise__in=manager.enterprises.all())

# class DriverResource(resources.ModelResource):
#     class Meta:
#         model = Driver
#         import_id_fields = ('license_number',)
#         fields = (
#             'license_number',
#             'first_name',
#             'last_name',
#             'enterprise',
#         )
#         skip_unchanged = True
#
# class DriverVehicleResource(resources.ModelResource):
#     driver = fields.Field(
#         column_name='driver_license',
#         attribute='driver',
#         widget=ForeignKeyWidget(Driver, 'license_number')
#     )
#
#     vehicle = fields.Field(
#         column_name='car_number',
#         attribute='vehicle',
#         widget=ForeignKeyWidget(Vehicle, 'car_number')
#     )
#
#     def dehydrate_driver_license(self, obj):
#         return obj.driver.license_number if obj.driver else ''
#
#     def dehydrate_car_number(self, obj):
#         return obj.vehicle.car_number if obj.vehicle else ''
#
#     class Meta:
#         model = DriverVehicle
#         fields = (
#             'driver_license',
#             'car_number',
#             'is_active',
#         )
#         skip_unchanged = True

admin.site.register(Enterprise, EnterpriseAdmin)
admin.site.register(Brand)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(DriverVehicle, DriverVehicleAdmin)
admin.site.register(Manager, ManagerAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(TelemetryTrip, TelemetryTripAdmin)