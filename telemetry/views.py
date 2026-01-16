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
from .models import TelemetryPoint
from .serializers import TelemetryPointSerializer, TelemetryPointGeoSerializer, GeoJSONVehicleGPSPointSerializer, \
    VehicleGPSPointSerializer
from rest_framework import serializers as rest_serializers

class VehicleGPSPointViewSet(viewsets.ViewSet):

    permission_classes = [
        IsAuthenticated,
        IsManagerOrReadOnly,
    ]

    def list(self, request):
        vehicle_id = request.query_params.get("vehicle_id", None)
        start_date = request.query_params.get("start_date", None)
        end_date = request.query_params.get("end_date", None)
        output_format = request.query_params.get("output_format", "geojson")

        if vehicle_id is None:
            raise rest_serializers.ValidationError(
                "'vehicle_id' parameter is required"
            )
        if start_date is None:
            raise rest_serializers.ValidationError(
                "'start_date' parameter is required"
            )
        if end_date is None:
            raise rest_serializers.ValidationError(
                "'end_date' parameter is required"
            )
        if start_date > end_date:
            raise rest_serializers.ValidationError(
                "'start_date' cant be greater than 'end_date'"
            )

        if not request.user.is_superuser:
            manager = Manager.objects.get(user=self.request.user)
            is_belong_to_manager = Vehicle.objects.filter(
                id=vehicle_id, enterprise__in=manager.enterprises.all()
            ).exists()
            if not is_belong_to_manager:
                raise PermissionDenied(
                    detail="You do not have permission to access this object."
                )

        current_points = TelemetryPoint.objects.filter(
            vehicle_id=vehicle_id,
            timestamp__date__gte=start_date,
            timestamp__date__lte=end_date,
        )
        print(current_points, output_format)
        if output_format == "json":
            data = VehicleGPSPointSerializer(current_points, many=True).data
        else:
            print('geojson')
            data = GeoJSONVehicleGPSPointSerializer(
                current_points, many=True
            ).data
        return Response(data)

class TrackAPIView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrReadOnly]

    def get(self, request):
        vehicle_id = request.query_params.get('vehicle_id')
        start_str = request.query_params.get('start')
        end_str = request.query_params.get('end')
        output_format = request.query_params.get('output_format', 'json').lower()

        if not all([vehicle_id, start_str, end_str]):
            return Response(
                {"error": "Required parameters: vehicle_id, start, end"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not request.user.is_superuser:
            try:
                manager = Manager.objects.get(user=request.user)
            except Manager.DoesNotExist:
                raise PermissionDenied()
            if not Vehicle.objects.filter(
                id=vehicle_id,
                enterprise__in=manager.enterprises.all()
            ).exists():
                raise PermissionDenied("You do not have permission to access this vehicle.")

        try:
            vehicle = Vehicle.objects.select_related('enterprise').get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            raise Http404("Vehicle not found")

        enterprise_tz = vehicle.enterprise.timezone
        try:
            local_tz = pytz.timezone(enterprise_tz)
        except pytz.UnknownTimeZoneError:
            raise rest_serializers.ValidationError("Enterprise has invalid timezone")

        # Парсим даты как локальные (naive) в таймзоне предприятия
        try:
            start_local = datetime.fromisoformat(start_str)
            end_local = datetime.fromisoformat(end_str)
        except ValueError:
            raise rest_serializers.ValidationError(
                "Invalid date format. Use ISO format: YYYY-MM-DDTHH:MM:SS"
            )

        if start_local >= end_local:
            raise rest_serializers.ValidationError("'start' must be earlier than 'end'")

        # Конвертируем в UTC для запроса к БД (где хранится UTC)
        start_utc = local_tz.localize(start_local).astimezone(pytz.UTC)
        end_utc = local_tz.localize(end_local).astimezone(pytz.UTC)

        # Запрос точек
        points_qs = TelemetryPoint.objects.filter(
            vehicle=vehicle,
            timestamp__range=(start_utc, end_utc)
        )

        if output_format == 'geojson':
            points = points_qs.exclude(location__isnull=True)
        else:
            points = points_qs

        if not points.exists():
            raise Http404("No telemetry points found for the given parameters")

        if output_format == 'geojson':
            serializer = TelemetryPointGeoSerializer(points, many=True)
        elif output_format == 'json':
            serializer = TelemetryPointSerializer(points, many=True)
        else:
            raise rest_serializers.ValidationError("Invalid format. Use 'json' or 'geojson'")

        return Response(serializer.data)