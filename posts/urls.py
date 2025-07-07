from django.urls import path
from . import views

urlpatterns = [
    # Feed de atividades
    path('novidades/', views.ultimas_atividades, name='novidades'),
    
    # Lista de posts e threads
    path('recent-threads/', views.recent_threads, name='recent_threads'),
    path('recent-posts/', views.recent_posts, name='recent_posts'),
    path('threads/', views.threads, name='threads'),
    path('posts/', views.posts, name='posts'),
    
    # API endpoints
    path('api/atividades-stats/', views.ultimas_atividades_stats, name='atividades_stats'),
    
    # Criação de posts
    path('criar/<slug:categoria_slug>/<slug:assunto_slug>/', views.criar_post, name='criar_post'),
    
    # Sistema de reações
    path('<slug:categoria_slug>/<slug:assunto_slug>/<int:postagem_id>/react/', 
         views.add_reaction_postagem, name='add_reaction_postagem'),
    path('reply/<int:reply_id>/react/', 
         views.add_reaction_reply, name='add_reaction_reply'),
    
    # Sistema de replies
    path('<slug:categoria_slug>/<slug:assunto_slug>/<int:postagem_id>/reply/', 
         views.add_reply, name='add_reply'),
    path('reply/edit/<slug:categoria_slug>/<slug:assunto_slug>/<int:reply_id>/', views.edit_reply, name='edit_reply'),
    path('reply/delete/<slug:categoria_slug>/<slug:assunto_slug>/<int:reply_id>/', views.delete_reply, name='delete_reply'),
    
    # View unificada para posts e threads
    path('<slug:categoria_slug>/<slug:assunto_slug>/<int:postagem_id>/', 
         views.postagem_detail, name='postagem_detail'),
    
    # URLs de compatibilidade
    path('<slug:categoria_slug>/<slug:assunto_slug>/thread/<int:thread_id>/', 
         views.thread_detail, name='thread_detail'),
    path('<slug:categoria_slug>/<slug:assunto_slug>/post/<int:post_id>/', 
         views.post_detail, name='post_detail'),
    
    # URLs de edição e deleção (no final para evitar conflitos)
    path('<slug:categoria_slug>/<slug:assunto_slug>/<int:post_id>/editar/', views.editar_post, name='editar_post'),
    path('<slug:categoria_slug>/<slug:assunto_slug>/<int:post_id>/deletar/', views.deletar_post, name='deletar_post'),
]