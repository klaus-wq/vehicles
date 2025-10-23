from vehicle.models import Enterprise
import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.contrib.auth.models import PermissionsMixin, AbstractUser, UserManager
from django.db import models

class CustomUser(AbstractUser, PermissionsMixin):
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username'

    objects = UserManager()

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_set",
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_set",
        blank=True,
    )

    @property
    def token(self):
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        dt = datetime.now(timezone.utc) + timedelta(days=1) + timedelta(days=1)
        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.timestamp())
        }, settings.SECRET_KEY, algorithm='HS256')
        return token

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def get_short_name(self):
        return self.first_name or self.username

class Manager(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='manager',
        verbose_name='Пользователь'
    )
    enterprises = models.ManyToManyField(
        Enterprise,
        related_name='managers',
        verbose_name='Предприятия'
    )

    class Meta:
        verbose_name = 'Менеджер'
        verbose_name_plural = 'Менеджеры'

    def __str__(self):
        enterprises_list = ", ".join([f"{enterprise.id} {enterprise.name}" for enterprise in self.enterprises.all()])
        return f'{self.user.username}, {enterprises_list}'