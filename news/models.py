import random
import re
import string

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify


def rand_slug():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))


def _slug_strip(value):
    """removes the '-' separator from the end or start of the string"""
    return re.sub(r'^%s+|%s+$' % ('-', '-'), '', value)


def unique_slugify(instance, value):
    """function used to give a unique slug to an instance"""

    slug = slugify(value, allow_unicode=True)
    slug = slug[:255]  # limit its len to max_length of slug field

    slug = _slug_strip(slug)
    original_slug = slug

    queryset = instance.__class__.objects.all()

    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    _next = 2
    while not slug or queryset.filter(slug=slug):
        slug = original_slug
        end = '-%s' % _next
        if len(slug) + len(end) > 255:
            slug = slug[:255 - len(end)]
            slug = _slug_strip(slug)
        slug = '%s%s' % (slug, end)
        _next += 1

    return slug


class Source(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(null=True)
    description = models.TextField()
    website = models.URLField()

    def __str__(self):
        return self.title


class Category(models.Model):
    title = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.title


class PostTag(models.Model):
    tag = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.tag


class Post(models.Model):
    slug = models.SlugField(allow_unicode=True, db_index=True, unique=True, max_length=255)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts')
    tags = models.ManyToManyField(PostTag, related_name='posts')
    title = models.CharField(max_length=1024)
    description = models.TextField()
    image = models.ImageField(null=True)
    detail_url = models.URLField()
    body = models.TextField()
    timestamp = models.DateTimeField(null=True)

    def save(self, **kwargs):
        self.slug = unique_slugify(self, self.title)

        return super().save(**kwargs)

    def __str__(self):
        return self.title


class Comment(models.Model):
    slug = models.SlugField(allow_unicode=True, db_index=True, unique=True, max_length=6)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, **kwargs):
        while self.post.comments.filter(slug=self.slug) or self.slug == '':
            self.slug = rand_slug()

        return super().save(**kwargs)

    def __str__(self):
        return self.text
