import random
from django.core.management.base import BaseCommand
from faker import Faker

from vehicle.models import (
    Enterprise, Driver, Brand, Vehicle, DriverVehicle
)

fake = Faker('ru_RU')


class Command(BaseCommand):
    help = 'Генерация данных для предприятий.'

    def add_arguments(self, parser):
        parser.add_argument(
            'enterprise_ids', nargs='+', type=int,
            help='ID предприятий.'
        )
        parser.add_argument(
            '--total_vehicles', type=int, required=True,
            help='Количество машин на все предприятия.'
        )
        parser.add_argument(
            '--total_drivers', type=int, required=True,
            help='Количество водителей на все предприятия.'
        )
        parser.add_argument(
            '--clear', action='store_true',
            help='Очистить машины, водителей и назначения перед генерацией.'
        )

    def handle(self, *args, **options):
        enterprise_ids = options['enterprise_ids']
        total_vehicles = options['total_vehicles']
        total_drivers = options['total_drivers']

        enterprises = Enterprise.objects.filter(id__in=enterprise_ids)
        total_enterprises = enterprises.count()
        if total_enterprises != len(enterprise_ids):
            self.stdout.write(self.style.ERROR("Предприятия не найдены!"))
            return

        if options['clear']:
            self.clear_data()

        self.stdout.write(f"Генерация {total_vehicles} машин и {total_drivers} водителей для {total_enterprises} предприятий.")

        if not Brand.objects.exists():
            self.create_brands()
        brands = list(Brand.objects.all())

        for _ in range(total_vehicles):
            self.create_vehicle(enterprises, brands)
        self.stdout.write(f"Сгенерировано {total_vehicles} машин", ending='')

        for _ in range(total_drivers):
            self.create_driver(enterprises)
        self.stdout.write(f" и {total_drivers} водителей.")

        total_active = 0
        for enterprise in enterprises:
            vehicles = Vehicle.objects.filter(enterprise=enterprise)
            drivers = Driver.objects.filter(enterprise=enterprise)

            if not vehicles or not drivers:
                continue

            active = self.assign_drivers(vehicles, drivers)
            total_active += active

            self.stdout.write(
                f"→ {enterprise.name}: {len(vehicles)} м, {len(drivers)} в | "
                f"{active} акт"
            )

        self.stdout.write(self.style.SUCCESS(
            f"\nГотово!\n"
            f"• Предприятий: {len(enterprises)}\n"
            f"• Машин: {total_vehicles}\n"
            f"• Водителей: {total_drivers}\n"
            f"• Активных водителей: {total_active}\n"
        ))

    def clear_data(self):
        DriverVehicle.objects.all().delete()
        Driver.objects.all().delete()
        Vehicle.objects.all().delete()
        self.stdout.write(self.style.WARNING("Данные очищены."))

    def create_brands(self):
        brands_data = [
            (1, 'noname', 'unknown', 0, None, 0),
            (2, 'КамАЗ', 'truck', 350, 20000, 3),
            (3, 'ГАЗ', 'truck', 120, 1500, 3),
            (4, 'Volvo', 'truck', 600, 25000, 2),
            (5, 'Mercedes-Benz', 'truck', 500, 22000, 2),
            (6, 'Hyundai', 'car', 50, None, 5),
            (7, 'Toyota', 'car', 60, None, 5),
            (8, 'ПАЗ', 'bus', 200, None, 43),
            (9, 'ЛиАЗ', 'bus', 300, None, 100),
            (10, 'Yamaha', 'motorcycle', 15, None, 2),
        ]
        for pk, name, vtype, tank, cargo, seats in brands_data:
            Brand.objects.update_or_create(
                id=pk,
                defaults={
                    'name': name,
                    'vehicle_type': vtype,
                    'fuel_tank_capacity': tank,
                    'cargo_capacity': cargo,
                    'seating_capacity': seats
                }
            )
        self.stdout.write("Бренды созданы.")

    def create_vehicle(self, enterprises, brands):
        brand = random.choice(brands)
        enterprise = random.choice(enterprises)
        plate = fake.bothify(text='???###', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        if Vehicle.objects.filter(car_number=plate).exists():
            return None
        return Vehicle.objects.create(
            car_number=plate,
            price=fake.pydecimal(
                left_digits=8, right_digits=2, positive=True,
                min_value=800000, max_value=15000000
            ),
            year=fake.random_int(min=2015, max=2025),
            mileage=fake.random_int(min=5000, max=600000),
            fuel_type=random.choice([c[0] for c in Vehicle.FUEL_TYPE_CHOICES]),
            transmission=random.choice([c[0] for c in Vehicle.TRANSMISSION_CHOICES]),
            color=fake.color_name(),
            brand=brand,
            enterprise=enterprise
        )

    def create_driver(self, enterprises):
        enterprise = random.choice(enterprises)
        license = fake.bothify(text='?? ######', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        if Driver.objects.filter(license_number=license).exists():
            return None
        return Driver.objects.create(
            enterprise=enterprise,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            license_number=license,
            salary=fake.pydecimal(
                left_digits=6, right_digits=2, positive=True,
                min_value=40000, max_value=150000
            )
        )

    def assign_drivers(self, vehicles, drivers):
        active = 0

        for i in range(0, len(vehicles), 10):
            if i >= len(vehicles):
                break

            vehicle = vehicles[i]
            if DriverVehicle.objects.filter(vehicle=vehicle, is_active=True).exists():
                continue

            free_drivers = [d for d in drivers if not DriverVehicle.objects.filter(driver=d, is_active=True).exists()]
            if not free_drivers:
                continue

            DriverVehicle.objects.create(
                driver=random.choice(free_drivers), vehicle=vehicle, is_active=True
            )
            active += 1

        return active