from django.contrib.auth import login
from django.contrib.auth.views import LogoutView, LoginView
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.urls import reverse_lazy

from authentication.forms import CustomLoginForm
from authentication.serializers import RegistrationSerializer, LoginSerializer

class RegistrationAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})

        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class LoginAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        return Response({'user': serializer.data}, status=status.HTTP_200_OK)

class CustomLoginView(LoginView):
    template_name = 'login.html'
    form_class = CustomLoginForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('enterprises')

    def form_invalid(self, form):
        messages.error(self.request, 'Неверный логин или пароль')
        return super().form_invalid(form)

    def get_success_url(self):
        messages.success(self.request, f'Добро пожаловать, {self.request.user.get_full_name() or self.request.user.username}!')
        return super().get_success_url()

class CustomLogoutView(LogoutView):
    next_page = 'login'