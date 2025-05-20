from django.urls import path
from . import views

urlpatterns = [
    path('threads/', views.threads, name='threads'),  # Página de tópicos com filtros
    path('posts/', views.posts, name='posts'),        # Página de posts com filtros
    path('threads/novos', views.recent_threads, name='recent_threads'),  # Novos tópicos
    path('posts/novos', views.recent_posts, name='recent_posts'),        # Novos posts
    path('novidades/', views.ultimas_atividades, name='novidades'),  # Feed de atividades
    path('<str:categoria_slug>/<str:assunto_slug>/thread/<int:postagem_id>/', views.postagem_detail, name='postagem_detail'),

    path('<str:categoria_slug>/<str:assunto_slug>/thread/<int:thread_id>/reply/', 
         views.add_reply, 
         name='add_reply'),
    path('<str:categoria_slug>/<str:assunto_slug>/thread/<int:postagem_id>/react/', 
         views.add_reaction, 
         name='add_reaction'),
]
