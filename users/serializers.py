from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('username', 'first_name', 'last_name', 'password', 'profile_photo')
        model = get_user_model()
        extra_kwargs = {
            'password': {
                'write_only': True, 'min_length': 8
            },
        }
