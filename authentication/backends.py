import jwt
from django.conf import settings
from rest_framework import authentication, exceptions
from .models import CustomUser

class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'Token'

    def authenticate(self, request):
        request.user = None
        auth_header = authentication.get_authorization_header(request).split()

        if not auth_header or len(auth_header) != 2:
            return None

        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != self.authentication_header_prefix.lower():
            return None

        return self._authenticate_credentials(request, token)

    def _authenticate_credentials(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Токен истёк.')
        except Exception:
            raise exceptions.AuthenticationFailed('Неверный токен.')

        try:
            user = CustomUser.objects.get(pk=payload['id'])
        except CustomUser.DoesNotExist:
            raise exceptions.AuthenticationFailed('Пользователь не найден.')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('Пользователь деактивирован.')

        return (user, token)