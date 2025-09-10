from rest_framework import serializers
from vehicle.models import Vehicle, Enterprise, Driver, DriverVehicle

from vehicle.models import Brand


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'vehicle_type', 'fuel_tank_capacity', 'cargo_capacity', 'seating_capacity']

class VehicleSerializer(serializers.ModelSerializer):
    # active_driver = serializers.SerializerMethodField()

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
            'driver',
            'is_active'
        ]

    # def get_active_driver(self, obj):
    #     try:
    #         active_driver = obj.vehicle_drivers.filter(is_active=True).first()
    #         if active_driver:
    #             return active_driver.id
    #         return -1
    #     except:
    #         return -1

class DriverSerializer(serializers.ModelSerializer):
    vehicles = VehicleSerializer(many=True, read_only=True, source='vehicles1')

    class Meta:
        model = Driver
        fields = [
            'id',
            # 'enterprise',
            'first_name',
            'last_name',
            'license_number',
            'salary',
            'vehicles'
        ]

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

    class Meta:
        model = Enterprise
        fields = [
            'id',
            'name',
            'city',
            'address',
            'phone',
            'drivers',
            'vehicles'
        ]

    def get_drivers(self, obj):
        return list(obj.drivers.values_list('id', flat=True))

    def get_vehicles(self, obj):
        return list(obj.vehicles.values_list('id', flat=True))