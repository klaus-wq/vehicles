from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from vehicle.models import Enterprise, Manager
from rest_framework.test import APIClient

class EnterpriseCSRFTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username='admin',
            password='adminpassword'
        )

        self.client = Client(enforce_csrf_checks=True)

    def test_enterprise_create_with_and_without_csrf(self):
        self.client.force_login(user=self.superuser)

        response = self.client.get('/api-auth/login/')

        self.assertIn('csrftoken', response.cookies)

        csrf_token = self.client.cookies['csrftoken'].value
        self.assertTrue(len(csrf_token) > 0)

        data = {
            'name': 'New Enterprise',
            'city': 'Moscow',
            'address': 'New Address',
            'phone': '123456789'
        }

        response = self.client.post(
            reverse('enterprise_create'),
            data,
            HTTP_X_CSRFTOKEN=csrf_token
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(
            reverse('enterprise_create'),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post(
            reverse('enterprise_create'),
            data,
            HTTP_X_CSRFTOKEN='error'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)