from django.db import models

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

    class Meta:
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'


    def __str__(self):
        return f'{self.year} г., {self.mileage} км., {self.color}, {self.price}, {self.get_fuel_type_display()}, {self.get_transmission_display()} {self.created_at}'
