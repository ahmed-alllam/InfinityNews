from rest_framework import serializers

from news.models import Post, Source


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('title', 'image')
        model = Source


class SourceDetailSerializer(serializers.ModelSerializer):
    categories = serializers.StringRelatedField(many=True)

    class Meta:
        fields = ('title', 'image', 'description', 'website', 'categories')
        model = Source


class PostSerializer(serializers.ModelSerializer):
    source = SourceSerializer()
    category = serializers.StringRelatedField()

    class Meta:
        fields = ('slug', 'source', 'category', 'title',
                  'description', 'image', 'timestamp')
        model = Post


class PostDetailSerializer(serializers.ModelSerializer):
    source = SourceSerializer()
    category = serializers.StringRelatedField()
    tags = serializers.StringRelatedField(many=True)

    class Meta:
        exclude = ('id',)
        model = Post
