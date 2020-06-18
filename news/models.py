from django.db import models


class Source(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(null=True)
    description = models.TextField()
    website = models.URLField()

    def __str__(self):
        return self.title


class Category(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class PostTag(models.Model):
    tag = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.tag


class Post(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(PostTag)
    title = models.CharField(max_length=1024)
    description = models.TextField()
    image = models.ImageField(null=True)
    detail_url = models.URLField()
    body = models.TextField()
    timestamp = models.DateTimeField(null=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    # user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    body = models.TextField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return self.title
