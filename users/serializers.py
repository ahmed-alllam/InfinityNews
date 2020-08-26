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

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, user, validated_data):
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')
        profile_photo = validated_data.get('profile_photo', None)

        user.first_name = first_name
        user.last_name = last_name
        user.profile_photo = profile_photo

        user.save()

        return user
