from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import generics, permissions, authentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.settings import api_settings

from news.models import Category
from news.pagination import SortCursorPagination
from news.serializers import CategorySerializer
from users.serializers import UserProfileSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserProfileSerializer


class CreateTokenView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserProfileSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class ReadOnlyUserView(generics.RetrieveAPIView):
    lookup_field = 'username'
    queryset = get_user_model().objects.all()
    serializer_class = UserProfileSerializer


class FavouriteCategoriesView(generics.ListAPIView, generics.UpdateAPIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = SortCursorPagination
    serializer_class = CategorySerializer

    def update(self, request, *args, **kwargs):
        user = request.user
        categories_slugs = request.data.get('categories', [])
        if categories_slugs:
            categories = []
            for category in categories_slugs:
                try:
                    category = Category.objects.get(slug=category)
                    categories.append(category)
                except Category.DoesNotExist:
                    return Response(_("Invalid category slug"), status=404)

            user.favourite_categories.set(categories)
            return Response(status=204)
        else:
            return Response(_("Invalid Data"), status=400)

    def get_queryset(self):
        return self.request.user.favourite_categories.all()
