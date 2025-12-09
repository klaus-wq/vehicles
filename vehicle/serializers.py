import pytz
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated

from authentication.models import Manager
from authentication.serializers import ManagerSerializer
from vehicle.models import Vehicle, Enterprise, Driver, DriverVehicle

from vehicle.models import Brand
from vehicle.permissions import IsManagerOrReadOnly


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'vehicle_type', 'fuel_tank_capacity', 'cargo_capacity', 'seating_capacity']

class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = [
            'id',
            # 'enterprise',
            'first_name',
            'last_name',
            'license_number',
            'salary'
            # 'vehicles'
        ]

class VehicleSerializer(serializers.ModelSerializer):
    active_driver = serializers.SerializerMethodField()
    purchase_datetime = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            'id',
            'car_number',
            'price',
            'year',
            'mileage',
            'fuel_type',
            'transmission',
            'color',
            'created_at',
            'purchase_datetime',
            'brand',
            'enterprise',
            'drivers',
            'active_driver'
        ]

    def get_active_driver(self, obj):
        try:
            active_driver = obj.vehicle_drivers.filter(is_active=True).first()
            if active_driver:
                return active_driver.driver.id
            return -1
        except:
            return -1

    def get_purchase_datetime(self, obj):
        if not obj.purchase_datetime:
            return None
        tz = pytz.timezone(obj.enterprise.timezone or 'UTC')
        return obj.purchase_datetime.astimezone(tz).isoformat()

class DriverVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverVehicle
        fields = [
            'driver',
            'vehicle',
            'is_active'
        ]

class EnterpriseSerializer(serializers.ModelSerializer):
    drivers = serializers.SerializerMethodField()
    vehicles = serializers.SerializerMethodField()
    managers = serializers.SerializerMethodField()
    # managers = ManagerSerializer(many=True, read_only=True)
    # managers = [manager['id'] for manager in ManagerSerializer(Manager.objects.all(), many=True).data]

    class Meta:
        model = Enterprise
        fields = [
            'id',
            'name',
            'city',
            'address',
            'phone',
            'drivers',
            'vehicles',
            'managers'
        ]

    def get_drivers(self, obj):
        return list(obj.drivers.values_list('id', flat=True))

    def get_vehicles(self, obj):
        return list(obj.vehicles.values_list('id', flat=True))

    def get_managers(self, obj):
        return list(obj.managers.values_list('id', flat=True))