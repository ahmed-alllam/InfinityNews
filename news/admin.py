from django.contrib import admin

from news.models import Source, Category, PostTag, Post, Comment

admin.site.register(Source)
admin.site.register(Category)
admin.site.register(PostTag)
admin.site.register(Post)
admin.site.register(Comment)
