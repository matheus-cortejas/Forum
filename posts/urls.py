from django.urls import path
from . import views

urlpatterns = [
    path('', views.posts, name='posts'),
    path('detail/', views.detail, name='detail'),
    path('novos/', views.novos_posts, name='novos_posts'),
]
