from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_page, name='logout_page'),
    path('login/', views.login_page, name='login_page'),
]