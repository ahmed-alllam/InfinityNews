from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('news/', include('news.urls')),
    path('users/', include('users.urls')),
    path('admin/', admin.site.urls),]