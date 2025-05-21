from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search, name='search'),
    path('search/result', views.search_view, name='search_result'),
]