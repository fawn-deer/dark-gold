import jwt

from django.utils.translation import ugettext as _
from rest_framework import exceptions
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.settings import api_settings

jwt_decode_handler = api_settings.JWT_DECODE_HANDLER


class ExtendJSONWebTokenAuthentication(JSONWebTokenAuthentication):
    """
    扩展jwt认证
    """

    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using JWT-based authentication.  Otherwise returns `None`.
        """
        jwt_value = self.get_jwt_value(request)
        if jwt_value is None:
            return None

        try:
            payload = jwt_decode_handler(jwt_value)
        except jwt.ExpiredSignature:
            msg = _('Signature has expired.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = _('Error decoding signature.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed()

        user = self.authenticate_credentials(payload)

        # 扩展 验证该用户jwt过期时间
        # jwt签发时间早于过期时间，需要重新登录，返回状态码为401
        user_jwt_deadline = user.jwt_deadline
        if user_jwt_deadline and payload['iat'] < user_jwt_deadline:
            raise exceptions.AuthenticationFailed('jwt has expired.')

        return (user, jwt_value)
