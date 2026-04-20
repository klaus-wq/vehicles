from reports.views import ReportListView, ReportCreateView, ReportDetailView, ReportGenerateView, ReportsView, \
    ReportExportPDFView
from django.urls import path

app_name = "reports"

urlpatterns = [
    path('reports_list/', ReportListView.as_view(), name='reports_list'),
    path('reports_list/create/', ReportCreateView.as_view(), name='reports_create'),
    path('reports_list/<int:pk>/', ReportDetailView.as_view(), name='reports_detail'),
    path('generate/', ReportGenerateView.as_view(), name='reports_generate'),
    path('report_view/', ReportsView.as_view(), name='report_view'),
    path('<int:pk>/export/pdf/', ReportExportPDFView.as_view(), name='export_pdf'),
]