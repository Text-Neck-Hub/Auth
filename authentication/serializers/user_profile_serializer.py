from rest_framework import serializers
from ..models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'name', 'bio', 'location', 'profile_picture']
        read_only_fields = ['id', 'user']
