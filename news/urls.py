from django.urls import path

from news import views

urlpatterns = [
    path('posts/<slug:post>/', view=views.PostDetailView.as_view(), name='post-detail'),
    path('posts/<slug:post>/comments/', view=views.CommentsView.as_view(
        {'get': 'list', 'post': 'create'}), name='comments-list'
         ),
    path('posts/<slug:post>/comments/<slug:comment>', view=views.CommentsView.as_view(
        {'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='comment-detail'
         ),
    path('categories/', view=views.CategoriesListView.as_view(), name='categories'),
    path('categories/<slug:category>/posts', view=views.CategoryPostsView.as_view(),
         name='category-posts'),
    path('sources/', view=views.SourcesListView.as_view(), name='sources'),
    path('sources/<slug:source>/', view=views.SourceDetailView.as_view(), name='source-detail'),
    path('sources/<slug:source>/categories/<slug:category>/posts',
         view=views.SourcePostsView.as_view(), name='source-posts')
]
