import random
import time
import math
import requests

from django.core.management.base import BaseCommand
from datetime import datetime, timedelta, timezone
from django.contrib.gis.geos import Point
from django.db import transaction
from faker import Faker

from telemetry.models import TelemetryTrip, TelemetryPoint
from vehicle.models import Vehicle
from vehicles.settings import GRAPHOPPER_API_KEY, ORS_API_KEY

LOCATIONS = [
    {'name': 'Krasnoyarsk', 'lat': 56.0153, 'lon': 92.8932, 'radius': 3.0},
    {'name': 'Divnogorsk', 'lat': 55.962, 'lon': 92.384, 'radius': 2.5},
    {'name': 'Emelyanovo', 'lat': 56.105, 'lon': 92.485, 'radius': 2.0},
    {'name': 'Sosnovoborsk', 'lat': 56.115, 'lon': 93.345, 'radius': 1.5},
]


def get_route_osrm(start: Point, end: Point, timeout: int = 30):
    """Получает маршрут через публичный OSRM сервер (v5+ API)"""
    url = f"http://router.project-osrm.org/route/v1/driving/{start.x},{start.y};{end.x},{end.y}"

    params = {
        'geometries': 'geojson',
        'overview': 'full'
    }

    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        data = response.json()

        if data.get('code') != 'Ok' or not data.get('routes'):
            return None

        coordinates = data['routes'][0]['geometry']['coordinates']
        distance = data['routes'][0]['distance']
        return [(lon, lat) for lon, lat in coordinates], distance

    except Exception as e:
        print(f"⚠️ OSRM error: {e}")
        return None

def random_point_nearby(current: Point, center: Point, radius: float, max_step: float, max_attempts: int = 50) -> Point:
    """Генерирует точку недалеко от current, но гарантированно в пределах radius от center"""
    for _ in range(max_attempts):
        lat_offset = random.uniform(-max_step / 111.3, max_step / 111.3)
        lon_offset = random.uniform(
            -max_step / (111.3 * math.cos(math.radians(current.y))),
            max_step / (111.3 * math.cos(math.radians(current.y)))
        )

        new_lat = current.y + lat_offset
        new_lon = current.x + lon_offset
        res_point = Point(new_lon, new_lat)

        if equirectangular_distance(center.y, center.x, res_point.y, res_point.x) < radius:
            return res_point

    # точка в центре радиуса
    return random_point_in_radius(center.y, center.x, radius * 0.5)

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

    lat = (step / 111.3) * math.cos(theta)
    lon = (step / (111.3 * math.cos(math.radians(current.y)))) * math.sin(theta)

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
        parser.add_argument('--count', type=int, help='Количество треков')
        # parser.add_argument('--vehicle_id', type=int, help='ID автомобиля')
        parser.add_argument('--length_min', type=int, help='Минимальная длина трека')
        parser.add_argument('--length_max', type=int, help='Максимальная длина трека')
        parser.add_argument('--length_km', type=float, default=10.0, help='Длина трека в км')
        parser.add_argument('--step_km', type=float, default=0.1, help='Шаг между точками в км')

    def handle(self, *args, **options):
        # vehicle_id = options['vehicle_id']
        # total_length = options['length_km']
        length_min = options['length_min']
        length_max = options['length_max']
        step = options['step_km']
        # center_lat = 56.0153
        # center_lon = 92.8932
        # radius = 3.0
        vehicles = list(Vehicle.objects.all())
        count = options['count']

        # try:
        #     vehicle = Vehicle.objects.get(id=vehicle_id)
        # except Vehicle.DoesNotExist:
        #     self.stdout.write(self.style.ERROR(f'{vehicle_id} не существует'))
        #     return

        for idx in range(count):
            with transaction.atomic():
                vehicle = random.choice(vehicles)
                point_location = random.choice(LOCATIONS)
                center_lat = point_location['lat']
                center_lon = point_location['lon']
                radius = point_location['radius']
                total_length = random.uniform(length_min, length_max)
                current_point = random_point_in_radius(center_lat, center_lon, radius)
                start_point = None
                end_point = None
                previous_point = None

                current_length = 0.0

                self.stdout.write(self.style.SUCCESS(
                    f"Генерация трека для автомобиля {vehicle.id}....."
                ))

                fake = Faker()
                point_start_time = fake.date_time_between(start_date="-5y", end_date="now", tzinfo=timezone.utc)

                while current_length < total_length:
                    # random_point = random_point_with_step(current_point, Point(center_lon, center_lat), radius, step)
                    random_point = random_point_nearby(current_point, Point(center_lon, center_lat), radius, step)

                    result = get_route_osrm(current_point, random_point)
                    coordinates, segment_distance = result if result else (None, 0)

                    # try:
                    #     response = requests.get(f"https://graphhopper.com/api/1/route?point={current_point.y},{current_point.x}&point={random_point.y},{random_point.x}&profile=car&locale=de&calc_points=true&points_encoded=false&key={GRAPHOPPER_API_KEY}", timeout=10)
                    #     data = response.json()
                    # except Exception as e:
                    #     self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))
                    #     return
                    #
                    # if 'paths' not in data or not data['paths']:
                    #     continue
                    #
                    # coordinates = data["paths"][0]["points"]["coordinates"]

                    for i, (lon, lat) in enumerate(coordinates):
                        location = Point(lon, lat)
                        if previous_point is not None and previous_point.distance(location) < 0.00009:
                            continue
                        previous_point = location

                        telemetry_point = TelemetryPoint(vehicle=vehicle, location=location)
                        telemetry_point.save()

                        point_start_time += timedelta(seconds=10)
                        telemetry_point.timestamp = point_start_time
                        telemetry_point.save()

                        if start_point is None:
                            start_point = telemetry_point
                        end_point = telemetry_point

                        # self.stdout.write(self.style.SUCCESS(f"Добавлена точка: [{lat} {lon}] в {telemetry_point.timestamp}."))

                        # time.sleep(10)

                    current_point = Point(coordinates[-1][0], coordinates[-1][1])
                    current_length += segment_distance / 1000
                    # current_length += data["paths"][0]["distance"] / 1000
                    # self.stdout.write(f"Остаток: {total_length - current_length} km")

                telemetry_trip = TelemetryTrip(
                    vehicle=vehicle,
                    start_point=start_point,
                    end_point=end_point,
                    start_time=start_point.timestamp,
                    end_time=end_point.timestamp,
                )
                telemetry_trip.save()

                self.stdout.write(self.style.SUCCESS("Трек готов"))