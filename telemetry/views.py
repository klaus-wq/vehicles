import folium
from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.http import Http404, HttpResponse, HttpResponseRedirect
from datetime import datetime
import pytz
from tablib import Dataset

from authentication.models import Manager
from vehicle.admin import EnterpriseResource, VehicleResource, TelemetryTripResource
from vehicle.models import Vehicle, Enterprise
from vehicle.permissions import IsManagerOrReadOnly
from .models import TelemetryPoint, TelemetryTrip
from .serializers import TelemetryPointSerializer, TelemetryPointGeoSerializer, TripSerializer
from rest_framework import serializers as rest_serializers

def prepare_response(dataset, format_str, prefix):
    if format_str == 'csv':
        content = dataset.csv
        content_type = 'text/csv; charset=utf-8'
        filename = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    else:
        content = dataset.json
        content_type = 'application/json; charset=utf-8'
        filename = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"

    response = HttpResponse(content, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

class EnterpriseExportView(APIView):
    permission_classes = [IsManagerOrReadOnly]

    def get(self, request):
        format = request.query_params.get('export_format', 'json').lower()
        if format not in ['csv', 'json']:
            return Response({"error": "Формат: csv или json"}, status=400)

        enterprise_id = request.query_params.get('enterprise_id')

        queryset = Enterprise.objects.all()
        if not request.user.is_superuser:
            try:
                manager = Manager.objects.get(user=request.user)
                allowed_ids = manager.enterprises.values_list('id', flat=True)
                queryset = queryset.filter(id__in=allowed_ids)
            except Manager.DoesNotExist:
                return Response({"error": "Профиль менеджера не найден"}, status=403)

        if enterprise_id:
            try:
                ids_list = [int(x.strip()) for x in enterprise_id.split(',')]
                queryset = queryset.filter(id__in=ids_list)
            except ValueError:
                return Response({"error": "Неверный формат enterprise_id"}, status=400)
        # if not request.user.is_superuser:
        #     manager = Manager.objects.get(user=self.request.user)
        #     queryset = queryset.filter(id__in=manager.enterprises.all())
        # if enterprise_id is not None:
        #     queryset = queryset.filter(id__in=enterprise_id)

        resource = EnterpriseResource()
        dataset = resource.export(queryset)

        return prepare_response(dataset, format, "enterprises")

class VehicleExportView(APIView):
    permission_classes = [IsManagerOrReadOnly]

    def get(self, request):
        format = request.query_params.get('export_format', 'json').lower()
        if format not in ['csv', 'json']:
            return Response({"error": "Формат: csv или json"}, status=400)

        enterprise_id = request.query_params.get('enterprise_id')
        vehicle_id = request.query_params.get('vehicle_id')

        queryset = Vehicle.objects.all()
        if vehicle_id is not None:
            queryset = queryset.filter(id=vehicle_id)
        if not request.user.is_superuser:
            manager = Manager.objects.get(user=self.request.user)
            queryset = queryset.filter(enterprise__in=manager.enterprises.all())
        if enterprise_id is not None:
            queryset = queryset.filter(enterprise__id=enterprise_id)

        resource = VehicleResource()
        dataset = resource.export(queryset)

        return prepare_response(dataset, format, "vehicles")

class TripExportView(APIView):
    permission_classes = [IsManagerOrReadOnly]

    def get(self, request):
        format = request.query_params.get('export_format', 'json').lower()
        if format not in ['csv', 'json']:
            return Response({"error": "Формат: csv или json"}, status=400)

        start = request.query_params.get('start')
        end = request.query_params.get('end')
        vehicle_id = request.query_params.get('vehicle_id')

        if not all([start, end]):
            return Response({"error": "Обязательны параметры start и end"}, status=400)

        try:
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)
        except ValueError:
            return Response({"error": "Неверный формат даты (ISO)"}, status=400)

        if start_dt >= end_dt:
            return Response({"error": "start должна быть раньше end"}, status=400)

        queryset = TelemetryTrip.objects.filter(
            start_time__gte=start,
            end_time__lte=end
        )
        if not request.user.is_superuser:
            manager = Manager.objects.get(user=self.request.user)
            queryset = queryset.filter(
                vehicle__enterprise__in=manager.enterprises.all()
            )

        if vehicle_id is not None:
            vehicle = Vehicle.objects.get(id=vehicle_id)
            queryset = queryset.filter(
                vehicle=vehicle,
            )

        if not queryset.exists():
            return Response({"message": "Нет поездок за период"}, status=200)

        resource = TelemetryTripResource()
        dataset = resource.export(queryset)

        return prepare_response(dataset, format, "trips")

def prepare_import_response(result, dataset):
    if result.has_errors():
        error_details = []

        if hasattr(result, 'error_rows') and result.error_rows:
            for row_result in result.error_rows:
                error_details.append(f"Ошибка в строке {row_result.number}: {row_result.errors}")

        for row_result in result.invalid_rows:
            row_num = row_result.number + 1
            row_errors = [f"{e.field or 'ошибка'}: {str(e.error)}" for e in row_result.errors]
            error_details.append(f"Строка {row_num}: {', '.join(row_errors)}")

        debug_info = {
            "total_rows": len(dataset),
            "result_totals": result.totals,
            "base_errors": str(result.base_errors) if hasattr(result, 'base_errors') else "нет",
        }

        return Response({
            "error": "Ошибки импорта",
            "details": error_details,
            "debug": debug_info
        }, status=400)

    return Response({
        "success": True,
        "new": result.totals.get('new', 0),
        "updated": result.totals.get('update', 0),
    }, status=201)

class VehicleImportView(APIView):
    permission_classes = [IsManagerOrReadOnly]

    def post(self, request):
        format = request.POST.get('import_format', 'json').lower()
        if format not in ['csv', 'json']:
            return Response({"error": "Формат: csv или json"}, status=400)
        if 'file' not in request.FILES:
            return Response({"error": "Нет файла"}, status=400)
        file = request.FILES['file']
        try:
            data = file.read().decode('utf-8')
        except UnicodeDecodeError:
            return Response({"error": "Неверная кодировка"}, status=400)
        dataset = Dataset()
        try:
            dataset.load(data, format)
        except Exception as e:
            return Response({"error": f"Неверные данные: {str(e)}"}, status=400)

        manager = None
        if not request.user.is_superuser:
            try:
                manager = request.user.manager
            except PermissionDenied:
                return Response({"error": "Нет прав"}, status=403)

        resource = VehicleResource(manager=manager)
        result = resource.import_data(dataset, dry_run=False)
        return prepare_import_response(result, dataset)

class TripImportView(APIView):
    permission_classes = [IsManagerOrReadOnly]

    def post(self, request):
        format = request.POST.get('import_format', 'json').lower()
        if format not in ['csv', 'json']:
            return Response({"error": "Формат: csv или json"}, status=400)
        if 'file' not in request.FILES:
            return Response({"error": "Нет файла"}, status=400)
        file = request.FILES['file']
        try:
            data = file.read().decode('utf-8')
        except UnicodeDecodeError:
            return Response({"error": "Неверная кодировка"}, status=400)
        dataset = Dataset()
        try:
            dataset.load(data, format)
        except Exception as e:
            return Response({"error": f"Неверные данные: {str(e)}"}, status=400)

        resource = TelemetryTripResource(user=request.user)
        result = resource.import_data(dataset)
        return prepare_import_response(result, dataset)

class EnterpriseImportView(APIView):
    permission_classes = [IsManagerOrReadOnly]

    def post(self, request):
        format = request.POST.get('import_format', 'json').lower()
        if format not in ['csv', 'json']:
            return Response({"error": "Формат: csv или json"}, status=400)
        if 'file' not in request.FILES:
            return Response({"error": "Нет файла"}, status=400)
        file = request.FILES['file']
        try:
            data = file.read().decode('utf-8')
        except UnicodeDecodeError:
            return Response({"error": "Неверная кодировка"}, status=400)
        dataset = Dataset()
        try:
            dataset.load(data, format)
        except Exception as e:
            return Response({"error": f"Неверные данные: {str(e)}"}, status=400)

        if not request.user.is_superuser:
            try:
                manager = request.user.manager
            except PermissionDenied:
                return Response({"error": "Нет прав"}, status=403)

        resource = EnterpriseResource()
        result = resource.import_data(dataset, dry_run=False)

        return prepare_import_response(result, dataset)

        # errors = []
        # error_count = 0
        # totals_new = 0
        # totals_update = 0
        # for row in dataset:
        #     try:
        #         name = row.get("name")
        #         city = row.get("city")
        #         phone = row.get("phone")
        #         address = row.get("address")
        #         enterprise_id = row.get("id")
        #         timezone = row.get("timezone", "UTC")
        #
        #         if not all([name, city, phone, address, timezone]):
        #             error_count += 1
        #             errors.append(f"Нет всех полей для {row}")
        #             continue
        #
        #         if Enterprise.objects.filter(id=enterprise_id).exists():
        #             enterprise = Enterprise.objects.get(id=enterprise_id)
        #             enterprise.name = name
        #             enterprise.city = city
        #             enterprise.phone = phone
        #             enterprise.address = address
        #             enterprise.timezone = timezone
        #             enterprise.save()
        #             totals_update += 1
        #         else:
        #             Enterprise.objects.create(
        #                 name=name,
        #                 city=city,
        #                 phone=phone,
        #                 address=address,
        #                 timezone=timezone,
        #             )
        #             totals_new += 1
        #     except Exception as e:
        #         error_count += 1
        #         errors.append(f"Ошибка при {row}: {str(e)}")
        #
        # if errors:
        #     return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
        # else:
        #     return Response(
        #         {"success": "Успешный импорт" + 'Новые:' + totals_new + 'Ошибок:' + error_count},
        #         status=status.HTTP_201_CREATED)

class EnterpriseImportFormView(LoginRequiredMixin, TemplateView):
    template_name = "import_form.html"
    extra_context = {'model_name': 'предприятий', 'url_name': 'telemetry:enterprises_import_api'}

class VehicleImportFormView(LoginRequiredMixin, TemplateView):
    template_name = "import_form.html"
    extra_context = {'model_name': 'машин', 'url_name': 'telemetry:vehicles_import_api'}

class TripImportFormView(LoginRequiredMixin, TemplateView):
    template_name = "import_form.html"
    extra_context = {'model_name': 'поездок', 'url_name': 'telemetry:trips_import_api'}

class TrackAPIView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrReadOnly]

    def get(self, request):
        vehicle_id = request.query_params.get('vehicle_id')
        start_str = request.query_params.get('start')
        end_str = request.query_params.get('end')
        output_format = request.query_params.get('output_format', 'json').lower()

        if not all([vehicle_id, start_str, end_str]):
            return Response(
                {"error": "Необходимые параметры: vehicle_id, start, end"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not request.user.is_superuser:
            try:
                manager = Manager.objects.get(user=request.user)
            except Manager.DoesNotExist:
                raise PermissionDenied()
            if not Vehicle.objects.filter(id=vehicle_id, enterprise__in=manager.enterprises.all()).exists():
                raise PermissionDenied("Нет доступа.")

        try:
            vehicle = Vehicle.objects.select_related('enterprise').get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            raise Http404("Автомобиль не найден.")

        enterprise_tz = vehicle.enterprise.timezone
        try:
            local_tz = pytz.timezone(enterprise_tz)
        except pytz.UnknownTimeZoneError:
            raise rest_serializers.ValidationError("Неверная таймзона предприятия.")

        try:
            start_local = datetime.fromisoformat(start_str)
            end_local = datetime.fromisoformat(end_str)
        except ValueError:
            raise rest_serializers.ValidationError("Неверный формат даты. YYYY-MM-DDTHH:MM:SS")

        if start_local >= end_local:
            raise rest_serializers.ValidationError("Начальная дата должна быть раньше, чем конечная.")

        start_utc = local_tz.localize(start_local).astimezone(pytz.UTC)
        end_utc = local_tz.localize(end_local).astimezone(pytz.UTC)

        points_qs = TelemetryPoint.objects.filter(
            vehicle=vehicle,
            timestamp__range=(start_utc, end_utc)
        )

        if output_format == 'geojson':
            points = points_qs.exclude(location__isnull=True)
        else:
            points = points_qs

        if not points.exists():
            raise Http404("Нет точек.")

        if output_format == 'geojson':
            serializer = TelemetryPointGeoSerializer(points, many=True)
        elif output_format == 'json':
            serializer = TelemetryPointSerializer(points, many=True)
        else:
            raise rest_serializers.ValidationError("Неверный формат.")

        return Response(serializer.data)

class TracksAPIView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrReadOnly]

    def get(self, request):
        vehicle_id = request.query_params.get('vehicle_id')
        start_str = request.query_params.get('start')
        end_str = request.query_params.get('end')
        output_format = request.query_params.get('output_format', 'json').lower()

        if not all([vehicle_id, start_str, end_str]):
            return Response(
                {"error": "Необходимые параметры: vehicle_id, start, end"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not request.user.is_superuser:
            try:
                manager = Manager.objects.get(user=request.user)
            except Manager.DoesNotExist:
                raise PermissionDenied()
            if not Vehicle.objects.filter(id=vehicle_id, enterprise__in=manager.enterprises.all()).exists():
                raise PermissionDenied("Нет доступа.")

        try:
            vehicle = Vehicle.objects.select_related('enterprise').get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            raise Http404("Автомобиль не найден.")

        enterprise_tz = pytz.timezone(vehicle.enterprise.timezone)
        try:
            start_local = datetime.fromisoformat(start_str)
            end_local = datetime.fromisoformat(end_str)
        except ValueError:
            raise rest_serializers.ValidationError("Неверный формат даты. YYYY-MM-DDTHH:MM:SS")

        if start_local >= end_local:
            raise rest_serializers.ValidationError("Начальная дата должна быть раньше, чем конечная.")

        try:
            start_utc = enterprise_tz.localize(start_local, is_dst=None).astimezone(pytz.utc)
            end_utc = enterprise_tz.localize(end_local, is_dst=None).astimezone(pytz.utc)
        except Exception as e:
            return Response(
                {"error": f"Ошибка таймзоны: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        telemetry_trips = TelemetryTrip.objects.filter(
            vehicle_id=vehicle_id,
            start_time__gte=start_utc,
            end_time__lte=end_utc,
        ).order_by('start_time')

        points = TelemetryPoint.objects.none()
        for telemetry_trip in telemetry_trips:
            points = points | TelemetryPoint.objects.filter(
                vehicle_id=vehicle_id,
                timestamp__gte=telemetry_trip.start_time,
                timestamp__lte=telemetry_trip.end_time)

        res_points = points.order_by("timestamp")
        print(res_points.query)

        if output_format == "geojson":
            return Response(TelemetryPointGeoSerializer(res_points, many=True).data["features"])
        elif output_format == 'json':
            return Response(TelemetryPointSerializer(res_points, many=True).data)
        else:
            raise rest_serializers.ValidationError("Неверный формат.")

class TripsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrReadOnly]

    def get(self, request):
        vehicle_id = request.query_params.get('vehicle_id')
        start_str = request.query_params.get('start')
        end_str = request.query_params.get('end')

        if not all([vehicle_id, start_str, end_str]):
            return Response(
                {"error": "Необходимые параметры: vehicle_id, start, end"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not request.user.is_superuser:
            try:
                manager = Manager.objects.get(user=request.user)
            except Manager.DoesNotExist:
                raise PermissionDenied()
            if not Vehicle.objects.filter(id=vehicle_id, enterprise__in=manager.enterprises.all()).exists():
                raise PermissionDenied("Нет доступа.")

        try:
            vehicle = Vehicle.objects.select_related('enterprise').get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            raise Http404("Автомобиль не найден.")

        enterprise_tz = pytz.timezone(vehicle.enterprise.timezone)
        try:
            start_local = datetime.fromisoformat(start_str)
            end_local = datetime.fromisoformat(end_str)
        except ValueError:
            raise rest_serializers.ValidationError("Неверный формат даты. YYYY-MM-DDTHH:MM:SS")

        if start_local >= end_local:
            raise rest_serializers.ValidationError("Начальная дата должна быть раньше, чем конечная.")

        try:
            start_utc = enterprise_tz.localize(start_local, is_dst=None).astimezone(pytz.utc)
            end_utc = enterprise_tz.localize(end_local, is_dst=None).astimezone(pytz.utc)
        except Exception as e:
            return Response(
                {"error": f"Ошибка таймзоны: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        telemetry_trips = TelemetryTrip.objects.filter(
            vehicle_id=vehicle_id,
            start_time__gte=start_utc,
            end_time__lte=end_utc,
        ).select_related('start_point', 'end_point', 'vehicle__enterprise').order_by('start_time')

        if not telemetry_trips.exists():
            return Response([], status=200)

        serializer = TripSerializer(
            telemetry_trips,
            many=True,
        )
        return Response(serializer.data)

class TripsMapView(LoginRequiredMixin, View):
    def post(self, request, enterprise_id, pk):
        enterprise = get_object_or_404(Enterprise, id=enterprise_id)

        if not request.user.is_superuser:
            try:
                manager = Manager.objects.get(user=request.user)
            except Manager.DoesNotExist:
                raise PermissionDenied()
            if enterprise not in manager.enterprises.all():
                raise PermissionDenied()
        trip_ids = request.POST.getlist('trip_ids')

        if not trip_ids:
            messages.error(request, "Выберите хотя бы одну поездку")
            return redirect('vehicle_detail', enterprise_id=enterprise_id, pk=pk)

        try:
            trip_ids = [int(tid) for tid in trip_ids]
        except ValueError:
            messages.error(request, "Некорректные идентификаторы поездок")
            return redirect('vehicle_detail', enterprise_id=enterprise_id, pk=pk)

        trips = TelemetryTrip.objects.filter(id__in=trip_ids)
        print(trips)

        m = folium.Map(tiles='openstreetmap')
        colors = ['blue', 'red', 'green', 'purple', 'orange', 'darkred', 'cadetblue']

        all_points = []

        for i, trip in enumerate(trips):
            points = list(TelemetryPoint.objects.filter(
                vehicle=trip.vehicle,
                timestamp__gte=trip.start_time,
                timestamp__lte=trip.end_time,
            ).order_by("timestamp"))
            print(points)
            if not points:
                continue

            coordinates = [(point.location.y, point.location.x) for point in points]
            all_points.extend(coordinates)

            color = colors[i % len(colors)]
            folium.PolyLine(
                coordinates,
                color=color,
                weight=4,
                opacity=0.8,
                tooltip=f"Поездка - {trip.id}: ({trip.start_time.strftime('%d.%m.%Y %H:%M')} - {trip.end_time.strftime('%d.%m.%Y %H:%M')})",
                popup=f"Поездка - {trip.id}: ({trip.start_time.strftime('%d.%m.%Y %H:%M')} - {trip.end_time.strftime('%d.%m.%Y %H:%M')})"
            ).add_to(m)

            if coordinates:
                folium.Marker(
                    coordinates[0],
                    popup=f"Начало поездки {trip.id}: {trip.start_time.strftime('%d.%m.%Y %H:%M')}",
                    icon=folium.Icon(color="green", icon="play")
                ).add_to(m)
                folium.Marker(
                    coordinates[-1],
                    popup=f"Конец поездки {trip.id}: {trip.end_time.strftime('%d.%m.%Y %H:%M')}",
                    icon=folium.Icon(color="red", icon="stop")
                ).add_to(m)

        if all_points:
            m.fit_bounds([[min(p[0] for p in all_points), min(p[1] for p in all_points)],
                          [max(p[0] for p in all_points), max(p[1] for p in all_points)]])

        return HttpResponse(m._repr_html_())