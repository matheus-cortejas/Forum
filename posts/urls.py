from django.urls import path
from . import views

urlpatterns = [
    path('', views.posts, name='posts'),
    path('detail/', views.detail, name='detail'),
    path('novos/', views.novos_posts, name='novos_posts'),
    path('', views.topicos, name='topicos'),
    path('novos/', views.novos_topicos, name='novos_topicos'),
]
