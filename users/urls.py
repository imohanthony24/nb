app_name = 'users'
from users.views import *
from django.urls import path
from django.contrib.auth.views import LogoutView

urlpatterns = [
	path('safe-login/',LoginViewUpdated.as_view(),name='login'),
	path('logout/',LogoutView.as_view(),name='logout'),
]