import logging
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings

logger = logging.getLogger('prod')


class RevokeTokenService:
    @staticmethod
    def revoke_refresh_token(refresh_token_value: str, request_user_id: int) -> bool:
        """
        주어진 리프레시 토큰을 무효화하고 Redis에서 삭제합니다.
        성공적으로 삭제되면 True를, 실패하면 ValueError를 발생시킵니다.
        """
        try:
            token = RefreshToken(refresh_token_value)
            jti = token[api_settings.JTI_CLAIM]

            token_user_id = token.get(api_settings.USER_ID_CLAIM)
            if str(token_user_id) != str(request_user_id):
                logger.error(
                    f"요청 유저 ID {request_user_id} 와 토큰 유저 ID {token_user_id} 가 불일치합니다.")
                raise ValueError("토큰과 사용자 정보가 일치하지 않습니다.")

            redis_key = f"refresh_token:{request_user_id}:{jti}"

            deleted_count = cache.delete(redis_key)

            if deleted_count == 0:
                logger.warning(
                    f"사용자 {request_user_id}의 리프레시 토큰(JTI: {jti})이 Redis에서 이미 없거나 무효화되었습니다. 키: {redis_key}")
                raise ValueError("리프레시 토큰을 찾을 수 없거나 이미 무효화되었습니다.")

            logger.info(
                f"Redis에서 리프레시 토큰 삭제 완료. 사용자: {request_user_id}, JTI: {jti}, 키: {redis_key}")
            return True

        except KeyError:
            logger.error("리프레시 토큰에서 JTI 클레임을 찾을 수 없습니다. 유효하지 않은 토큰입니다.")
            raise ValueError("유효하지 않은 리프레시 토큰입니다.")
        except Exception as e:
            logger.error(
                f"리프레시 토큰 무효화 중 예상치 못한 오류 발생 (사용자 {request_user_id}): {e}", exc_info=True)
            raise ValueError(f"토큰 무효화 중 오류가 발생했습니다: {e}")
