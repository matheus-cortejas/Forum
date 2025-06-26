from django.urls import path
from . import views

urlpatterns = [
    path('novidades/', views.ultimas_atividades, name='novidades'),  # Feed de atividades
    
    # Lista de posts e threads
    path('recent-threads/', views.recent_threads, name='recent_threads'),
    path('recent-posts/', views.recent_posts, name='recent_posts'),
    path('threads/', views.threads, name='threads'),
    path('posts/', views.posts, name='posts'),
    
    # Detalhes de postagem (URLs mais específicas primeiro)
    path('<slug:categoria_slug>/<slug:assunto_slug>/<int:postagem_id>/', 
         views.postagem_detail, name='postagem_detail'),
    path('<slug:categoria_slug>/<slug:assunto_slug>/thread/<int:thread_id>/', 
         views.thread_detail, name='thread_detail'),
    path('<slug:categoria_slug>/<slug:assunto_slug>/post/<int:post_id>/', 
         views.post_detail, name='post_detail'),
    
    # Sistema de reações
    path('<slug:categoria_slug>/<slug:assunto_slug>/<int:postagem_id>/react/', 
         views.add_reaction_postagem, name='add_reaction_postagem'),
    path('reply/<int:reply_id>/react/', 
         views.add_reaction_reply, name='add_reaction_reply'),
    
    # Sistema de replies
    path('<slug:categoria_slug>/<slug:assunto_slug>/<int:postagem_id>/reply/', 
         views.add_reply, name='add_reply'),
]