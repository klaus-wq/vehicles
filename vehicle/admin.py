from django.contrib import admin

from .models import Vehicle, Brand, Enterprise, Driver, DriverVehicle
admin.site.register(Brand)
admin.site.register(Enterprise)
admin.site.register(Driver)
admin.site.register(Vehicle)
admin.site.register(DriverVehicle)