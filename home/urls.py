from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('<slug:categoria_slug>/<slug:assunto_slug>/', 
         views.assunto_detail, 
         name='assunto_detail'),
]