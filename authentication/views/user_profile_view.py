from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from ..models import UserProfile
from ..serializers.user_profile_serializer import UserProfileSerializer
from ..services.user_profile_service import UserProfileService
from ..utils.cache import CacheAside
from ..services.refresh_token_service import RevokeTokenService
import logging

logger = logging.getLogger('prod')


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class UserProfileView(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        if self.action in ['retrieve', 'update', 'destroy'] and 'pk' not in self.kwargs:
            return UserProfile.objects.filter(user=self.request.user)
        return super().get_queryset()

    def get_object(self, is_get=False):
        logger.info(
            f"get_object 호출: is_get={is_get}, user={self.get_queryset().first().name}")
        user_id = self.request.user.id
        cached_data = CacheAside.get(user_id)
        if cached_data and is_get:
            logger.info(f"캐시 get_object 히트: user_profile:{user_id}")
            return cached_data
        else:
            if not (obj := self.get_queryset().first()):
                obj = UserProfile.objects.create(user=self.request.user)
            self.check_object_permissions(self.request, obj)
        if is_get:
            serializer = self.get_serializer(obj)
            CacheAside.set(user_id, serializer.data)
            return serializer.data
        return obj

    def retrieve(self, request, *args, **kwargs):
        user_profile = self.get_object(is_get=True)
        return Response(user_profile)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        updated = UserProfileService.update_user_profile(
            instance, serializer.validated_data)
        updated_serializer = self.get_serializer(updated)
        CacheAside.set(request.user.id, updated_serializer.data)
        return Response(updated_serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        refresh_token_value = request.COOKIES.get('refresh_token')
        CacheAside.delete(request.user.id)
        RevokeTokenService.revoke_refresh_token(
            refresh_token_value, request.user.id)

        response = Response(
            {"message": "리프레시 토큰이 성공적으로 무효화되었습니다."},
            status=status.HTTP_200_OK
        )
        response.delete_cookie('refresh_token')
        UserProfileService.delete_user_profile(
            profile_instance=instance, user_id=request.user.id)
        return Response(status=status.HTTP_204_NO_CONTENT)
