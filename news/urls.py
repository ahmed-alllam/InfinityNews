from django.urls import path

from news import views

urlpatterns = [
    path('posts/<post>/', view=views.PostDetailView.as_view(), name='post-detail'),
    path('posts/<post>/comments/', view=views.CommentsView.as_view(
        {'get': 'list', 'post': 'create'}), name='comments-list'
         ),
    path('posts/<post>/comments/<comment>/', view=views.CommentsView.as_view(
        {'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='comment-detail'
         ),
    path('categories/', view=views.CategoriesListView.as_view(), name='categories'),
    path('categories/<category>/posts/', view=views.CategoryPostsView.as_view(),
         name='category-posts'),
    path('sources/', view=views.SourcesListView.as_view(), name='sources'),
    path('sources/<source>/', view=views.SourceDetailView.as_view(), name='source-detail'),
    path('sources/<source>/categories/<category>/posts/',
         view=views.SourcePostsView.as_view(), name='source-posts')
]
