from rest_framework import generics, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import GenericViewSet

from news import serializers
from news.models import Post, Category, Source, Comment
from news.pagination import TimeStampCursorPagination, SortCursorPagination
from news.permissions import IsOwner


class CategoryPostsView(generics.ListAPIView):
    serializer_class = serializers.PostSerializer
    pagination_class = TimeStampCursorPagination
    authentication_classes = (TokenAuthentication,)
    lookup_url_kwarg = 'category'
    queryset = Post.objects.all()

    def filter_queryset(self, queryset):
        return queryset.filter(category__slug=self.kwargs[self.lookup_url_kwarg])


class PostDetailView(generics.RetrieveAPIView):
    lookup_field = 'slug'
    lookup_url_kwarg = 'post'
    serializer_class = serializers.PostDetailSerializer
    queryset = Post.objects.all()


class CategoriesListView(generics.ListAPIView):
    serializer_class = serializers.CategorySerializer
    authentication_classes = (TokenAuthentication,)
    pagination_class = SortCursorPagination
    queryset = Category.objects.all()


class SourcesListView(generics.ListAPIView):
    serializer_class = serializers.SourceSerializer
    pagination_class = SortCursorPagination
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

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset.filter(post__slug=self.kwargs.get('post', '')))


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
