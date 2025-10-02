from rest_framework import serializers
from vehicle.models import Vehicle, Enterprise, Driver, DriverVehicle, Manager

from vehicle.models import Brand


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
            'brand',
            # 'enterprise',
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

class DriverVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverVehicle
        fields = [
            'driver',
            'vehicle',
            'is_active'
        ]

class ManagerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Manager
        fields = ['id', 'username', 'enterprises']

class EnterpriseSerializer(serializers.ModelSerializer):
    drivers = serializers.SerializerMethodField()
    vehicles = serializers.SerializerMethodField()
    managers = [manager['id'] for manager in ManagerSerializer(Manager.objects.all(), many=True).data]

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