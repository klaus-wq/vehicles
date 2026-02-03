from telemetry.views import TrackAPIView, TracksAPIView, TripsAPIView
from django.urls import path

app_name = "telemetry"

urlpatterns = [
    path('track/', TrackAPIView.as_view(), name='track'),
    path('tracks/', TracksAPIView.as_view(), name="tracks"),
    path('trips/', TripsAPIView.as_view(), name="tracks")
]