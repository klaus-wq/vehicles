from telemetry.views import TrackAPIView, TracksAPIView, TripsAPIView, EnterpriseExportView, \
    VehicleExportView, TripExportView, EnterpriseImportFormView, VehicleImportFormView, TripImportFormView, \
    EnterpriseImportView, VehicleImportView, TripImportView
from django.urls import path

from vehicle.models import Vehicle

app_name = "telemetry"

urlpatterns = [
    path('track/', TrackAPIView.as_view(), name='track'),
    path('tracks/', TracksAPIView.as_view(), name="tracks"),
    path('trips/', TripsAPIView.as_view(), name="tracks"),
    path("export/vehicles/", VehicleExportView.as_view(), name="vehicles_export"),
    path(
        "export/enterprises/",
        EnterpriseExportView.as_view(),
        name="enterprises_export",
    ),
    path(
        "export/trips/",
        TripExportView.as_view(),
        name="trips_export",
    ),
    path('import/enterprises/',EnterpriseImportFormView.as_view(), name='enterprises_import'),
    path('import/vehicles/', VehicleImportFormView.as_view(), name='vehicles_import'),
    path('import/trips/', TripImportFormView.as_view(), name='trips_import'),
    path('api/import/enterprises/', EnterpriseImportView.as_view(), name='enterprises_import_api'),
    path('api/import/vehicles/', VehicleImportView.as_view(), name='vehicles_import_api'),
    path('api/import/trips/', TripImportView.as_view(), name='trips_import_api'),
]