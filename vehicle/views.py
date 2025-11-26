from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, ProtectedError
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from django.views.decorators.csrf import csrf_protect
from django.views.generic import ListView, TemplateView, CreateView
from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import OrderingFilter
from authentication.models import Manager
from vehicle.models import Vehicle, Driver, Enterprise, DriverVehicle
from vehicle.permissions import IsManagerOrReadOnly
from vehicle.serializers import VehicleSerializer, DriverSerializer, EnterpriseSerializer, DriverVehicleSerializer
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

def index(request):
    return HttpResponse("Hello")

class StandardPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 3000

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsManagerOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ['color', 'car_number', 'price', 'year']
    ordering = 'color'

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

    def get_object(self):
        obj = get_object_or_404(Enterprise, pk=self.kwargs['pk'])

        user = self.request.user
        if user.is_superuser:
            return obj

        if not hasattr(user, 'manager'):
            raise PermissionDenied("Доступ запрещён.")

        manager = user.manager
        if obj not in manager.enterprises.all():
            raise PermissionDenied("Доступ запрещён.")

        return obj

    def create(self, request, *args, **kwargs):
        if not (request.user.is_superuser or hasattr(request.user, 'manager')):
            return Response(
                {"detail": "Нужно быть менеджером или админом, чтобы создать предприятия."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        enterprise = serializer.save()

        if not request.user.is_superuser and hasattr(request.user, 'manager'):
            manager = request.user.manager
            manager.enterprises.add(enterprise)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def delete(self, request, *args, **kwargs):
        if not (request.user.is_superuser or hasattr(request.user, 'manager')):
            return Response(
                {"detail": "У вас нет прав для удаления предприятий."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        enterprise = self.get_object()

        if enterprise.managers.count() > 1:
            return Response(
                {"detail": "Нельзя удалить предприятие, видимое другим менеджерам."},
                status=status.HTTP_409_CONFLICT
            )

        if enterprise.vehicles.exists() or enterprise.drivers.exists():
            return Response(
                {"detail": "Нельзя удалить предприятие с автомобилями или водителями."},
                status=status.HTTP_409_CONFLICT
            )

        return super().destroy(request, *args, **kwargs)

class DriverVehicleViewSet(viewsets.ModelViewSet):
    queryset = DriverVehicle.objects.all()
    serializer_class = DriverVehicleSerializer

class EnterprisesListViewSet(LoginRequiredMixin, ListView):
    model = Enterprise
    template_name = 'enterprises.html'
    context_object_name = 'enterprises'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            try:
                manager = request.user.manager
                if not manager.enterprises.exists():
                    raise PermissionDenied("Нет привязанных предприятий")
            except AttributeError:
                raise PermissionDenied("Профиль менеджера не найден")

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.is_superuser:
            qs = Enterprise.objects.all()
        else:
            qs = self.request.user.manager.enterprises.all()

        return qs.annotate(
            vehicle_count=Count('vehicles'),
            driver_count=Count('drivers')
        )

    # def get_queryset(self):
    #     user = self.request.user
    #
    #     if user.is_superuser:
    #         return Enterprise.objects.all()
    #
    #     try:
    #         manager = user.manager
    #         print(manager.enterprises.all())
    #         return manager.enterprises.all()
    #     except (Manager.DoesNotExist, AttributeError):
    #         return Enterprise.objects.none()

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     for enterprise in context['enterprises']:
    #         enterprise.vehicle_count = enterprise.vehicles.count()
    #         enterprise.driver_count = enterprise.drivers.count()
    #     return context

class EnterpriseCreateView(APIView):
    permission_classes = [IsManagerOrReadOnly]

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

class VehicleListView(LoginRequiredMixin, ListView):
    template_name = 'vehicle_list.html'
    context_object_name = 'vehicles'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        self.enterprise = get_object_or_404(Enterprise, id=self.kwargs['enterprise_id'])
        if not request.user.is_superuser:
            if not request.user.manager.enterprises.filter(id=self.enterprise.id).exists():
                raise PermissionDenied("Доступ запрещён")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Vehicle.objects.filter(enterprise=self.enterprise)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enterprise'] = self.enterprise
        return context

# class VehicleForm(forms.ModelForm):
#     class Meta:
#         model = Vehicle
#         fields = '__all__'

class VehicleFormView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Vehicle
    fields = ['car_number', 'brand', 'year', 'mileage', 'color', 'price', 'fuel_type', 'transmission']
    template_name = 'vehicle_form.html'
    success_message = "Машина успешно сохранена!"

    def dispatch(self, request, *args, **kwargs):
        self.enterprise = get_object_or_404(Enterprise, id=self.kwargs['enterprise_id'])
        # Проверка прав
        if not request.user.is_superuser:
            if self.enterprise not in request.user.manager.enterprises.all():
                raise PermissionDenied("Доступ запрещён")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enterprise'] = self.enterprise
        context['title'] = 'Редактировать машину' if self.object else 'Добавить машину'
        return context

    def form_valid(self, form):
        form.instance.enterprise = self.enterprise
        messages.success(self.request, f"Машина {form.instance.car_number} сохранена!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('vehicle_list', kwargs={'enterprise_id': self.enterprise.id})

class VehicleUpdateView(VehicleFormView, UpdateView):
    success_message = "Машина успешно обновлена!"

class VehicleDeleteView(LoginRequiredMixin, DeleteView):
    model = Vehicle
    template_name = 'vehicle_confirm_delete.html'

    def get_queryset(self):
        return Vehicle.objects.filter(enterprise_id=self.kwargs['enterprise_id'])

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not self.request.user.is_superuser:
            if obj.enterprise not in self.request.user.manager.enterprises.all():
                raise PermissionDenied("Доступ запрещён")
        return obj

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        car_number = self.object.car_number

        try:
            self.object.delete()  # пытаемся удалить
            messages.success(request, f"Машина {car_number} успешно удалена!")
            return redirect(self.get_success_url())

        except ProtectedError:
            messages.error(
                request,
                format_html(
                    "Нельзя удалить машину <strong>{}</strong> — "
                    "к ней привязаны водители. Сначала отвяжите их.",
                    car_number
                )
            )
            return redirect('vehicle_list', enterprise_id=self.object.enterprise.id)

    # def delete(self, request, *args, **kwargs):
    #     vehicle = self.get_object()
    #     car_number = vehicle.car_number  # ← сохраняем номер до удаления
    #     messages.success(request, f"Машина {car_number} успешно удалена!")
    #     return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('vehicle_list', kwargs={'enterprise_id': self.kwargs['enterprise_id']})