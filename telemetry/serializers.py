import pytz
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import TelemetryPoint

class VehicleGPSPointSerializer(serializers.ModelSerializer):
    timestamp = serializers.SerializerMethodField()

    class Meta:
        model = TelemetryPoint
        fields = ["vehicle", "location", "timestamp"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timezone_cache = None

    def get_timestamp(self, obj):
        timestamp = obj.timestamp
        if timestamp is None:
            return timestamp
        if self.timezone_cache is None:
            self.timezone_cache = pytz.timezone(obj.vehicle.enterprise.timezone)
        timestamp = timestamp.astimezone(self.timezone_cache)
        return timestamp

class GeoJSONVehicleGPSPointSerializer(GeoFeatureModelSerializer):
    timestamp = serializers.SerializerMethodField()

    class Meta:
        model = TelemetryPoint
        geo_field = "location"
        fields = ["vehicle", "timestamp"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timezone_cache = None

    def get_timestamp(self, obj):
        if self.timezone_cache is None:
            self.timezone_cache = pytz.timezone(obj.vehicle.enterprise.timezone)
        timestamp = obj.timestamp
        if timestamp is None:
            return timestamp
        timestamp = timestamp.astimezone(self.timezone_cache)
        return timestamp

class TelemetryPointSerializer(serializers.ModelSerializer):
    timestamp = serializers.SerializerMethodField()

    class Meta:
        model = TelemetryPoint
        fields = ['id', 'timestamp', 'speed', 'location']

    def get_timestamp(self, obj):
        # Всегда переводим в таймзону предприятия автомобиля
        tz = pytz.timezone(obj.vehicle.enterprise.timezone)
        return obj.timestamp.astimezone(tz)

class TelemetryPointGeoSerializer(GeoFeatureModelSerializer):
    timestamp = serializers.SerializerMethodField()

    class Meta:
        model = TelemetryPoint
        geo_field = 'location'
        fields = ['id', 'timestamp', 'speed']

    def get_timestamp(self, obj):
        tz = pytz.timezone(obj.vehicle.enterprise.timezone)
        return obj.timestamp.astimezone(tz)