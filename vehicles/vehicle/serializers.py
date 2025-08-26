from rest_framework import serializers
from vehicle.models import Vehicle

class VehicleSerializer(serializers.ModelSerializer):
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
        ]