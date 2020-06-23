from rest_framework import serializers

from users.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('username', 'first_name', 'last_name', 'password')
        model = UserProfile
        extra_kwargs = {'password': {'write_only': True}}
