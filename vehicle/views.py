from django.shortcuts import render
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import viewsets

from vehicle.models import Vehicle, Driver, Enterprise, DriverVehicle, Manager
from vehicle.permissions import IsManagerOrReadOnly
from vehicle.serializers import VehicleSerializer, DriverSerializer, EnterpriseSerializer, DriverVehicleSerializer

def index(request):
    return HttpResponse("Hello METANIT.COM")
# Create your views here.

class VehicleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsManagerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Vehicle.objects.all()
        try:
            manager = self.request.user.manager
            return Vehicle.objects.filter(enterprise__in=manager.enterprises.all())
        except (Manager.DoesNotExist, AttributeError):
            return Vehicle.objects.none()

class DriverViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [IsManagerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Driver.objects.all()
        try:
            manager = self.request.user.manager
            return Driver.objects.filter(enterprise__in=manager.enterprises.all())
        except (Manager.DoesNotExist, AttributeError):
            return Driver.objects.none()

@method_decorator(csrf_protect, name='dispatch')
class EnterpriseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Enterprise.objects.all()
    serializer_class = EnterpriseSerializer
    permission_classes = [IsManagerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        print(f"Запрос от пользователя: {user.username}")

        if user.is_superuser:
            return Enterprise.objects.all()
        try:
            manager = user.manager
            print(f"Найден менеджер: {manager}")

            enterprises = manager.enterprises.all()
            print(f"Предприятия менеджера: {[e.name for e in enterprises]}")
            return enterprises
        except (Manager.DoesNotExist, AttributeError) as e:
            print(f"Ошибка получения менеджера: {e}")
            return Enterprise.objects.none()

class DriverVehicleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DriverVehicle.objects.all()
    serializer_class = DriverVehicleSerializer