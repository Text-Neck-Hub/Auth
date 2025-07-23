from rest_framework import serializers
from ..models import UserProfile
from ..services.user_profile_service import UserProfileService


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    uid = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'username',
            'email',
            'name',
            'bio',
            'location',
            'profile_picture',
            'uid'
        ]
        read_only_fields = [
            'id',
            'username',
            'email',
            'uid'
        ]

    def get_uid(self, obj: UserProfile) -> str | None:
        return UserProfileService.get_user_profile_data(obj)
