from rest_framework import serializers

from news.models import Post, Source, Comment, Category


class CategorySerializer(serializers.ModelSerializer):
    is_favourited_by_user = serializers.SerializerMethodField()

    class Meta:
        fields = ('slug', 'title', 'image', 'is_favourited_by_user')
        model = Category

    def get_is_favourited_by_user(self, category):
        user = self.context.get('request')['user']
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

    class Meta:
        exclude = ('id',)
        model = Post


class CommentSerializer(serializers.ModelField):
    # user = UserProfileSerializer()
    class Meta:
        fields = ('slug', 'user', 'text', 'timestamp')
        model = Comment
