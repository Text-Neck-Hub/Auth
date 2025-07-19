from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import logging

from ..services.token_servies import SocialAuthService
from ..services.token_servies import TokenRefreshService


logger = logging.getLogger('prod')


class AccessTokenObtainView(APIView):
    permission_classes = [permissions.AllowAny]

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        provider = request.session.get('provider', None)

        if not provider:
            logger.error("세션에 제공자를 찾을 수 없습니다. 사용자가 소셜 계정으로 로그인하지 않았을 수 있습니다.")
            return Response(
                {"error": "세션에 제공자를 찾을 수 없습니다. 소셜 계정으로 로그인해주세요."},
                status=status.HTTP_400_BAD_REQUEST
            )

        request.session.pop('provider')

        user = request.user

        try:
            response_data, cookie_settings = SocialAuthService.obtain_jwt_for_social_user(
                user, provider)

            response = Response(response_data, status=status.HTTP_200_OK)
            response.set_cookie(**cookie_settings)
            logger.info(f"성공적으로 JWT 응답 및 쿠키 설정 완료 (사용자 ID: {user.id})")
            return response

        except ValueError as e:
            logger.error(f"소셜 로그인 토큰 발급 중 오류 발생: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.critical(
                f"예상치 못한 심각한 오류 발생 (유저 ID: {user.id}): {e}", exc_info=True)
            return Response({"error": "내부 서버 오류가 발생했습니다."}, status=status.HTTP_500_INTERNAL_ERROR)


class AccessTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token_from_cookie = request.COOKIES.get('refresh_token')

        if refresh_token_from_cookie is None:
            logger.warning("쿠키에서 리프레시 토큰을 찾을 수 없습니다. 토큰 갱신 시도 실패.")
            return Response(
                {"detail": "쿠키에서 리프re시 토큰을 찾을 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        mutable_data = request.data.copy()
        mutable_data['refresh'] = refresh_token_from_cookie
        request._data = mutable_data

        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            new_refresh_token = response.data.get('refresh')

            if new_refresh_token:
                try:
                    cookie_settings = TokenRefreshService.manage_refreshed_tokens_in_cache_and_cookies(
                        refresh_token_from_cookie,
                        new_refresh_token
                    )
                    response.set_cookie(**cookie_settings)
                    logger.info("클라이언트 쿠키에 새로운 리프레시 토큰 설정 완료.")
                except ValueError as e:
                    logger.error(f"토큰 갱신 후 처리 오류: {e}")
                    return Response({"detail": f"토큰 처리 중 오류가 발생했습니다: {e}"}, status=status.HTTP_500_INTERNAL_ERROR)
                except Exception as e:
                    logger.critical(
                        f"토큰 갱신 후 처리 중 예상치 못한 심각한 오류 발생: {e}", exc_info=True)
                    return Response({"detail": "내부 서버 오류가 발생했습니다."}, status=status.HTTP_500_INTERNAL_ERROR)
            else:
                logger.warning("새 리프레시 토큰을 응답에서 찾을 수 없어 Redis/쿠키 업데이트를 건너뜀.")

        return response
