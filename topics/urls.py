from django.urls import path
from . import views

urlpatterns = [
    path('', views.topicos, name='topicos'),
    path('novos/', views.novos_topicos, name='novos_topicos'),
]
