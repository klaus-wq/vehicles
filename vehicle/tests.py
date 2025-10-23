from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from vehicle.models import Vehicle, Brand, Enterprise, Driver, DriverVehicle
from authentication.models import Manager

User = get_user_model()

class Tests(APITestCase):

    def test_user_get_forbidden(self):
        """1. Обычный юзер (не менеджер), корректно авторизован — 403 Forbidden"""
        user = User.objects.create_user(username="user", password="user")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {user.token}")

        response = self.client.get("/api/vehicles/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_request_unauthorized(self):
        """2. Сторонний человек (не авторизован) — 401 Unauthorized"""
        response = self.client.get("/api/vehicles/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_invalid_password_unauthorized(self):
        """3. Менеджер: правильный логин, неверный пароль — 401 Unauthorized"""
        User.objects.create_user(username="manager1", password="manager1")
        response = self.client.post("/api/auth/users/login/", {
            "user": {"username": "manager1", "password": "wrongpass"}
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_manager_access_to_other_enterprise_forbidden(self):
        """4. Менеджер пытается получить доступ к чужому ресурсу — 403 Forbidden"""
        user1 = User.objects.create_user(username="manager1", password="manager1")
        user2 = User.objects.create_user(username="manager2", password="manager2")
        enterprise1 = Enterprise.objects.create(name="Enterprise 1", city="City 1")
        enterprise2 = Enterprise.objects.create(name="Enterprise 2", city="City 2")
        manager1 = Manager.objects.create(user=user1)
        manager1.enterprises.add(enterprise1)
        manager2 = Manager.objects.create(user=user2)
        manager2.enterprises.add(enterprise2)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {manager1.user.token}")
        response = self.client.get(f"/api/enterprises/{enterprise2.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_request_bad_request(self):
        """5. Некорректный запрос — 400 Bad Request"""
        user = User.objects.create_user(username="manager1", password="manager1")
        manager = Manager.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {manager.user.token}")
        response = self.client.post("/api/enterprises/", {
            "name": "Enterprise 1",
            "citty": "City 1",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_enterprise_with_vehicles_conflict(self):
        """6. Удаление предприятия с автомобилями — 409 Conflict"""
        user = User.objects.create_user(username="manager1", password="manager1")
        enterprise = Enterprise.objects.create(name="Enterprise 1", city="City 1")
        manager = Manager.objects.create(user=user)
        manager.enterprises.add(enterprise)
        brand = Brand.objects.create(
            id=1,
            name="Toyota",
            vehicle_type="car",
            fuel_tank_capacity=60,
            seating_capacity=5
        )
        Vehicle.objects.create(
            car_number="A123BC77",
            price=1000000,
            year=2020,
            mileage=0,
            fuel_type="gasoline",
            transmission="automatic",
            color="Red",
            brand=brand,
            enterprise=enterprise
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {manager.user.token}")
        response = self.client.delete(f"/api/enterprises/{enterprise.id}/")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_delete_enterprise_shared_with_other_manager_conflict(self):
        """7. Удаление предприятия, видимого другим менеджерам — 409 Conflict"""
        enterprise = Enterprise.objects.create(name="Enterprise 1", city="City 1")
        user1 = User.objects.create_user(username="manager1", password="manager1")
        user2 = User.objects.create_user(username="manager2", password="manager2")
        manager1 = Manager.objects.create(user=user1)
        manager2 = Manager.objects.create(user=user2)
        manager1.enterprises.add(enterprise)
        manager2.enterprises.add(enterprise)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {manager1.user.token}")
        response = self.client.delete(f"/api/enterprises/{enterprise.id}/")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_successful_crud_status_codes(self):
        """8. Успешный CRUD — правильные коды: POST-201, PUT-200, DELETE-204"""
        user = User.objects.create_user(username="manager1", password="manager1")
        enterprise = Enterprise.objects.create(name="Eneterpeise 1", city="City 1")
        manager = Manager.objects.create(user=user)
        manager.enterprises.add(enterprise)
        brand = Brand.objects.create(
            id=1,
            name="Toyota",
            vehicle_type="car",
            fuel_tank_capacity=60,
            seating_capacity=5
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {manager.user.token}")
        response = self.client.post("/api/vehicles/", {
            "car_number": "B456DE77",
            "price": "1500000.00",
            "year": 2021,
            "mileage": 10000,
            "fuel_type": "gasoline",
            "transmission": "automatic",
            "color": "Green",
            "brand": brand.id,
            "enterprise": enterprise.id
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        vehicle_id = response.data["id"]

        response = self.client.put(f"/api/vehicles/{vehicle_id}/", {
            "car_number": "B456DE77",
            "price": "1400000.00",
            "year": 2021,
            "mileage": 10000,
            "fuel_type": "gasoline",
            "transmission": "automatic",
            "color": "Blue",
            "brand": brand.id,
            "enterprise": enterprise.id
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(f"/api/vehicles/{vehicle_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)