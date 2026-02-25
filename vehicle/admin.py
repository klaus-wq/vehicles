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
from import_export.exceptions import ImportError
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
    class Meta:
        model = Enterprise

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
    def __init__(self, manager=None):
        super().__init__()
        self.manager = manager

    def skip_row(self, instance, original, row, import_context=None):
        if self.manager and instance.enterprise:
            if not self.manager.enterprises.filter(id=instance.enterprise.id).exists():
                return True
        return super().skip_row(instance, original, row, import_context)

    class Meta:
        model = Vehicle

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
    trip_id = fields.Field(
        column_name='trip_id',
        attribute='trip_id',
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

    def dehydrate_trip_id(self, obj):
        trip = TelemetryTrip.objects.filter(
            vehicle=obj.vehicle,
            start_time__lte=obj.timestamp,
            end_time__gte=obj.timestamp
        ).first()
        return trip.id if trip else None

    class Meta:
        model = TelemetryPoint
        fields = (
            'id',
            'vehicle',
            'timestamp',
            'speed',
            'location',
            'trip_id',
        )
        export_order = fields

class TelemetryTripResource(resources.ModelResource):
    def __init__(self, user=None):
        super().__init__()
        self.user = user

    def before_import_row(self, row, **kwargs):
        def create_point(address, timestamp, vehicle_id):
            if not address:
                raise ImportError("Адрес не указан")

            coords = get_coordinates(address)
            print(coords)
            if coords is None:
                raise ImportError(f"Не удалось определить координаты для адреса: {address}")

            lat, lng = coords

            existing = TelemetryPoint.objects.filter(
                vehicle_id=vehicle_id,
                location=Point(lng, lat),
                timestamp=timestamp
            ).first()

            if existing:
                return existing.id

            try:
                location = Point(lng, lat)
            except Exception as e:
                raise ImportError(f"Ошибка создания Point: {str(e)}")

            point = TelemetryPoint.objects.create(
                vehicle=vehicle,
                location=location,
                timestamp=timestamp
            )
            point.timestamp = timestamp

            print(point)

            point.save()
            return point.id

        if not self.user.is_superuser and self.user.manager:
            allowed_enterprises = set(self.user.manager.enterprises.values_list("id", flat=True))
        else:
            allowed_enterprises = None

        vehicle_id = row.get('vehicle')
        if not vehicle_id:
            raise ImportError("Не указан автомобиль")

        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            raise ImportError(f"Автомобиль {vehicle_id} не найден")

        if allowed_enterprises is not None and vehicle.enterprise.id not in allowed_enterprises:
            raise ImportError(f"Нет прав на добавление поездок для автомобиля {vehicle.car_number}")

        start_time_str = row.get('start_time')
        end_time_str = row.get('end_time')

        if not all([start_time_str, end_time_str]):
            raise ImportError("Обязательны поля start_time и end_time")

        try:
            start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")

            tz = pytz.timezone(vehicle.enterprise.timezone)
            if start_time.tzinfo is None:
                start_time = tz.localize(start_time)
            if end_time.tzinfo is None:
                end_time = tz.localize(end_time)

        except Exception as e:
            raise ImportError(f"Ошибка парсинга дат: {str(e)}")

        if start_time >= end_time:
            raise ImportError("start_time должно быть раньше end_time")


        start_address = row.get('start_address')
        end_address = row.get('end_address')
        start_point_id = create_point(start_address, start_time, vehicle_id)
        end_point_id = create_point(end_address, end_time, vehicle_id)
        if not start_point_id or not end_point_id:
            raise ImportError("Не удалось создать одну или обе точки")
        row['end_point'] = end_point_id
        row['start_point'] = start_point_id
        row['vehicle'] = vehicle.id
        row['start_time'] = start_time
        row['end_time'] = end_time

    class Meta:
        model = TelemetryTrip
        skip_unchanged = True
        # import_id_fields = ('id',)
        fields = ('id', 'vehicle', 'start_point', 'end_point', 'start_time', 'end_time')

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