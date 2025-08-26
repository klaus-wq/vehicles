from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets

from vehicle.models import Vehicle
from vehicle.serializers import VehicleSerializer


def index(request):
    return HttpResponse("Hello METANIT.COM")
# Create your views here.

class VehicleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint, который позволяет просматривать информацию об автомобилях.
    """
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer