from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('news/', 'news.urls'),
    path('users/', 'users.urls'),
    path('admin/', admin.site.urls),
]
