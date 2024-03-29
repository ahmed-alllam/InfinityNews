from django.contrib.auth import get_user_model
from django.db import models

from core.utils import unique_slugify


class Source(models.Model):
    sort = models.SmallAutoField(primary_key=True)
    slug = models.SlugField(max_length=255)
    title = models.CharField(max_length=100)
    image = models.ImageField(null=True)
    description = models.TextField()
    website = models.URLField(blank=True)

    class Meta:
        ordering = ('sort',)

    @property
    def categories(self):
        return Category.objects.filter(pk__in=self.posts.values_list('category', flat=True)
                                       .distinct())

    def save(self, **kwargs):
        self.slug = unique_slugify(self, value=self.title)

        return super().save(**kwargs)

    def __str__(self):
        return self.title


class Category(models.Model):
    sort = models.SmallAutoField(primary_key=True)
    image = models.ImageField()
    slug = models.SlugField(max_length=100)
    title = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ('sort',)

    def save(self, **kwargs):
        self.slug = unique_slugify(self, value=self.title, max_length=100)

        return super().save(**kwargs)

    def is_favourited_by_user(self, user):
        return user.favourite_categories.filter(slug=self.slug).exists()

    def __str__(self):
        return self.title


class PostTag(models.Model):
    tag = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.tag


class Post(models.Model):
    slug = models.SlugField(allow_unicode=True, db_index=True, unique=True, max_length=1024)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts')
    tags = models.ManyToManyField(PostTag, related_name='posts')
    title = models.CharField(max_length=1024)
    description = models.TextField()
    thumbnail = models.URLField(null=True, max_length=2048)
    full_image = models.URLField(null=True, max_length=2048)
    detail_url = models.URLField(max_length=2048)
    body = models.TextField()
    timestamp = models.DateTimeField(null=True)

    class Meta:
        ordering = ('-timestamp',)

    def save(self, **kwargs):
        self.slug = unique_slugify(self, value=self.title)

        return super().save(**kwargs)

    def __str__(self):
        return self.title

    @property
    def comments_count(self):
        return self.comments.count()


class Comment(models.Model):
    slug = models.SlugField(allow_unicode=True, db_index=True, max_length=15)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-timestamp',)
        unique_together = ('slug', 'post',)

    def save(self, **kwargs):
        self.slug = unique_slugify(self, self.post.comments.all(), max_length=15)

        return super().save(**kwargs)

    def __str__(self):
        return self.text
