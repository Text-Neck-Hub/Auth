# myapp/views.py
from django.core.cache import cache  # Redis 캐시 사용
from allauth.socialaccount.models import SocialAccount  # allauth를 사용한다고 가정
from rest_framework_simplejwt.tokens import RefreshToken  # 토큰에서 사용자 ID 추출용
from rest_framework import status
from rest_framework_simplejwt.views import TokenRefreshView
import logging
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.conf import settings

from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework_simplejwt.settings import api_settings

logger = logging.getLogger('prod')

User = get_user_model()


logger = logging.getLogger(__name__)


class AccessTokenObtainView(APIView):
    # 소셜 로그인 콜백 시점에서는 AllowAny가 맞음.
    permission_classes = [permissions.AllowAny]
    provider = None  # 이 값은 URLconf에서 설정되거나, 하위 클래스에서 정의될 것임.

    @method_decorator(login_required)  # 🚨 이 데코레이터가 사용자를 이미 인증했음을 보장.
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        user = request.user
        logger.info(
            f"User: {user.username} ({user.id}) attempting social login token obtain for provider {self.provider}.")

        social_account = SocialAccount.objects.filter(
            user=user, provider=self.provider).first()

        if not social_account:
            logger.error(
                f"No SocialAccount found for user {user.username} with provider {self.provider}")
            return Response(
                {"error": f"No SocialAccount found for {self.provider}. Please link your account first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.info(f"SocialAccount found: {social_account.uid}. Issuing JWT.")

        refresh = RefreshToken.for_user(user)  # 🚨 여기서 refresh 토큰 객체가 생성됨.
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response_data = {
            'access': access_token,
            'user_info': {
                'email': user.email,
                'name': user.first_name,
            },
            "message": "Social login successful! JWTs issued."
        }
        # 🚨 개선: 전체 토큰 로깅은 보안상 위험. 앞부분만 로깅하는 것은 OK.
        logger.info(
            f"🎄Final response_data before sending🎆: Access token issued (starts with {access_token[:10]})...")
        logger.info(
            f"JWTs issued for user {user.username} ({user.id}). Access token: {access_token[:10]}... Refresh token: {refresh_token[:10]}...")
        response = Response(response_data, status=status.HTTP_200_OK)

        # 🚨 수정 시작: Redis 키 전략 변경 및 TTL 계산 수정!
        # 1. TTL 계산 수정: total_seconds()는 이미 float 값을 반환.
        ttl_seconds = int(
            settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())

        # 2. RefreshToken 객체에서 JTI (JWT ID) 추출
        try:
            # refresh는 이미 RefreshToken 객체이므로 다시 생성할 필요 없음
            jti = refresh['jti']  # RefreshToken 객체에서 직접 jti 클레임에 접근
        except KeyError:
            logger.error(
                f"JTI claim not found in refresh token for user {user.id}.")
            return Response({"error": "Failed to process token (JTI missing)."}, status=status.HTTP_500_INTERNAL_ERROR)

        # 3. Redis 키 전략 변경: user.id와 jti를 함께 사용!
        # 이렇게 해야 각 리프레시 토큰이 고유하게 관리되어 다중 로그인이 가능해져.
        key = f"refresh_token:{user.id}:{jti}"  # 🚨 키 변경!

        cache.set(key, refresh_token, timeout=ttl_seconds)  # Redis에 리프레시 토큰 저장
        logger.info(
            f"✅ Redis에 사용자 {user.id}의 새 리프레시 토큰 저장 완료! 키: {key}, JTI: {jti}, TTL: {ttl_seconds}초")

        # 4. 쿠키 설정 (max_age도 int로 변환)
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=settings.DEBUG is False,
            samesite='Lax',
            max_age=ttl_seconds  # 🚨 max_age도 int로 변환된 ttl_seconds 사용
        )

        return response


class GoogleAccessTokenObtainView(AccessTokenObtainView):
    provider = "google"


class KakaoAccessTokenObtainView(AccessTokenObtainView):
    provider = "kakao"


class NaverAccessTokenObtainView(AccessTokenObtainView):
    provider = "naver"


class GithubAccessTokenObtainView(AccessTokenObtainView):
    provider = "github"


logger = logging.getLogger(__name__)


class AccessTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token_from_cookie = request.COOKIES.get('refresh_token')

        if refresh_token_from_cookie is None:
            logger.warning(
                "Refresh token not found in cookies during refresh attempt.")
            return Response(
                {"detail": "Refresh token not found in cookies."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🚨 수정 시작: old_refresh_token_jti 추출 (이전 토큰 무효화 대상)
        old_refresh_token_jti = None
        user_id = None  # 이 user_id는 이전 토큰에서 추출된 user_id임
        try:
            old_refresh_token_obj = RefreshToken(refresh_token_from_cookie)
            old_refresh_token_jti = old_refresh_token_obj['jti']  # 이전 토큰의 JTI
            user_id = old_refresh_token_obj.get(
                settings.SIMPLE_JWT['USER_ID_CLAIM'])  # 이전 토큰의 사용자 ID
        except Exception as e:
            logger.error(
                f"Error extracting JTI or user_id from old refresh token in cookie: {e}")
            # 여기서 에러가 발생하면, 토큰 자체가 유효하지 않다는 뜻이므로,
            # 부모 클래스의 post 메서드에서 401을 반환할 가능성이 높음.
            # 하지만 안전을 위해 여기서 바로 에러를 반환할 수도 있음.
            # 일단은 simple_jwt의 기본 에러 핸들링에 맡김.

        # 2. simple_jwt의 TokenRefreshView가 처리할 수 있도록 request.data에 refresh 토큰을 넣어주기
        mutable_data = request.data.copy()
        mutable_data['refresh'] = refresh_token_from_cookie
        request._data = mutable_data

        # 3. 부모 클래스의 post 메서드를 호출하여 실제 토큰 갱신 로직 수행
        response = super().post(request, *args, **kwargs)

        # 4. 토큰 갱신 성공 시 (200 OK) 추가 처리
        if response.status_code == status.HTTP_200_OK:
            new_access_token = response.data.get('access')
            # ROTATE_REFRESH_TOKENS=True 이므로 항상 새로운 값이 있음!
            new_refresh_token = response.data.get('refresh')

            # 🚨 이전 리프레시 토큰을 Redis에서 삭제 (무효화)
            # user_id와 old_refresh_token_jti가 유효할 때만 삭제 시도
            if user_id and old_refresh_token_jti:
                # 🚨 이전 키!
                old_redis_key = f"refresh_token:{user_id}:{old_refresh_token_jti}"
                cache.delete(old_redis_key)
                logger.info(f"✅ Redis에서 이전 리프레시 토큰 삭제 완료! 키: {old_redis_key}")
            else:
                logger.warning(
                    "Could not determine user ID or old JTI to delete previous refresh token from Redis.")

            # 🚨 새로운 리프레시 토큰을 Redis에 저장하고 쿠키에 설정
            if user_id and new_refresh_token:  # 사용자 ID와 새로운 리프레시 토큰이 유효할 때만 처리
                try:
                    new_refresh_token_obj = RefreshToken(new_refresh_token)
                    new_jti = new_refresh_token_obj['jti']  # 새로운 토큰의 JTI
                except Exception as e:
                    logger.error(
                        f"Error extracting JTI from new refresh token: {e}")
                    # 새 토큰에서 JTI 추출 실패 시 Redis 저장 및 쿠키 설정 불가.
                    # 이 경우 클라이언트는 새 토큰을 받지만 Redis에 저장되지 않아 다음 갱신 시 문제 발생 가능.
                    # 사용자에게 재로그인 필요 메시지를 보낼지 고려.
                    logger.warning(
                        "Failed to process new refresh token for Redis/cookie update. User might need to re-login.")
                    return response  # 에러 로깅 후 기존 응답 반환

                ttl_seconds = int(
                    settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
                # 🚨 새로운 키!
                new_redis_key = f"refresh_token:{user_id}:{new_jti}"
                cache.set(new_redis_key, new_refresh_token,
                          timeout=ttl_seconds)
                logger.info(
                    f"✅ Redis에 사용자 {user_id}의 새 리프레시 토큰 저장 완료! 키: {new_redis_key}, JTI: {new_jti}")

                # 🚨 클라이언트 쿠키에 새로운 리프레시 토큰 설정 (ROTATE_REFRESH_TOKENS=True 이므로 항상 업데이트)
                response.set_cookie(
                    key='refresh_token',
                    value=new_refresh_token,
                    httponly=True,
                    secure=settings.DEBUG is False,
                    samesite='Lax',
                    max_age=ttl_seconds
                )
                logger.info(f"✅ 클라이언트 쿠키에 새로운 리프레시 토큰 설정 완료.")
            else:
                logger.warning(
                    "Could not determine user ID or new refresh token for Redis/cookie update.")

        return response


class AccessTokenVerificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({"detail": "Access token is valid"}, status=status.HTTP_200_OK)


class RefreshTokenRevokeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        refresh_token_value = request.COOKIES.get('refresh_token')

        if not refresh_token_value:
            return Response(
                {"error": "Refresh token is required for revocation."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 1. 리프레시 토큰 문자열에서 JTI 추출 (가장 중요! ✨)
            # simple_jwt의 RefreshToken 클래스를 사용하면 토큰 문자열을 파싱하고 클레임에 접근할 수 있어.
            token = RefreshToken(refresh_token_value)
            jti = token[api_settings.JTI_CLAIM] # settings에서 JTI 클레임 이름 가져오기

            user_id_from_token = request.user.id
            
            # 2. Redis 키를 로그인 시 저장한 키와 동일하게 구성! ✨
            redis_key = f"refresh_token:{user_id_from_token}:{jti}" 
            
            deleted_count = cache.delete(redis_key)

            if deleted_count == 0:
                logger.warning(
                    f"Attempted to revoke non-existent or already revoked refresh token in Redis for user {user_id_from_token} with JTI {jti}. Key attempted: {redis_key}")
                return Response(
                    {"error": "Refresh token not found or already revoked."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            response = Response(
                {"message": "Refresh token successfully revoked."},
                status=status.HTTP_200_OK
            )
            response.delete_cookie('refresh_token')
            logger.info(
                f"Refresh token revoked for user {user_id_from_token} with JTI {jti} from Redis and cookie. Key: {redis_key}")
            return response

        except Exception as e:
            logger.error(
                f"Error revoking refresh token for user {request.user.id}: {e}", exc_info=True) # exc_info=True로 하면 스택 트레이스도 로깅돼서 디버깅에 도움돼!
            return Response(
                {"error": "An error occurred during token revocation."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )