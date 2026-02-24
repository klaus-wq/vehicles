import pytz
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import TelemetryPoint, TelemetryTrip
from .utils.geocoder import get_address


class TelemetryPointSerializer(serializers.ModelSerializer):
    timestamp = serializers.SerializerMethodField()

    class Meta:
        model = TelemetryPoint
        fields = ['id', 'timestamp','location']

    def get_timestamp(self, obj):
        # Всегда переводим в таймзону предприятия автомобиля
        tz = pytz.timezone(obj.vehicle.enterprise.timezone)
        return obj.timestamp.astimezone(tz)

class TelemetryPointGeoSerializer(GeoFeatureModelSerializer):
    timestamp = serializers.SerializerMethodField()

    class Meta:
        model = TelemetryPoint
        geo_field = 'location'
        fields = ['id', 'timestamp']

    def get_timestamp(self, obj):
        tz = pytz.timezone(obj.vehicle.enterprise.timezone)
        return obj.timestamp.astimezone(tz)

class TripSerializer(serializers.ModelSerializer):
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    start_address = serializers.SerializerMethodField()
    end_address = serializers.SerializerMethodField()

    class Meta:
        model = TelemetryTrip
        fields = [
            'id',
            'start_time',
            'end_time',
            'start_address',
            'end_address',
        ]

    def get_start_time(self, obj):
        if obj.start_time:
            tz = pytz.timezone(obj.vehicle.enterprise.timezone)
            return obj.start_time.astimezone(tz)
        return None

    def get_end_time(self, obj):
        if obj.end_time:
            tz = pytz.timezone(obj.vehicle.enterprise.timezone)
            return obj.end_time.astimezone(tz)
        return None

    def get_start_address(self, obj):
        if not obj.start_point:
            return "Адрес неизвестен"
        lat = obj.start_point.location.y
        lon = obj.start_point.location.x
        return get_address(lat, lon)

    def get_end_address(self, obj):
        if not obj.end_point:
            return "Адрес неизвестен"
        lat = obj.end_point.location.y
        lon = obj.end_point.location.x
        return get_address(lat, lon)

