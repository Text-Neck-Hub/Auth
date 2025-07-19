
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
import logging

from ..services.refresh_token_service import RevokeTokenService


logger = logging.getLogger('prod')


class RefreshTokenRevokeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        refresh_token_value = request.COOKIES.get('refresh_token')

        if not refresh_token_value:
            logger.warning(
                f"리프레시 토큰 무효화 요청에 토큰이 누락되었습니다. 사용자: {request.user.id}")
            return Response(
                {"error": "리프레시 토큰이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            RevokeTokenService.revoke_refresh_token(
                refresh_token_value, request.user.id)

            response = Response(
                {"message": "리프레시 토큰이 성공적으로 무효화되었습니다."},
                status=status.HTTP_200_OK
            )
            response.delete_cookie('refresh_token')
            logger.info(
                f"사용자 {request.user.id}의 리프레시 토큰이 성공적으로 무효화되고 쿠키에서 삭제되었습니다.")
            return response

        except ValueError as e:
            logger.error(
                f"리프레시 토큰 무효화 비즈니스 로직 오류 (사용자: {request.user.id}): {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.critical(
                f"리프레시 토큰 무효화 중 예상치 못한 심각한 오류 발생 (사용자: {request.user.id}): {e}", exc_info=True)
            return Response(
                {"error": "토큰 무효화 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
