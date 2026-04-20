# reports/serializers.py
from rest_framework import serializers
from .models import Report


class ReportGenerateRequestSerializer(serializers.Serializer):
    report_type = serializers.ChoiceField(
        choices=[key for key, _ in Report.REPORT_TYPES],
        required=True,
        help_text="Тип отчёта: MILEAGE, TRIPS_COUNT, DRIVER_ASSIGNMENT"
    )
    name = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text="Название отчёта (для сохранения)"
    )
    period = serializers.ChoiceField(
        choices=[key for key, _ in Report.PERIOD_CHOICES],
        default='DAY',
        help_text="Гранулярность: DAY, MONTH, YEAR"
    )
    start_date = serializers.DateTimeField(required=True)
    end_date = serializers.DateTimeField(required=True)

    vehicle_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=[],
        help_text="Список ID автомобилей"
    )
    enterprise_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="ID предприятия"
    )

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Начальная дата не может быть позже конечной")
        return data

class ReportResponseSerializer(serializers.Serializer):
    report_id = serializers.IntegerField(read_only=True, allow_null=True)
    report_type = serializers.CharField()
    period = serializers.CharField()
    unit = serializers.CharField()
    generated_at = serializers.DateTimeField(read_only=True)
    data = serializers.DictField()
    summary = serializers.DictField(required=False)
