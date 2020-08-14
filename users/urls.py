from django.urls import path

from users import views

urlpatterns = [
    path('signup/', view=views.CreateUserView.as_view(), name='signup'),
    path('token/', view=views.CreateTokenView.as_view(), name='token'),
    path('me/', view=views.ManageUserView.as_view(), name='me'),
    path('me/favourite-categories/', view=views.FavouriteCategoriesView.as_view(), name='favourite-categories'),
    path('<username>/', view=views.ReadOnlyUserView.as_view(), name='user-profile'),
]
