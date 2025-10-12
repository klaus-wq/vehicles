from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class CSRFProtectionTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            is_staff=True
        )
        self.token = Token.objects.create(user=self.user)

    def test_csrf_protected_view_requires_token(self):
        """Проверяет, что защищенная view требует CSRF токен для POST запроса"""
        # Попытка POST без CSRF токена
        response = self.client.post(
            reverse('api-token-auth'),
            {'username': 'testuser', 'password': 'testpassword'}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Получение CSRF токена
        response = self.client.get(reverse('api-token-auth'))
        csrf_token = response.cookies['csrftoken'].value

        # Успешный POST с CSRF токеном
        response = self.client.post(
            reverse('api-token-auth'),
            {'username': 'testuser', 'password': 'testpassword'},
            HTTP_X_CSRFTOKEN=csrf_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_csrf_token_in_response_headers(self):
        """Проверяет, что ответ содержит CSRF токен в заголовках"""
        response = self.client.get(reverse('api-token-auth'))
        self.assertIn('csrftoken', response.cookies)
        self.assertTrue(len(response.cookies['csrftoken'].value) > 0)

    def test_csrf_protected_api_endpoint(self):
        """Проверяет защиту конкретного API эндпоинта"""
        # Получение CSRF токена
        self.client.get('/api/enterprises/create/')
        csrf_token = self.client.cookies['csrftoken'].value

        # Попытка создания предприятия с токеном
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(
            '/api/enterprises/create/',
            {},
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)