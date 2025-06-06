from django.urls import path
from . import views

urlpatterns = [
    path('threads/', views.threads, name='threads'),  # Página de tópicos com filtros
    path('posts/', views.posts, name='posts'),        # Página de posts com filtros
    path('novidades/', views.ultimas_atividades, name='novidades'),  # Feed de atividades
    path('<str:categoria_slug>/<str:assunto_slug>/thread/<int:thread_id>/', views.thread_detail, name='thread_detail'),
    path('<str:categoria_slug>/<str:assunto_slug>/post/<int:post_id>/', views.post_detail, name='post_detail'),

    path('<str:categoria_slug>/<str:assunto_slug>/thread/<int:thread_id>/reply/', 
         views.add_reply, 
         name='add_reply'),
    path('<str:categoria_slug>/<str:assunto_slug>/thread/<int:postagem_id>/react/', 
         views.add_reaction, 
         name='add_reaction'),
]
