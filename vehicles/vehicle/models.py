from django.db import models

class Brand(models.Model):
    VEHICLE_TYPE_CHOICES = [
        ('car', 'Легковой'),
        ('truck', 'Грузовой'),
        ('bus', 'Автобус'),
        ('motorcycle', 'Мотоцикл'),
    ]

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
        return f'{self.name}, {self.get_vehicle_type_display()}, {self.fuel_tank_capacity} л., {self.cargo_capacity} кг., {self.seating_capacity}'

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
        verbose_name='Уникальный идентификатор'
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
        null=True,
        verbose_name='Бренд'
    )

    class Meta:
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'


    def __str__(self):
        return f'{self.id}, {self.brand}, {self.year} г., {self.mileage} км., {self.color}, {self.price}, {self.get_fuel_type_display()}, {self.get_transmission_display()}'