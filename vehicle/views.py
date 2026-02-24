from datetime import datetime

import pytz
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Count, ProtectedError
from django import forms
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.utils import timezone
from django.utils.html import format_html
from django.views.generic import ListView, TemplateView, CreateView, DetailView
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import OrderingFilter
from authentication.models import Manager
from telemetry.models import TelemetryTrip
from telemetry.serializers import TripSerializer
from vehicle.admin import EnterpriseResource, VehicleResource, TelemetryTripResource
from vehicle.models import Vehicle, Driver, Enterprise, DriverVehicle, Brand
from vehicle.permissions import IsManagerOrReadOnly
from vehicle.serializers import VehicleSerializer, DriverSerializer, EnterpriseSerializer, DriverVehicleSerializer
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
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

class EnterpriseUpdateView(LoginRequiredMixin, UpdateView):
    model = Enterprise
    fields = ['name', 'city', 'address', 'phone', 'timezone']
    template_name = 'enterprise_form.html'
    success_url = None

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Enterprise.objects.all()
        return self.request.user.manager.enterprises.all()

    def get_success_url(self):
        return reverse('enterprises_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['enterprise'] = self.object
        tz_name = self.object.timezone or 'UTC'
        context['now_in_enterprise_tz'] = timezone.now().astimezone(pytz.timezone(tz_name))
        print(f"DEBUG: tz_name = {tz_name}, now_tz = {context['now_in_enterprise_tz']}")
        common = pytz.common_timezones
        now = timezone.now()
        timezone_choices = []
        for tz in common:
            try:
                offset = now.astimezone(pytz.timezone(tz)).utcoffset()
                hours = int(offset.total_seconds() // 3600)
                sign = "+" if hours >= 0 else ""
                offset_str = f"UTC{sign}{hours:02d}:00"
                timezone_choices.append({
                    'value': tz,
                    'label': f"{tz} ({offset_str})"
                })
            except Exception:
                timezone_choices.append({'value': tz, 'label': tz})

        timezone_choices.sort(key=lambda x: x['value'])

        context['timezone_choices'] = timezone_choices
        return context

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
        return Vehicle.objects.none()
    #     return Vehicle.objects.filter(enterprise=self.enterprise)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enterprise'] = self.enterprise

        queryset = Vehicle.objects.filter(enterprise=self.enterprise)
        paginator = Paginator(queryset, self.paginate_by)
        page_obj = paginator.get_page(self.request.GET.get('page'))

        serializer = VehicleSerializer(page_obj.object_list, many=True)
        context['vehicles_json'] = serializer.data
        print(context['vehicles_json'][0])
        context['page_obj'] = page_obj
        context['is_paginated'] = page_obj.has_other_pages()

        return context


class VehicleFormView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Vehicle
    fields = ['car_number', 'purchase_datetime', 'brand', 'year', 'mileage', 'color', 'price', 'fuel_type', 'transmission', 'enterprise']
    template_name = 'vehicle_form.html'
    success_message = "Машина успешно сохранена!"

    def dispatch(self, request, *args, **kwargs):
        self.enterprise_from_url = get_object_or_404(Enterprise, id=self.kwargs['enterprise_id'])

        if not request.user.is_superuser:
            if self.enterprise_from_url not in request.user.manager.enterprises.all():
                raise PermissionDenied("Доступ запрещён")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Vehicle.objects.filter(enterprise=self.enterprise_from_url)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        tz = pytz.timezone(self.enterprise_from_url.timezone or 'UTC')

        form.fields['fuel_type'].empty_label = None
        form.fields['transmission'].empty_label = None

        if self.object:
            if 'enterprise' in form.fields:
                del form.fields['enterprise']

        else:
            if not self.request.user.is_superuser:
                queryset = self.request.user.manager.enterprises.all()
            else:
                queryset = Enterprise.objects.all()

            form.fields['enterprise'].queryset = queryset
            form.fields['enterprise'].empty_label = None
            form.fields['enterprise'].required = True

            form.fields['fuel_type'].initial = 'petrol'
            form.fields['transmission'].initial = 'automatic'

        if self.object and self.object.purchase_datetime:
            localized = self.object.purchase_datetime.astimezone(tz)
            form.initial['purchase_datetime'] = localized.strftime('%Y-%m-%dT%H:%M')
        else:
            # при создании — текущее время в зоне предприятия
            now_local = timezone.now().astimezone(tz)
            form.initial['purchase_datetime'] = now_local.strftime('%Y-%m-%dT%H:%M')

        return form

    def form_valid(self, form):
        purchase_dt = form.cleaned_data.get('purchase_datetime')
        if purchase_dt:
            tz = pytz.timezone(self.enterprise_from_url.timezone or 'UTC')
            aware_local = tz.localize(purchase_dt)  # делаем aware в зоне предприятия
            form.instance.purchase_datetime = aware_local.astimezone(pytz.UTC)

        form.instance.enterprise = self.enterprise_from_url
        messages.success(self.request, f"Машина {form.instance.car_number} успешно сохранена!")
        return super().form_valid(form)

    # def get_form(self, form_class=None):
    #     form = super().get_form(form_class)
    #
    #     form.fields['fuel_type'].empty_label = None
    #     form.fields['transmission'].empty_label = None
    #
    #     if self.object:
    #         if 'enterprise' in form.fields:
    #             del form.fields['enterprise']
    #
    #     else:
    #         if not self.request.user.is_superuser:
    #             queryset = self.request.user.manager.enterprises.all()
    #         else:
    #             queryset = Enterprise.objects.all()
    #
    #         form.fields['enterprise'].queryset = queryset
    #         form.fields['enterprise'].empty_label = None
    #         form.fields['enterprise'].required = True
    #
    #         form.fields['fuel_type'].initial = 'petrol'
    #         form.fields['transmission'].initial = 'automatic'
    #
    #     return form

    def get_initial(self):
        initial = super().get_initial()
        if not self.object:
            initial['enterprise'] = self.enterprise_from_url
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enterprise'] = self.enterprise_from_url
        context['title'] = 'Редактировать машину' if self.object else 'Добавить машину'
        return context

    # def form_valid(self, form):
    #     form.instance.enterprise = self.enterprise_from_url
    #     messages.success(self.request, f"Машина {form.instance.car_number} успешно сохранена!")
    #     return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('vehicle_list', kwargs={'enterprise_id': self.enterprise_from_url.id})

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

class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Дата начала"
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Дата окончания"
    )

class VehicleDetailView(LoginRequiredMixin, DetailView):
    template_name = "vehicle_detail.html"
    permission_classes = [IsManagerOrReadOnly]
    context_object_name = "vehicle"

    def dispatch(self, request, *args, **kwargs):
        self.enterprise = get_object_or_404(Enterprise, id=self.kwargs['enterprise_id'])
        if not request.user.is_superuser:
            if not request.user.manager.enterprises.filter(id=self.enterprise.id).exists():
                raise PermissionDenied("Доступ запрещён")
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(
            Vehicle,
            id=self.kwargs["pk"],
            enterprise=self.enterprise
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicle = self.object

        context["enterprise"] = self.enterprise
        context['drivers_json'] = vehicle.vehicle_drivers.select_related("driver")

        form = DateRangeForm(self.request.GET)
        start_date = form['start_date'].value() if form.is_valid() else None
        end_date = form['end_date'].value() if form.is_valid() else None

        trips = vehicle.trips.all()
        if start_date:
            trips = trips.filter(start_time__gte=start_date)
        if end_date:
            trips = trips.filter(start_time__lte=end_date)

        trips_serialized = TripSerializer(
            trips,
            many=True
        ).data

        context["trips"] = trips_serialized
        context["date_form"] = form

        return context

class BrandListView(LoginRequiredMixin, ListView):
    model = Brand
    template_name = 'brand_list.html'
    context_object_name = 'object_list'

class BrandCreateView(LoginRequiredMixin, CreateView):
    model = Brand
    fields = '__all__'
    template_name = 'brand_form.html'
    success_url = reverse_lazy('brands_list')

class BrandUpdateView(BrandCreateView, UpdateView):
    pass

class BrandDeleteView(LoginRequiredMixin, DeleteView):
    model = Brand
    template_name = 'brand_confirm_delete.html'
    success_url = reverse_lazy('brands_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        brand = self.get_object()

        vehicles = brand.vehicle_set.all().order_by('car_number')

        paginator = Paginator(vehicles, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['protected_objects'] = page_obj
        context['page_obj'] = page_obj
        context['is_paginated'] = page_obj.has_other_pages()

        return context

    def delete(self, request, *args, **kwargs):
        try:
            response = super().delete(request, *args, **kwargs)
            messages.success(request, f"Бренд «{self.object.name}» успешно удалён.")
            return response
        except ProtectedError:
            return self.get(request, *args, **kwargs)