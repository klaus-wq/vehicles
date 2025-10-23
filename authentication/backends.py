from rest_framework import authentication, exceptions
from django.conf import settings
import jwt
from authentication.models import CustomUser

class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'Token'

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).split()
        if not auth_header or len(auth_header) != 2:
            raise exceptions.AuthenticationFailed(
                'Authentication credentials were not provided.'
            )

        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != self.authentication_header_prefix.lower():
            raise exceptions.AuthenticationFailed('Invalid token prefix.')

        return self._authenticate_credentials(request, token)

    def _authenticate_credentials(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired.')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token.')

        try:
            user = CustomUser.objects.get(pk=payload['id'])
        except CustomUser.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found.')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('User is deactivated.')

        if not (user.is_superuser or hasattr(user, 'manager')):
            raise exceptions.AuthenticationFailed(
                'User must be a manager or superuser to access this API.'
            )

        return (user, token)