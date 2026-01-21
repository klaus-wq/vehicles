from django.db import models
from django.contrib.gis.db import models as gis_models
from django.core.exceptions import ValidationError

from vehicle.models import Vehicle

class TelemetryPoint(models.Model):
    id = models.BigAutoField(primary_key=True)
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name='telemetry'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    speed = models.PositiveSmallIntegerField(null=True, blank=True)
    location = gis_models.PointField(srid=4326, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["vehicle", "timestamp"]),
            models.Index(fields=["location"]),
        ]

    def __str__(self):
        return f"{self.vehicle} - {self.location}, {self.speed}, {self.timestamp}"

class TelemetryTrip(models.Model):
    id = models.BigAutoField(primary_key=True)
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="trips",
        verbose_name="Автомобиль",
    )
    start_point = models.ForeignKey(
        TelemetryPoint,
        related_name="trip_starts",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Начало",
    )
    end_point = models.ForeignKey(
        TelemetryPoint,
        related_name="trip_ends",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Конец",
    )
    start_time = models.DateTimeField(null=True,
        blank=True,verbose_name="Время начала")
    end_time = models.DateTimeField(null=True,
        blank=True, verbose_name="Время окончания")

    def clean(self):
        if (
            self.start_time
            and self.end_time
            and self.start_time > self.end_time
        ):
            raise ValidationError(
                "Время начала поездки не может быть позже времени окончания."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=["vehicle", "start_time", "end_time"]),
        ]
        ordering = ["-start_time"]

    def __str__(self):
        return f"Поездка {self.vehicle.car_number}: {self.start_point} {self.start_time} - {self.end_point} {self.end_time}"