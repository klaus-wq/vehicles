from django.db.models import Q
from django.views.generic import ListView, CreateView, DetailView, TemplateView
from django.urls import reverse_lazy
from vehicle.models import Enterprise, Vehicle, Brand
from .models import Report, MileageReportGenerator, DriverAssignmentReportGenerator
from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic import View
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest, HttpResponse
from datetime import datetime, time
from django.utils import timezone

class ReportListView(LoginRequiredMixin, ListView):
    model = Report
    template_name = 'reports_list.html'
    context_object_name = 'reports'
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Report.objects.filter(author=self.request.user)

        report_type = self.request.GET.get('report_type')
        if report_type:
            queryset = queryset.filter(report_type=report_type)

        period = self.request.GET.get('period')
        if period:
            queryset = queryset.filter(period=period)

        start_date = self.request.GET.get('start_date')
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)

        end_date = self.request.GET.get('end_date')
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_filters'] = {
            'report_type': self.request.GET.get('report_type', ''),
            'period': self.request.GET.get('period', ''),
            'start_date': self.request.GET.get('start_date', ''),
            'end_date': self.request.GET.get('end_date', ''),
        }
        return context


class ReportCreateView(LoginRequiredMixin, CreateView):
    model = Report
    template_name = 'reports_create.html'
    fields = ['name', 'report_type', 'period', 'start_date', 'end_date']
    success_url = reverse_lazy('reports:list')

    def get_enterprises(self):
        if self.request.user.is_superuser:
            return Enterprise.objects.all()
        return self.request.user.manager.enterprises.all()

    def get_vehicles(self):
        if self.request.user.is_superuser:
            return Vehicle.objects.all()
        return Vehicle.objects.filter(enterprise__in=self.get_enterprises())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enterprises'] = self.get_enterprises()
        context['vehicles'] = self.get_vehicles()
        return context

    def form_valid(self, form):
        try:
            vehicle_ids = self.request.POST.getlist('vehicle_ids')
            enterprise_id = self.request.POST.get('enterprise_id', '')

            try:
                vehicle_ids = [
                    int(vid) for vid in vehicle_ids
                    if vid and str(vid).strip().isdigit()
                ]
            except (ValueError, TypeError) as e:
                vehicle_ids = []

            try:
                enterprise_id = int(enterprise_id) if enterprise_id and str(enterprise_id).strip().isdigit() else None
            except (ValueError, TypeError) as e:
                enterprise_id = None

            try:
                start_date = datetime.combine(form.cleaned_data['start_date'], time.min)
                end_date = datetime.combine(form.cleaned_data['end_date'], time.max)
            except Exception as e:
                messages.error(self.request, f"Ошибка дат: {str(e)}")
                return self.form_invalid(form)

            if not vehicle_ids and not enterprise_id:
                messages.error(
                    self.request,
                    "Выберите хотя бы одно предприятие или один автомобиль для отчёта"
                )
                return self.form_invalid(form)

            report = form.save(commit=False)
            report.author = self.request.user
            report.start_date = start_date
            report.end_date = end_date
            report.vehicle_ids = vehicle_ids
            report.enterprise_id = enterprise_id
            report.save()

            try:
                if form.cleaned_data['report_type'] == 'MILEAGE':
                    generator = MileageReportGenerator(
                        start_date=report.start_date,
                        end_date=report.end_date,
                        period=report.period,
                        vehicle_ids=report.vehicle_ids,
                        enterprise_id=report.enterprise_id
                    )
                else:
                    generator = DriverAssignmentReportGenerator(
                        start_date=report.start_date,
                        end_date=report.end_date,
                        period=report.period,
                        vehicle_ids=report.vehicle_ids,
                        enterprise_id=report.enterprise_id
                    )

                result = generator.generate()

                report.result_data = result
                report.save(update_fields=['result_data'])

                messages.success(self.request, "Отчёт успешно сформирован!")

            except Exception as gen_error:
                messages.error(self.request, f"Ошибка генерации отчёта: {str(gen_error)}")
                return redirect('reports:reports_detail', pk=report.pk)

            return redirect('reports:reports_detail', pk=report.pk)

        except Exception as e:
            messages.error(self.request, f"Внутренняя ошибка: {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class ReportDetailView(LoginRequiredMixin, DetailView):
    model = Report
    template_name = 'reports_detail.html'
    context_object_name = 'report'

    def get_queryset(self):
        return Report.objects.filter(author=self.request.user)


class ReportGenerateView(LoginRequiredMixin, View):
    """
    http://127.0.0.1:8000/api/reports/generate/?type=MILEAGE&period=MONTH&start_date=2010-03-01&end_date=2026-03-31&vehicle_ids=53870,50861&name=Пробег автомобилей

    http://127.0.0.1:8000/api/reports/generate/?type=DRIVER_ASSIGNMENT&period=MONTH&start_date=2010-03-01&end_date=2026-03-31&vehicle_ids=53870,50861&name=Назначение водителей

    Генерирует отчёт по параметрам и отображает результат.
    """
    template_name = 'reports_detail.html'

    def get(self, request):
        try:
            report_type = request.GET.get('type', '').upper()
            if not report_type:
                return HttpResponseBadRequest('Параметр type обязателен')

            valid_types = [key for key, _ in Report.REPORT_TYPES]
            if report_type not in valid_types:
                return HttpResponseBadRequest(f'Неверный тип отчёта. Доступные: {", ".join(valid_types)}')

            period = request.GET.get('period', 'DAY').upper()
            start_date_str = request.GET.get('start_date')
            end_date_str = request.GET.get('end_date')

            if not start_date_str or not end_date_str:
                return HttpResponseBadRequest('Параметры start_date и end_date обязательны')

            try:
                start_date = datetime.combine(
                    datetime.strptime(start_date_str, '%Y-%m-%d').date(),
                    time.min
                )
                end_date = datetime.combine(
                    datetime.strptime(end_date_str, '%Y-%m-%d').date(),
                    time.max
                )
            except ValueError as e:
                return HttpResponseBadRequest(f'Неверный формат даты. Используйте YYYY-MM-DD: {e}')

            if start_date > end_date:
                return HttpResponseBadRequest('Начальная дата не может быть позже конечной')

            vehicle_ids_str = request.GET.get('vehicle_ids', '')
            enterprise_id_str = request.GET.get('enterprise_id', '')

            vehicle_ids = []
            if vehicle_ids_str:
                try:
                    vehicle_ids = [int(vid.strip()) for vid in vehicle_ids_str.split(',') if vid.strip()]
                except ValueError:
                    return HttpResponseBadRequest('Неверный формат vehicle_ids (должны быть числа через запятую)')

            enterprise_id = None
            if enterprise_id_str:
                try:
                    enterprise_id = int(enterprise_id_str)
                except ValueError:
                    return HttpResponseBadRequest('Неверный формат enterprise_id')

            if not vehicle_ids and not enterprise_id:
                return HttpResponseBadRequest('Укажите vehicle_ids или enterprise_id')

            name = request.GET.get('name', f'{dict(Report.REPORT_TYPES).get(report_type, report_type)} за {start_date_str} — {end_date_str}')

            if report_type == 'MILEAGE':
                generator = MileageReportGenerator(
                    start_date=start_date,
                    end_date=end_date,
                    period=period,
                    vehicle_ids=vehicle_ids,
                    enterprise_id=enterprise_id
                )
            else:
                generator = DriverAssignmentReportGenerator(
                    start_date=start_date,
                    end_date=end_date,
                    period=period,
                    vehicle_ids=vehicle_ids,
                    enterprise_id=enterprise_id
                )
            result = generator.generate()

            report_data = {
                'name': name,
                'report_type': report_type,
                'report_type_display': dict(Report.REPORT_TYPES).get(report_type, report_type),
                'period': period,
                'period_display': dict(Report.PERIOD_CHOICES).get(period, period),
                'start_date': start_date,
                'end_date': end_date,
                'result_data': result,
                'created_at': timezone.now(),
                'saved': False,
            }

            report_data['get_report_type_display'] = lambda: report_data['report_type_display']
            report_data['get_period_display'] = lambda: report_data['period_display']

            print(report_data)

            return render(request, self.template_name, {
                'report': report_data,
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return HttpResponseBadRequest(f'Ошибка генерации отчёта: {str(e)}')

class ReportsView(LoginRequiredMixin, View):
    """
    GET: /reports/generate/?type=MILEAGE&period=DAY&start_date=2024-03-01&end_date=2024-03-31&vehicle_ids=1,2&enterprise_id=5

    Получает отчёт по параметрам и отображает результат.
    """
    template_name = 'reports_detail.html'

    def get(self, request):
        try:
            report_type = request.GET.get('type', '').upper()
            if not report_type:
                return HttpResponseBadRequest('Параметр type обязателен')

            valid_types = [key for key, _ in Report.REPORT_TYPES]
            if report_type not in valid_types:
                return HttpResponseBadRequest(f'Неверный тип отчёта. Доступные: {", ".join(valid_types)}')

            period = request.GET.get('period', 'DAY').upper()
            start_date_str = request.GET.get('start_date')
            end_date_str = request.GET.get('end_date')

            if not start_date_str or not end_date_str:
                return HttpResponseBadRequest('Параметры start_date и end_date обязательны')

            try:
                start_date = datetime.combine(
                    datetime.strptime(start_date_str, '%Y-%m-%d').date(),
                    time.min
                )
                end_date = datetime.combine(
                    datetime.strptime(end_date_str, '%Y-%m-%d').date(),
                    time.max
                )
            except ValueError as e:
                return HttpResponseBadRequest(f'Неверный формат даты. Используйте YYYY-MM-DD: {e}')

            if start_date > end_date:
                return HttpResponseBadRequest('Начальная дата не может быть позже конечной')

            vehicle_ids_str = request.GET.get('vehicle_ids', '')
            enterprise_id_str = request.GET.get('enterprise_id', '')

            vehicle_ids = []
            if vehicle_ids_str:
                try:
                    vehicle_ids = [int(vid.strip()) for vid in vehicle_ids_str.split(',') if vid.strip()]
                except ValueError:
                    return HttpResponseBadRequest('Неверный формат vehicle_ids (должны быть числа через запятую)')

            enterprise_id = None
            if enterprise_id_str:
                try:
                    enterprise_id = int(enterprise_id_str)
                except ValueError:
                    return HttpResponseBadRequest('Неверный формат enterprise_id')

            if not vehicle_ids and not enterprise_id:
                return HttpResponseBadRequest('Укажите vehicle_ids или enterprise_id')

            name = request.GET.get('name', f'{dict(Report.REPORT_TYPES).get(report_type, report_type)} за {start_date_str} — {end_date_str}')

            reports = Report.objects.filter(author=request.user, report_type=report_type,
                                           period=period, start_date__gte=start_date,
                                           end_date__lte=end_date
            ).order_by('-created_at')

            # Фильтр по enterprise_id
            if enterprise_id:
                reports = reports.filter(enterprise_id=enterprise_id)

            if vehicle_ids:
                matching_ids = []
                for report in reports:
                    # report.vehicle_ids — это список или None
                    report_vehicle_ids = report.vehicle_ids or []
                    # Проверяем, есть ли хотя бы один из запрошенных ID в списке отчёта
                    if any(vid in report_vehicle_ids for vid in vehicle_ids):
                        matching_ids.append(report.pk)

                # Фильтруем по найденным ID
                reports = Report.objects.filter(pk__in=matching_ids) if matching_ids else Report.objects.none()

            report = reports.order_by('-created_at').first()

            if not report:
                return HttpResponseBadRequest(
                    f'Отчёты не найдены. Параметры: type={report_type}, '
                    f'start={start_date_str}, end={end_date_str}, '
                    f'vehicle_ids={vehicle_ids_str}, enterprise_id={enterprise_id_str}'
                )

            report_data = {
                'name': name,
                'report_type': report_type,
                'report_type_display': dict(Report.REPORT_TYPES).get(report_type, report_type),
                'period': period,
                'period_display': dict(Report.PERIOD_CHOICES).get(period, period),
                'start_date': start_date,
                'end_date': end_date,
                'result_data': report.result_data,
                'created_at': timezone.now(),
                'filters': {
                    'report_type': report_type,
                    'period': period,
                    'start_date': start_date_str,
                    'end_date': end_date_str,
                    'vehicle_ids': vehicle_ids_str,
                    'enterprise_id': enterprise_id_str,
                }
            }

            report_data['get_report_type_display'] = lambda: report_data['report_type_display']
            report_data['get_period_display'] = lambda: report_data['period_display']

            print(report_data)

            return render(request, self.template_name, {
                'report': report_data,
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return HttpResponseBadRequest(f'Ошибка генерации отчёта: {str(e)}')


class ReportExportPDFView(LoginRequiredMixin, View):
    def get(self, request, pk):
        from weasyprint import HTML
        from django.template.loader import render_to_string

        report = get_object_or_404(Report, pk=pk, author=request.user)

        html_string = render_to_string('reports_pdf.html', {
            'report': report,
        })

        pdf = HTML(string=html_string).write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="report_{report.id}.pdf"'

        return response