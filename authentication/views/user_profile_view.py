from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from ..models import UserProfile
from ..serializers.user_profile_serializer import UserProfileSerializer
from ..services.user_profile_service import UserProfileService

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
        if self.action in ['retrieve', 'partial_update', 'destroy'] and 'pk' not in self.kwargs:
            return UserProfile.objects.filter(user=self.request.user)
        return super().get_queryset()

    def get_object(self):
        obj = None
        if self.action in ['retrieve', 'partial_update', 'destroy'] and 'pk' not in self.kwargs:
            obj = self.get_queryset().first()
            if not obj:
                obj = UserProfile.objects.create(user=self.request.user)
        else:
            obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_update(self, serializer):
        UserProfileService.update_user_profile(
            serializer.instance, serializer.validated_data)

    def perform_destroy(self, instance):
        UserProfileService.delete_user_profile(instance)
