from rest_framework import generics, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from news import serializers
from news.models import Post, Category, Source, Comment
from news.pagination import TimeStampCursorPagination, PriorityCursorPagination
from news.permissions import IsOwner


class NewsFeedView(generics.ListAPIView):
    serializer_class = serializers.PostSerializer
    pagination_class = TimeStampCursorPagination
    authentication_classes = (TokenAuthentication,)
    queryset = Post.objects.all()

    def filter_queryset(self, queryset):
        user = self.request.user
        if user.is_authenticated:
            queryset.filter(category__in=user.favourite_categories)

        return queryset


class PostDetailView(generics.RetrieveAPIView):
    lookup_field = 'slug'
    lookup_url_kwarg = 'post'
    serializer_class = serializers.PostDetailSerializer
    queryset = Post.objects.all()


class CategoriesListView(generics.ListAPIView):
    serializer_class = serializers.CategorySerializer
    pagination_class = PriorityCursorPagination
    queryset = Category.objects.all()


class SourcesListView(generics.ListAPIView):
    serializer_class = serializers.SourceSerializer
    pagination_class = PriorityCursorPagination
    queryset = Source.objects.all()


class CommentsView(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   GenericViewSet):
    lookup_field = 'slug'
    lookup_url_kwarg = 'comment'
    serializer_class = serializers.CommentSerializer
    pagination_class = TimeStampCursorPagination
    queryset = Comment.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwner)


class SourceDetailView(generics.RetrieveAPIView):
    lookup_field = 'slug'
    lookup_url_kwarg = 'source'
    serializer_class = serializers.SourceDetailSerializer
    queryset = Source.objects.all()


class SourcePostsView(generics.ListAPIView):
    serializer_class = serializers.PostSerializer
    pagination_class = TimeStampCursorPagination
    queryset = Post.objects.all()

    def filter_queryset(self, queryset):
        source_slug = self.kwargs.get('source', '')
        category_slug = self.kwargs.get('category', '')
        return queryset.filter(source__slug=source_slug, category__slug=category_slug)


class CategoryFavouriteView(generics.CreateAPIView,
                            generics.DestroyAPIView):
    lookup_field = 'category'
    lookup_url_kwarg = 'category'
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Category.objects.all()

    def perform_create(self, instance):
        self.request.user.favourite_categories.add(instance)

    def perform_destroy(self, instance):
        self.request.user.favourite_categories.remove(instance)
