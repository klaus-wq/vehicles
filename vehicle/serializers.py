from rest_framework import serializers
from vehicle.models import Vehicle, Enterprise, Driver, DriverVehicle

from vehicle.models import Brand


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'vehicle_type', 'fuel_tank_capacity', 'cargo_capacity', 'seating_capacity']

class EnterpriseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enterprise
        fields = [
            'id',
            'name',
            'city',
            'address',
            'phone'
        ]

class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = [
            'id',
            'enterprise',
            'first_name',
            'last_name',
            'license_number',
            'salary'
            # 'vehicles'
        ]

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
            'enterprise',
            'drivers',
            # 'active_driver'
        ]

    def get_active_driver(self, obj):
        active_driver = obj.vehicle_drivers.filter(is_active=True).first()
        if active_driver:
            return active_driver.id
        return None

class DriverVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverVehicle
        fields = [
            'driver',
            'vehicle',
            'is_active'
        ]