import uuid
from collections import defaultdict

from django.db import models
from django.db.models.functions import TruncDay, TruncMonth, TruncYear

from authentication.models import CustomUser
from telemetry.models import TelemetryTrip, TelemetryPoint
from vehicle.models import Vehicle, DriverVehicle


class Report(models.Model):
    REPORT_TYPES = [
        ('MILEAGE', 'Пробег автомобиля'),
        ('TRIPS_COUNT', 'Количество поездок'),
        ('DRIVER_ASSIGNMENT', 'Назначение водителей'),
    ]

    PERIOD_CHOICES = [
        ("DAY", "День"),
        ("MONTH", "Месяц"),
        ("YEAR", "Год"),
    ]

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name="Название отчёта")
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES, verbose_name="Тип отчёта")
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='DAY', verbose_name="Период")
    start_date = models.DateTimeField(verbose_name="Начальная дата")
    end_date = models.DateTimeField(verbose_name="Конечная дата")

    vehicle_ids = models.JSONField(default=list, verbose_name="ID Автомобилей")
    enterprise_id = models.IntegerField(null=True, blank=True, verbose_name="ID Предприятия")

    result_data = models.JSONField(default=list, verbose_name="Результат (время-значение)")

    guid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, verbose_name="Менеджер")

    class Meta:
        indexes = [
            models.Index(fields=["report_type", "created_at"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.report_type})"


class ReportGeneratorBase:
    def __init__(self, start_date, end_date, period='DAY', vehicle_ids=None, enterprise_id=None):
        self.start_date = start_date
        self.end_date = end_date
        self.period = period.upper()
        self.vehicle_ids = vehicle_ids or []
        self.enterprise_id = enterprise_id

    def get_trunc_function(self):
        mapping = {
            'DAY': TruncDay,
            'MONTH': TruncMonth,
            'YEAR': TruncYear,
        }
        trunc_class = mapping.get(self.period, TruncDay)
        return trunc_class('start_time')

    def get_period_key(self, dt):
        if self.period == "DAY":
            return dt.strftime("%Y-%m-%d")
        if self.period == "MONTH":
            return dt.strftime("%Y-%m")
        if self.period == "YEAR":
            return dt.strftime("%Y")
        return dt.isoformat()

    def generate(self):
        raise NotImplementedError


class MileageReportGenerator(ReportGeneratorBase):
    def __init__(self, start_date, end_date, period="DAY", vehicle_ids=None, enterprise_id=None):
        super().__init__(start_date, end_date, period, vehicle_ids, enterprise_id)
        self.type = 'MILEAGE'

    def generate(self):
        result = {
            "type": self.type,
            "data": {},
        }

        if self.vehicle_ids:
            vehicles = Vehicle.objects.filter(id__in=self.vehicle_ids)
        elif self.enterprise_id:
            vehicles = Vehicle.objects.filter(enterprise_id=self.enterprise_id)
        else:
            return result

        for vehicle in vehicles:
            trips = TelemetryTrip.objects.filter(
                vehicle=vehicle,
                start_time__gte=self.start_date,
                end_time__lte=self.end_date,
                end_time__isnull=False,
            ).order_by('start_time')

            periods_mileage = defaultdict(float)
            vehicle_total_km = 0.0

            for trip in trips:
                period_key = self.get_period_key(trip.start_time.date())

                points = TelemetryPoint.objects.filter(
                    vehicle=vehicle,
                    timestamp__gte=trip.start_time,
                    timestamp__lte=trip.end_time
                ).order_by('timestamp')

                if len(points) < 2:
                    continue

                total_distance_m = 0.0
                prev_point = points[0].location
                for point in points[1:]:
                    curr_point = point.location
                    if prev_point and curr_point:
                        total_distance_m += prev_point.distance(curr_point) * 111139
                    prev_point = curr_point

                trip_km = total_distance_m / 1000
                trip_km_rounded = round(trip_km, 1)

                periods_mileage[period_key] += trip_km_rounded
                vehicle_total_km += trip_km_rounded

            name = f"{vehicle.car_number} {vehicle.id} ({vehicle.brand})"

            result["data"][vehicle.car_number] = {
                "name": name,
                "periods": dict(periods_mileage),
                "total": round(vehicle_total_km, 1)
            }

        return result


class DriverAssignmentReportGenerator(ReportGeneratorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'DRIVER_ASSIGNMENT'

    def generate(self):
        result = {
            "type": self.type,
            "data": {},
            "summary": {
                "total_vehicles": 0,
                "total_drivers": 0,
                "active_assignments": 0,
                "inactive_assignments": 0,
                "assignments_in_period": 0
            }
        }

        if self.vehicle_ids:
            vehicles = Vehicle.objects.filter(id__in=self.vehicle_ids)
        elif self.enterprise_id:
            vehicles = Vehicle.objects.filter(enterprise_id=self.enterprise_id)
        else:
            return result

        all_drivers = set()
        total_assignments = 0
        periods_data = {}

        for vehicle in vehicles:
            assignments = DriverVehicle.objects.filter(
                vehicle=vehicle,
                vehicle__created_at__gte=self.start_date,
                vehicle__created_at__lte=self.end_date
            ).select_related('driver', 'driver__enterprise')

            if not assignments.exists():
                continue

            for vd in assignments:
                print('vd', vd.vehicle.created_at, vd.driver)
                driver = vd.driver
                print(driver.id)
                all_drivers.add(driver.id)
                period_key = self.get_period_key(vd.vehicle.created_at.date())
                print(period_key)
                total_assignments += 1

                if period_key not in periods_data:
                    periods_data[period_key] = {}

                if vehicle.car_number not in periods_data[period_key]:
                    periods_data[period_key][vehicle.car_number] = {
                        "brand": f"{vehicle.brand.name}",
                        "enterprise": vehicle.enterprise.name,
                        "drivers": []
                    }

                periods_data[period_key][vehicle.car_number]["drivers"].append({
                    "id": driver.id,
                    "name": f"{driver.last_name} {driver.first_name}",
                    "license": driver.license_number,
                    "assigned_date": vd.vehicle.created_at.strftime("%d.%m.%Y %H:%M"),
                    "is_active": vd.is_active,
                })


        result["data"] = periods_data

        result["summary"] = {
            "total_vehicles": len(set(
                car for period in periods_data.values() for car in period.keys()
            )),
            "total_drivers": len(all_drivers),
            "assignments_in_period": total_assignments,
        }

        print(result)

        return result