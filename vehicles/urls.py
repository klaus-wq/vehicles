"""
URL configuration for vehicles project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from rest_framework import routers

from authentication.views import CustomLoginView
from telemetry.views import TripsMapView
from vehicle.exceptions import custom_handler403, custom_handler401, custom_handler500
from vehicle.views import VehicleViewSet, DriverViewSet, EnterpriseViewSet, DriverVehicleViewSet, \
    EnterprisesListViewSet, VehicleListView, VehicleUpdateView, VehicleDeleteView, VehicleFormView, BrandDeleteView, \
    BrandListView, BrandUpdateView, BrandCreateView, EnterpriseUpdateView, VehicleDetailView

handler403 = custom_handler403
handler401 = custom_handler401
# handler500 = custom_handler500

router = routers.DefaultRouter()
router.register(r'vehicles', VehicleViewSet)
router.register(r'drivers', DriverViewSet)
router.register(r'enterprises', EnterpriseViewSet)
router.register(r'active', DriverVehicleViewSet)

urlpatterns = [
    path('', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('enterprises/', EnterprisesListViewSet.as_view(), name='enterprises_list'),
    path('enterprise/<int:enterprise_id>/vehicles/', VehicleListView.as_view(), name='vehicle_list'),
    path('enterprise/<int:enterprise_id>/vehicle/add/', VehicleFormView.as_view(), name='vehicle_create'),
    path('enterprise/<int:enterprise_id>/vehicle/<int:pk>/edit/', VehicleUpdateView.as_view(), name='vehicle_update'),
    path('enterprise/<int:enterprise_id>/vehicle/<int:pk>/delete/', VehicleDeleteView.as_view(), name='vehicle_delete'),
    path('enterprise/<int:enterprise_id>/vehicle/<int:pk>/', VehicleDetailView.as_view(), name='vehicle_detail'),
    path('enterprise/<int:pk>/edit/', EnterpriseUpdateView.as_view(), name='enterprise_update'),

    path('enterprise/<int:enterprise_id>/vehicle/<int:pk>/trips/map/', TripsMapView.as_view(), name='trips_map'),

    path('brand/<int:pk>/delete/', BrandDeleteView.as_view(), name='brand_delete'),
    path('brands/', BrandListView.as_view(), name='brands_list'),
    path('brand/add/', BrandCreateView.as_view(), name='brand_create'),
    path('brand/<int:pk>/edit/', BrandUpdateView.as_view(), name='brand_update'),

    path('admin/', admin.site.urls),

    path('api/', include(router.urls)),
    path('api/auth/', include('authentication.urls')),

    path('api/telemetry/', include('telemetry.urls')),
]

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('api/auth/', include('authentication.urls')),
#     path('api/', include(router.urls)),
#     path('api-auth/', include('rest_framework.urls')),
#     path('', include('authentication.urls'))
# ]
