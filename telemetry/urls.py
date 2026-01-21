from telemetry.views import TrackAPIView, TracksAPIView
from django.urls import path

app_name = "telemetry"

urlpatterns = [
    path('track/', TrackAPIView.as_view(), name='track'),
    path('tracks/', TracksAPIView.as_view(), name="tracks")
]