from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.http import Http404
from datetime import datetime
import pytz
from authentication.models import Manager
from vehicle.models import Vehicle
from vehicle.permissions import IsManagerOrReadOnly
from .models import TelemetryPoint, TelemetryTrip
from .serializers import TelemetryPointSerializer, TelemetryPointGeoSerializer, TripSerializer
from rest_framework import serializers as rest_serializers

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


