# myapp/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
import requests
import os

User = get_user_model()


class TokenVerificationView(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        google_id_token = request.data.get('id_token')

        if not google_id_token:
            return Response({"error": "ID 토큰이 없어! 🥺"}, status=status.HTTP_400_BAD_REQUEST)

        google_verify_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={google_id_token}"

        try:
            response = requests.get(google_verify_url)
            response.raise_for_status()
            token_info = response.json()
        except requests.exceptions.RequestException as e:
            print(f"구글 토큰 검증 요청 실패: {e}")
            return Response({"error": "구글 토큰 검증에 실패했어. 😭"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        GOOGLE_CLIENT_ID = os.environ.get(
            "GOOGLE_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID_HERE")

        if token_info.get('aud') != GOOGLE_CLIENT_ID:
            print(f"클라이언트 ID 불일치: {token_info.get('aud')} != {GOOGLE_CLIENT_ID}")
            return Response({"error": "유효하지 않은 클라이언트 ID야! 😡"}, status=status.HTTP_401_UNAUTHORIZED)
        if token_info.get('iss') not in ['accounts.google.com', 'https://accounts.google.com']:
            print(f"발급자 불일치: {token_info.get('iss')}")
            return Response({"error": "유효하지 않은 발급자야! 😠"}, status=status.HTTP_401_UNAUTHORIZED)

        email = token_info.get('email')
        name = token_info.get('name', email)

        if not email:
            return Response({"error": "이메일 정보가 없어! 😥"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user, created = User.objects.get_or_create(email=email)
            if created:
                user.username = email
                user.first_name = name
                user.set_unusable_password()
                user.save()
                print(f"새로운 유저 생성! 🎉: {user.email}")
            else:
                print(f"기존 유저 로그인! 🥳: {user.email}")

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({
                'access': access_token,
                'refresh': str(refresh),
                'user_info': {
                    'email': user.email,
                    'name': user.first_name,
                },
                "message": "구글 로그인 성공! 🤩"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"유저 처리 중 에러 발생: {e}")
            return Response({"error": "사용자 처리 중 오류가 발생했어. 😢"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
