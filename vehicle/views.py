from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import ListView, TemplateView
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import Manager
from vehicle.models import Vehicle, Driver, Enterprise, DriverVehicle
from vehicle.permissions import IsManagerOrReadOnly
from vehicle.serializers import VehicleSerializer, DriverSerializer, EnterpriseSerializer, DriverVehicleSerializer

def index(request):
    return HttpResponse("Hello METANIT.COM")
# Create your views here.

class VehicleViewSet(viewsets.ModelViewSet):
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

class DriverViewSet(viewsets.ModelViewSet):
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

class EnterpriseViewSet(viewsets.ModelViewSet):
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

class DriverVehicleViewSet(viewsets.ModelViewSet):
    queryset = DriverVehicle.objects.all()
    serializer_class = DriverVehicleSerializer

class EnterprisesListViewSet(LoginRequiredMixin, ListView):
    model = Enterprise
    template_name = 'enterprises.html'
    context_object_name = 'enterprises'

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Enterprise.objects.all()

        try:
            manager = user.manager
            return manager.enterprises.all()
        except (Manager.DoesNotExist, AttributeError):
            return Enterprise.objects.none()

class EnterpriseCreateApiView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrReadOnly]

    def post(self, request, format=None):
        if not request.user.is_superuser:
            return Response(
                {"detail": "У вас нет прав для создания предприятий."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = EnterpriseSerializer(data=request.data)
        if serializer.is_valid():
            enterprise = serializer.save()
            response_data = serializer.data

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EnterpriseCreateFormView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'enterprise_create.html'