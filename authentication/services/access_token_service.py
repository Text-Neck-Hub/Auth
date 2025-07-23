from django.core.cache import cache  # cache 임포트 (Redis 캐시 사용 시)
from django.conf import settings  # settings 임포트
from allauth.socialaccount.models import SocialAccount  # SocialAccount 임포트
from rest_framework_simplejwt.tokens import RefreshToken  # RefreshToken 임포트
from django.core.cache import cache
from allauth.socialaccount.models import SocialAccount
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.contrib.auth import get_user_model
from ..serializers.access_token_serializer import AccessTokenObtainPairSerializer
import logging


logger = logging.getLogger('prod')
User = get_user_model()


# class SocialAuthService:

#     @staticmethod
#     def obtain_jwt_for_social_user(user):
#         providers = {'kakao': 'kakao', 'naver': 'naver', 'gmail': 'google'}
#         logger.info(f"소셜 로그인 사용자 {user}의 JWT 발급 시작.")
#         logger.info(f"소셜 로그인 사용자 {user} ({user.email.split('@')[1].split('.')[0]})의 JWT 발급 시작.")
#         provider = providers.get(user.email.split('@')[1].split('.')[0], None)
#         logger.info(f"소셜 로그인 제공자: {provider}")
#         social_account = SocialAccount.objects.filter(
#             user=user, provider=provider).first()

#         if not social_account:
#             logger.error(f"유저 {user.username}를 위한 소셜 계정({provider})을 찾을 수 없음.")
#             raise ValueError(f"소셜 계정 ({provider})을 찾을 수 없습니다.")

#         logger.info(f"소셜 계정 발견: UID {social_account.uid}. JWT 발급 진행.")

#         refresh = RefreshToken.for_user(user)
#         access_token = str(refresh.access_token)
#         refresh_token = str(refresh)

#         response_data = {
#             'access': access_token,
#             'user_info': {
#                 'uid': social_account.uid
#             },
#             "message": "소셜 로그인 성공! JWT 발급 완료."
#         }
#         logger.info(
#             f"JWTs 발급 완료: Access token (시작: {access_token[:10]}), Refresh token (시작: {refresh_token[:10]})")

#         ttl_seconds = int(
#             settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
#         try:
#             jti = refresh['jti']
#         except KeyError:
#             logger.error(f"유저 {user.id}의 리프레시 토큰에서 JTI 클레임을 찾을 수 없음.")
#             raise ValueError("토큰 처리 실패 (JTI 누락).")

#         cache_key = f"refresh_token:{user.id}:{jti}"
#         cache.set(cache_key, refresh_token, timeout=ttl_seconds)
#         logger.info(
#             f"캐시에 사용자 {user.id}의 새 리프레시 토큰 저장 완료. 키: {cache_key}, JTI: {jti}, TTL: {ttl_seconds}초")

#         cookie_settings = {
#             'key': 'refresh_token',
#             'value': refresh_token,
#             'httponly': True,
#             'secure': settings.DEBUG is False,
#             'samesite': 'Lax',
#             'max_age': ttl_seconds
#         }

#         return response_data, cookie_settings

# your_app/services/access_token_service.py


class SocialAuthService:
    @staticmethod
    def obtain_jwt_for_social_user(user):
        # 1) RefreshToken 생성 (get_token으로 커스텀 클레임 적용)
        refresh = AccessTokenObtainPairSerializer.get_token(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # 2) 응답 데이터 구성
        response_data = {
            'access': access_token,
            'message': '소셜 로그인 성공! JWT 발급 완료.'
        }

        # 3) Refresh 토큰 JTI 캐싱 (블랙리스트/토큰 회전 대비)
        ttl_seconds = int(
            settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
        jti = refresh['jti']
        cache_key = f"refresh_token:{user.id}:{jti}"
        cache.set(cache_key, refresh_token, timeout=ttl_seconds)
        logger.info(
            f"Cached refresh token for user {user.id}, JTI {jti}, TTL {ttl_seconds}s")

        # 4) 쿠키 설정 반환
        cookie_settings = {
            'key': 'refresh_token',
            'value': refresh_token,
            'httponly': True,
            'secure': not settings.DEBUG,
            'samesite': 'Lax',
            'max_age': ttl_seconds
        }

        return response_data, cookie_settings
# class SocialAuthService:
#     @staticmethod
#     def obtain_jwt_for_social_user(user):
#         providers = {'kakao': 'kakao', 'naver': 'naver', 'gmail': 'google'}
#         logger.info(
#             f"소셜 로그인 사용자 {user.username} ({user.email})의 JWT 발급 시작. 추론된 제공자: {providers.get(user.email.split('@')[1].split('.')[0], '알 수 없음')}")

#         try:
#             domain_suffix = user.email.split('@')[1].split('.')[0]
#             provider = providers.get(domain_suffix, None)
#             if not provider:
#                 first_social_account = SocialAccount.objects.filter(
#                     user=user).first()
#                 if first_social_account:
#                     provider = first_social_account.provider
#                 else:
#                     raise ValueError("소셜 제공자 정보를 찾을 수 없습니다.")
#         except Exception:
#             first_social_account = SocialAccount.objects.filter(
#                 user=user).first()
#             if first_social_account:
#                 provider = first_social_account.provider
#             else:
#                 raise ValueError("소셜 제공자 정보를 찾을 수 없습니다.")

#         social_account = SocialAccount.objects.filter(
#             user=user, provider=provider).first()

#         if not social_account:
#             logger.error(f"유저 {user.username}를 위한 소셜 계정({provider})을 찾을 수 없음.")
#             raise ValueError(f"소셜 계정 ({provider})을 찾을 수 없습니다.")

#         logger.info(f"소셜 계정 발견: UID {social_account.uid}. JWT 발급 진행.")

#         refresh = RefreshToken.for_user(user)

#         access_token = str(refresh.access_token)
#         refresh_token = str(refresh)

#         response_data = {
#             'access': access_token,
#             "message": "소셜 로그인 성공! JWT 발급 완료."
#         }
#         logger.info(
#             f"JWTs 발급 완료: Access token (시작: {access_token[:10]}), Refresh token (시작: {refresh_token[:10]})")

#         ttl_seconds = int(
#             settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
#         try:
#             jti = refresh['jti']
#         except KeyError:
#             logger.error(f"유저 {user.id}의 리프레시 토큰에서 JTI 클레임을 찾을 수 없음.")
#             raise ValueError("토큰 처리 실패 (JTI 누락).")

#         cache_key = f"refresh_token:{user.id}:{jti}"
#         cache.set(cache_key, refresh_token, timeout=ttl_seconds)
#         logger.info(
#             f"캐시에 사용자 {user.id}의 새 리프레시 토큰 저장 완료. 키: {cache_key}, JTI: {jti}, TTL: {ttl_seconds}초")

#         cookie_settings = {
#             'key': 'refresh_token',
#             'value': refresh_token,
#             'httponly': True,
#             'secure': settings.DEBUG is False,
#             'samesite': 'Lax',
#             'max_age': ttl_seconds
#         }

#         return response_data, cookie_settings


class TokenRefreshService:
    @staticmethod
    def manage_refreshed_tokens_in_cache_and_cookies(old_refresh_token_cookie: str, new_refresh_token: str) -> dict:
        try:
            old_refresh_token_obj = RefreshToken(old_refresh_token_cookie,verify=False)
            logger.debug(
                f"✅🎭🖼🎨 토큰 파싱 성공 - payload: {old_refresh_token_obj.payload}")
        except Exception as e:
            logger.error(f"❌🎭🖼🎨 리프레시 토큰 파싱 중 오류 발생: {str(e)}", exc_info=True)

        old_refresh_token_jti = None
        user_id = None

        try:
            old_refresh_token_obj = RefreshToken(old_refresh_token_cookie,verify=False)
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
