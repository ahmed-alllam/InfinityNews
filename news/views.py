from django.db.models import Count
from rest_framework import generics, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from news.models import Post, Category, Source, Comment
from news.permissions import IsOwner
from news.serializers import PostSerializer, PostDetailSerializer, CategorySerializer, SourceSerializer, \
    CommentSerializer, SourceDetailSerializer


class NewsFeedView(generics.ListAPIView):
    serializer_class = PostSerializer
    pagination_class = LimitOffsetPagination  # todo: change it to Cursor-based Pagignation
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
    serializer_class = PostDetailSerializer
    queryset = Post.objects.all()


class CategoriesListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    pagination_class = LimitOffsetPagination  # todo: change it to Cursor-based Pagignation
    queryset = Category.objects.all()

    def filter_queryset(self, queryset):
        queryset.annotate(count=Count('posts')).order_by('-count')


class SourcesListView(generics.ListAPIView):
    serializer_class = SourceSerializer
    pagination_class = LimitOffsetPagination  # todo: change it to Cursor-based Pagignation
    queryset = Source.objects.all()


class CommentsView(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   GenericViewSet):
    lookup_field = 'slug'
    lookup_url_kwarg = 'comment'
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwner)


class SourceDetailView(generics.RetrieveAPIView):
    lookup_field = 'slug'
    lookup_url_kwarg = 'source'
    serializer_class = SourceDetailSerializer
    queryset = Source.objects.all()


class SourcePostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    pagination_class = LimitOffsetPagination  # todo: change it to Cursor-based Pagignation
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
