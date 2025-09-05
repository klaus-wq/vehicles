from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets

from vehicle.models import Vehicle, Driver, Enterprise, DriverVehicle
from vehicle.serializers import VehicleSerializer, DriverSerializer, EnterpriseSerializer, DriverVehicleSerializer


def index(request):
    return HttpResponse("Hello METANIT.COM")
# Create your views here.

class VehicleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

class DriverViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer

class EnterpriseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Enterprise.objects.all()
    serializer_class = EnterpriseSerializer

class DriverVehicleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DriverVehicle.objects.all()
    serializer_class = DriverVehicleSerializer