from django.db import models
from django.contrib.gis.db import models as gis_models

from vehicle.models import Vehicle

class TelemetryPoint(models.Model):
    id = models.BigAutoField(primary_key=True)
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name='telemetry'
    )
    timestamp = models.DateTimeField(db_index=True)
    speed = models.PositiveSmallIntegerField(null=True, blank=True)
    location = gis_models.PointField(srid=4326, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['vehicle', '-timestamp'], name='idx_vehicle_ts_desc'),
        ]

    def __str__(self):
        return f"{self.vehicle} - {self.location}, {self.speed}, {self.timestamp}"