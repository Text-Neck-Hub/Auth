from django.core.cache import cache
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from ..serializers.access_token_serializer import AccessTokenObtainPairSerializer
import logging


logger = logging.getLogger('prod')
User = get_user_model()


class SocialAuthService:
    @staticmethod
    def obtain_jwt_for_social_user(user):

        refresh = AccessTokenObtainPairSerializer.get_token(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response_data = {
            'access': access_token,
            'message': '소셜 로그인 성공! JWT 발급 완료.'
        }

        ttl_seconds = int(
            settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
        jti = refresh['jti']
        cache_key = f"refresh_token:{user.id}:{jti}"
        cache.set(cache_key, refresh_token, timeout=ttl_seconds)
        logger.info(
            f"Cached refresh token for user {user.id}, JTI {jti}, TTL {ttl_seconds}s")

        cookie_settings = {
            'key': 'refresh_token',
            'value': refresh_token,
            'httponly': True,
            'secure': not settings.DEBUG,
            'samesite': 'Lax',
            'max_age': ttl_seconds
        }

        return response_data, cookie_settings


class TokenRefreshService:
    @staticmethod
    def manage_refreshed_tokens_in_cache_and_cookies(old_refresh_token_cookie: str, new_refresh_token: str) -> dict:
        try:
            old_refresh_token_obj = RefreshToken(
                old_refresh_token_cookie, verify=False)
            logger.debug(
                f"✅🎭🖼🎨 토큰 파싱 성공 - payload: {old_refresh_token_obj.payload}")
        except Exception as e:
            logger.error(f"❌🎭🖼🎨 리프레시 토큰 파싱 중 오류 발생: {str(e)}", exc_info=True)

        old_refresh_token_jti = None
        user_id = None

        try:
            old_refresh_token_obj = RefreshToken(
                old_refresh_token_cookie, verify=False)
            old_refresh_token_jti = old_refresh_token_obj['jti']
            user_id = old_refresh_token_obj.get(
                settings.SIMPLE_JWT['USER_ID_CLAIM'])
            logger.debug(
                f"오래된 리프레시 토큰 파싱됨: 유저 ID {user_id}, JTI {old_refresh_token_jti}")
        except Exception as e:
            logger.error(f"오래된 리프레시 토큰(쿠키)에서 JTI 또는 사용자 ID 추출 오류: {e}")
            raise ValueError("오래된 토큰 처리 중 오류가 발생했습니다.")

        if user_id and old_refresh_token_jti:
            old_redis_key = f"refresh_token:{user_id}:{old_refresh_token_jti}"
            cache.delete(old_redis_key)
            logger.info(f"✅ Redis에서 이전 리프레시 토큰 삭제 완료! 키: {old_redis_key}")
        else:
            logger.warning(
                "이전 리프레시 토큰을 Redis에서 삭제하기 위한 사용자 ID 또는 JTI를 확인할 수 없음.")

        new_jti = None
        try:
            new_refresh_token_obj = RefreshToken(new_refresh_token)
            new_jti = new_refresh_token_obj['jti']
            logger.debug(f"새 리프레시 토큰 파싱됨: JTI {new_jti}")
        except Exception as e:
            logger.error(f"새 리프레시 토큰에서 JTI 추출 오류: {e}")
            raise ValueError("새 토큰 처리 중 오류가 발생했습니다.")

        ttl_seconds = int(
            settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
        new_redis_key = f"refresh_token:{user_id}:{new_jti}"
        cache.set(new_redis_key, new_refresh_token, timeout=ttl_seconds)
        logger.info(
            f"✅ Redis에 사용자 {user_id}의 새 리프레시 토큰 저장 완료! 키: {new_redis_key}, JTI: {new_jti}")

        cookie_settings = {
            'key': 'refresh_token',
            'value': new_refresh_token,
            'httponly': True,
            'secure': settings.DEBUG is False,
            'samesite': 'Lax',
            'max_age': ttl_seconds
        }
        logger.info("새 리프레시 토큰을 위한 쿠키 설정 준비 완료.")
        return cookie_settings
