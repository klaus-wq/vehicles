from django.core.exceptions import ValidationError
from django.db import models

class Enterprise(models.Model):
    id = models.AutoField(
        primary_key=True,
        unique=True,
        verbose_name='Уникальный идентификатор'
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Название предприятия'
    )
    city = models.CharField(
        max_length=100,
        verbose_name='Город'
    )
    address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Адрес'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Телефон'
    )

    class Meta:
        verbose_name = 'Предприятие'
        verbose_name_plural = 'Предприятия'

    def __str__(self):
        return f'{self.id}, {self.name}, {self.city}, {self.address}, {self.phone}'

class Driver(models.Model):
    enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.CASCADE,
        verbose_name='Предприятие',
        related_name='drivers'
    )
    first_name = models.CharField(
        max_length=50,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=50,
        verbose_name='Фамилия'
    )
    license_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Номер водительского удостоверения'
    )
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Заработная плата, ₽'
    )
    vehicles = models.ManyToManyField(
        'Vehicle',
        through='DriverVehicle',
        related_name='driver_vehicles',
        verbose_name='автомобили'
    )

    class Meta:
        verbose_name = 'Водитель'
        verbose_name_plural = 'Водители'

    def __str__(self):
        vehicles_list = ", ".join([f"{vehicle.id} {vehicle.car_number}" for vehicle in self.vehicles.all()])
        return f'{self.id}, {self.last_name} {self.first_name}, {self.enterprise.name}, {vehicles_list}'

    def save(self, *args, **kwargs):
        if self.pk:
            original = Driver.objects.get(pk=self.pk)
            if original.enterprise != self.enterprise and self.vehicles.exists():
                raise ValidationError(
                    "Нельзя изменить предприятие, если водителю назначен автомобиль."
                )
        super().save(*args, **kwargs)


class Brand(models.Model):
    VEHICLE_TYPE_CHOICES = [
        ('noname', 'noname'),
        ('car', 'Легковой'),
        ('truck', 'Грузовой'),
        ('bus', 'Автобус'),
        ('motorcycle', 'Мотоцикл'),
    ]

    id = models.PositiveIntegerField(
        primary_key=True,
        verbose_name='Уникальный идентификатор'
    )
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Название бренда'
    )
    vehicle_type = models.CharField(
        max_length=20,
        choices=VEHICLE_TYPE_CHOICES,
        verbose_name='Тип транспорта'
    )
    fuel_tank_capacity = models.PositiveSmallIntegerField(
        verbose_name='Объем бака, л'
    )
    cargo_capacity = models.PositiveSmallIntegerField(
        verbose_name='Грузоподъемность, кг',
        null=True,
        blank=True
    )
    seating_capacity = models.PositiveSmallIntegerField(
        verbose_name='Количество мест'
    )

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'

    def __str__(self):
        return f'{self.id}, {self.name}, {self.get_vehicle_type_display()}, {self.fuel_tank_capacity} л., {self.cargo_capacity} кг., {self.seating_capacity}'

class Vehicle(models.Model):
    FUEL_TYPE_CHOICES = [
        ('gasoline', 'Бензин'),
        ('diesel', 'Дизель'),
        ('electric', 'Электро'),
        ('hybrid', 'Гибрид'),
        ('gas', 'Газ'),
    ]

    TRANSMISSION_CHOICES = [
        ('manual', 'Механическая'),
        ('automatic', 'Автоматическая'),
        ('robot', 'Роботизированная'),
        ('variator', 'Вариатор'),
    ]

    id = models.AutoField(
        primary_key=True,
        unique=True,
        verbose_name='Уникальный идентификатор'
    )
    car_number = models.CharField(
        max_length=15,
        unique=True,
        verbose_name='Государственный номер',
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Стоимость, ₽'
    )
    year = models.PositiveSmallIntegerField(
        verbose_name='Год выпуска'
    )
    mileage = models.PositiveIntegerField(
        verbose_name='Пробег, км'
    )
    fuel_type = models.CharField(
        max_length=20,
        choices=FUEL_TYPE_CHOICES,
        verbose_name='Тип топлива'
    )
    transmission = models.CharField(
        max_length=20,
        choices=TRANSMISSION_CHOICES,
        verbose_name='Коробка передач'
    )
    color = models.CharField(
        max_length=50,
        verbose_name='Цвет'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )
    brand = models.ForeignKey(
        'Brand',
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        default=1,
        verbose_name='Бренд'
    )
    enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.CASCADE,
        verbose_name='Предприятие',
        related_name='vehicles'
    )
    drivers = models.ManyToManyField(
        Driver,
        through='DriverVehicle',
        related_name='vehicle_drivers',
        verbose_name='водители'
    )

    class Meta:
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'

    def __str__(self):
        drivers_list = ", ".join([f"{driver.last_name} {driver.first_name}" for driver in self.drivers.all()])
        return f'{self.id}, {self.car_number}, {self.enterprise.name}, {drivers_list}'
        # return f'{self.id}, {self.enterprise}, {self.drivers}, {self.car_number}, {self.brand}, {self.year} г., {self.mileage} км., {self.color}, {self.price}, {self.get_fuel_type_display()}, {self.get_transmission_display()}'

    def save(self, *args, **kwargs):
        if self.pk:
            original = Vehicle.objects.get(pk=self.pk)
            if (original.enterprise != self.enterprise and self.drivers.exists()):
                raise ValidationError(
                    "Нельзя изменить предприятие, если автомобилю назначены водители."
                )
        super().save(*args, **kwargs)

class DriverVehicle(models.Model):
    driver = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        verbose_name='Водитель',
        related_name='driver_vehicles'
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        verbose_name='Автомобиль',
        related_name='vehicle_drivers'
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name='Активный водитель'
    )

    class Meta:
        verbose_name = 'Назначение водителя автомобилю'
        verbose_name_plural = 'Назначения водителей автомобилям'
        unique_together = [
            ('driver', 'vehicle'),  # Один водитель не может быть назначен одному автомобилю дважды
        ]
        constraints = [
            #Один водитель может быть основным только для одного автомобиля
            models.UniqueConstraint(
                fields=['driver'],
                condition=models.Q(is_active=True),
                name='unique_active_driver'
            ),
            #Один автомобиль может иметь только одного основного водителя
            models.UniqueConstraint(
                fields=['vehicle'],
                condition=models.Q(is_active=True),
                name='unique_active_vehicle'
            ),
        ]

    def __str__(self):
        status = 'основной' if self.is_active else 'дополнительный'
        return f'{self.driver.id}, {self.driver.first_name} {self.driver.last_name} ({status}) → {self.vehicle.id}, {self.vehicle.car_number} '

    def clean(self):
        #Автомобиль и водитель должны принадлежать одному и тому же предприятию
        if self.driver.enterprise != self.vehicle.enterprise:
            raise ValidationError(
                ("Автомобиль и водитель должны принадлежать одному и тому же предприятию")
            )

        #Проверка, что водитель не назначен активным на другой автомобиль
        if self.is_active and DriverVehicle.objects.filter(
                driver=self.driver,
                is_active=True
        ).exclude(pk=self.pk).exists():
            raise ValidationError(
                ("Данный водитель уже назначен активным для другого автомобиля")
            )

        #Проверка, что у автомобиля не назначен другой активный водитель
        if self.is_active and DriverVehicle.objects.filter(
                vehicle=self.vehicle,
                is_active=True
        ).exclude(pk=self.pk).exists():
            raise ValidationError(
                ("У данного автомобиля уже назначен активный водитель")
            )

    def save(self, *args, **kwargs):
        self.full_clean()  # Вызываем проверку перед сохранением
        super().save(*args, **kwargs)