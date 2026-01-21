import pytz
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import TelemetryPoint

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