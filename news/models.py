from django.db import models


class Source(models.Model):
    slug = models.SlugField(allow_unicode=True, unique=True)
    title = models.CharField(max_length=100)
    image = models.ImageField(null=True)
    description = models.TextField()
    website = models.URLField()


class SourceCategory(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)


class PostTag(models.Model):
    tag = models.CharField(max_length=30, unique=True)


class Post(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    category = models.ForeignKey(SourceCategory, on_delete=models.CASCADE)
    tags = models.ManyToManyField(PostTag)
    slug = models.SlugField(allow_unicode=True, unique=True)
    title = models.CharField(max_length=1024)
    description = models.TextField()
    image = models.ImageField(null=True)
    detail_url = models.URLField()
    body = models.TextField()
    timestamp = models.DateTimeField()


class Comment(models.Model):
    slug = models.SlugField(allow_unicode=True, unique=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    body = models.TextField()
    timestamp = models.DateTimeField()
