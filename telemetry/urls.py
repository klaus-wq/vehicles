from telemetry.views import TrackAPIView, VehicleGPSPointViewSet
from django.urls import path

app_name = "telemetry"

urlpatterns = [
    path('track/', TrackAPIView.as_view(), name='track'),
    path('points/', VehicleGPSPointViewSet.as_view({'get': 'list'}), name='points'),
]