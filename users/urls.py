from django.urls import path

urlpatterns = [
    path('signup/', view=None, name='signup'),
    path('token/', view=None, name='token'),
    path('me/', view=None, name='me'),
    path('<username>/', view=None, name='user-profile'),
]
