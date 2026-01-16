import random
import time
import math
import requests
from datetime import timedelta, datetime

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.gis.geos import Point

from telemetry.models import TelemetryTrip, TelemetryPoint
from vehicle.models import Vehicle
from vehicles.settings import GRAPHOPPER_API_KEY

def equirectangular_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Упрощённая формула Гаверсина для малых расстояний https://www.movable-type.co.uk/scripts/latlong.html."""
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta = math.radians(lon2 - lon1)
    phim = (phi1 + phi2) / 2
    x = delta * math.cos(phim)
    y = phi2 - phi1
    d = R * math.sqrt(x * x + y * y)
    return d

def random_point_with_step(current: Point, center: Point, radius: float, step: float) -> Point:
    theta = random.uniform(0, 2 * math.pi)

    lat = (step / 111.32) * math.cos(theta)
    lon = (step / (111.32 * math.cos(math.radians(current.y)))) * math.sin(theta)

    new_lat = current.y + lat
    new_lon = current.x + lon

    res_point = Point(new_lon, new_lat)

    distance_to_center = equirectangular_distance(center.y, center.x, res_point.y, res_point.x)
    while distance_to_center >= radius:
        res_point = random_point_with_step(current, center, radius, step)
    return res_point

def random_point_in_radius(center_lat: float, center_lon: float, radius: float) -> Point:
    """Полярные координаты https://habr.com/ru/articles/583838/"""
    r = radius * math.sqrt(random.random())
    theta = random.uniform(0, 2 * math.pi)

    lat = (r / 111.32) * math.cos(theta)
    lon = (r / (111.32 * math.cos(math.radians(center_lat)))) * math.sin(theta)

    new_lat = center_lat + lat
    new_lon = center_lon + lon

    return Point(new_lon, new_lat)


class Command(BaseCommand):
    help = 'Генерирует трек для автомобиля в Красноярске.'

    def add_arguments(self, parser):
        parser.add_argument('vehicle_id', type=int, help='ID автомобиля')
        parser.add_argument('--length_km', type=float, default=10.0, help='Длина трека в км')
        parser.add_argument('--step_km', type=float, default=0.1, help='Шаг между точками в км')

    def handle(self, *args, **options):
        vehicle_id = options['vehicle_id']
        total_length = options['length_km']
        step = options['step_km']
        center_lat = 56.0153
        center_lon = 92.8932
        radius = 3.0

        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'{vehicle_id} не существует'))
            return

        self.stdout.write(self.style.SUCCESS(
            f"Генерация трека для автомобиля {vehicle_id}....."
        ))

        current_point = random_point_in_radius(center_lat, center_lon, radius)
        start_point = None
        end_point = None
        previous_point = None

        current_length = 0.0

        while current_length < total_length:
            random_point = random_point_with_step(current_point, Point(center_lon, center_lat), radius, step)

            try:
                response = requests.get(f"https://graphhopper.com/api/1/route?point={current_point.y},{current_point.x}&point={random_point.y},{random_point.x}&profile=car&locale=de&calc_points=true&points_encoded=false&key={GRAPHOPPER_API_KEY}", timeout=10)
                data = response.json()
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))
                return

            if 'paths' not in data or not data['paths']:
                continue

            coordinates = data["paths"][0]["points"]["coordinates"]#

            for i, (lon, lat) in enumerate(coordinates):
                location = Point(lon, lat)
                if previous_point is not None and previous_point.distance(location) < 0.00009:
                    continue
                previous_point = location

                telemetry_point = TelemetryPoint(vehicle=vehicle, location=location, timestamp=datetime.now())
                telemetry_point.save()

                if start_point is None:
                    start_point = telemetry_point
                end_point = telemetry_point

                self.stdout.write(self.style.SUCCESS(f"Добавлена точка: [{lat} {lon}] в {telemetry_point.timestamp}."))

                time.sleep(10)

            current_point = Point(coordinates[-1][0], coordinates[-1][1])
            current_length += data["paths"][0]["distance"] / 1000
            self.stdout.write(f"Остаток: {total_length - current_length} km")

        telemetry_trip = TelemetryTrip(
            vehicle=vehicle,
            start_point=start_point,
            end_point=end_point,
        )
        telemetry_trip.save()

        self.stdout.write(self.style.SUCCESS("Трек готов"))