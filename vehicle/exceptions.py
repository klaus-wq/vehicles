from django.db.models import ProtectedError
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, ProtectedError):
        return Response(
            {"detail": "Невозможно удалить объект, так как он используется другими записями."},
            status=status.HTTP_409_CONFLICT
        )

    return response

def custom_handler403(request, exception):
    return render(
        request=request,
        template_name="error.html",
        status=403,
        context={
            "title": "Ошибка доступа: 403",
            "error_message": "Доступ к этой странице ограничен",
            'status': 403
        },
    )

def custom_handler401(request, exception):
    return render(
        request=request,
        template_name="error.html",
        status=401,
        context={
            "title": "Ошибка доступа: 401",
            "error_message": "Страница доступна только авторизированным пользователям",
            'status': 401
        },
    )

def custom_handler500(request):
    return render(request, "error.html", {
        "title": "Ошибка сервера: 500",
        "error_message": "Что-то пошло не так. Обратитесь к администратору.",
        'status': 500
    }, status=500)