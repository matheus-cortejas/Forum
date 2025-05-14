from django.urls import path
from . import views

urlpatterns = [
    path('logout/', views.logout, name='logout'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('members/', views.members, name='members'),
    path('online/', views.online, name='online'),
    path('profile/', views.profile, name='profile'),
]
