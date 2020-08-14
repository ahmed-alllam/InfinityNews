from rest_framework import serializers

from news.models import Post, Source, Comment, Category
from users.serializers import UserProfileSerializer


class CategorySerializer(serializers.ModelSerializer):
    is_favourited_by_user = serializers.SerializerMethodField()

    class Meta:
        fields = ('slug', 'title', 'sort', 'image', 'is_favourited_by_user')
        model = Category

    def get_is_favourited_by_user(self, category):
        user = self.context.get('request').user
        if user.is_authenticated:
            return category.is_favourited_by_user(user)
        return False


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('title', 'image')
        model = Source


class SourceDetailSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)

    class Meta:
        fields = ('title', 'image', 'description', 'website', 'categories')
        model = Source


class PostSerializer(serializers.ModelSerializer):
    source = SourceSerializer()
    category = CategorySerializer()

    class Meta:
        fields = ('slug', 'source', 'category', 'title',
                  'description', 'image', 'timestamp')
        model = Post


class PostDetailSerializer(serializers.ModelSerializer):
    source = SourceSerializer()
    category = CategorySerializer()
    tags = serializers.StringRelatedField(many=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ('source', 'category', 'title', 'detail_url', 'body', 'description',
                  'image', 'timestamp', 'comments_count', 'tags')
        model = Post


class CommentSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta:
        fields = ('slug', 'user', 'text', 'timestamp')
        model = Comment
        extra_kwargs = {
            'slug': {
                'read_only': True
            }
        }

    def create(self, validated_data):
        post = Post.objects.get(slug=self.context['view'].kwargs.get('post'))
        user = self.context['request'].user

        return Comment.objects.create(post=post, user=user, **validated_data)
