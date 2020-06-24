from django.urls import path

urlpatterns = [
    path('news-feed/', view=None, name='feed'),
    path('posts/<slug:post>/', view=None, name='post-detail'),
    path('posts/<slug:post>/comments/', view=None, name='comments-list'),
    path('posts/<slug:post>/comments/<slug:comment>', view=None, name='comment-detail'),
    path('catergories/', view=None, name='categories'),
    path('sources/', view=None, name='sources'),
    path('sources/<slug:source>/', view=None, name='source-detail'),
    path('sources/<slug:source>/categories/posts', view=None, name='source-posts')
]
