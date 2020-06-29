from rest_framework import serializers

from news.models import Post, Source, Comment, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        models = Category


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

    class Meta:
        exclude = ('id',)
        model = Post


class CommentSerializer(serializers.ModelField):
    # user = UserProfileSerializer()
    class Meta:
        fields = ('slug', 'user', 'text', 'timestamp')
        model = Comment
