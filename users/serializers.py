from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from core.utils import generate_random_username


class UserProfileSerializer(serializers.ModelSerializer):
    is_guest = serializers.BooleanField()

    class Meta:
        fields = ('username', 'first_name', 'last_name', 'password', 'profile_photo', 'is_guest')
        model = get_user_model()
        extra_kwargs = {
            'username': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'password': {
                'write_only': True, 'min_length': 8, 'required': False
            },
        }

    def validate(self, attrs):
        if not attrs.get("is_guest", False):
            if not attrs.get("username", "") or not attrs.get("password", "") \
                or not attrs.get("first_name", "") or not attrs.get("last_name", ""):
                raise serializers.ValidationError()

        return attrs

    def create(self, validated_data):
        if validated_data.pop('is_guest', False):
            validated_data['username'] = generate_random_username()
        user = get_user_model().objects.create_user(**validated_data)
        return user


class AuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(
        style={
            'input_type': 'password'
        },
        trim_whitespace=False,
        required=False
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password' or None)

        user = authenticate(
            request=self.context.get('request'),
            username=username,
            password=password
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            print(username)
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
