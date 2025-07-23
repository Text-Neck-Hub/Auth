
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

class CookieTokenRefreshSerializer(TokenRefreshSerializer):

    refresh = serializers.CharField(required=False, allow_null=True)

    default_error_messages = {
        'no_token': ('쿠키에서 유효한 refresh 토큰을 찾을 수 없습니다.'),
    }

    def validate(self, attrs):
        request = self.context.get('request')

        if not request:
            raise ValidationError("Request context is missing.", 'no_request_context')

        refresh_token_from_cookie = request.COOKIES.get('refresh_token')

        if not refresh_token_from_cookie:

            raise ValidationError(self.error_messages['no_token'], 'no_token')

        
        attrs['refresh'] = refresh_token_from_cookie

        return super().validate(attrs)