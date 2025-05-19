from django.db.models import Count
from posts.models import Postagem
from django.contrib.auth import get_user_model
from .models import UltimaAtividade, Pesquisa

def forum_stats(request):
    """Context processor para estatísticas do fórum"""
    User = get_user_model()
    
    return {
        'trending_posts': Postagem.objects.select_related(
            'autor', 
            'assunto'
        ).order_by('-visualizacoes')[:5],
        
        'recent_posts': Postagem.objects.select_related(
            'autor', 
            'assunto'
        ).order_by('-criado_em')[:5],
        
        'forum_stats': {
            'total_topics': Postagem.objects.filter(tipo='THREAD').count(),
            'total_posts': Postagem.objects.count(),
            'total_members': User.objects.count(),
            'newest_member': User.objects.order_by('-date_joined').first(),
        }
    }

def atividades_recentes(request):
    """Context processor para fornecer últimas atividades e pesquisas aos templates"""
    context = {
        'ultimas_atividades': UltimaAtividade.objects.select_related(
            'usuario',
            'postagem',
            'reacao'
        ).all()[:10],
        
        'novos_posts': UltimaAtividade.objects.select_related(
            'usuario',
            'postagem'
        ).filter(
            tipo='NOVO_POST'
        )[:5],
        
        'novas_replies': UltimaAtividade.objects.select_related(
            'usuario',
            'postagem'
        ).filter(
            tipo='NOVA_REPLY'
        )[:5]
    }

    if request.user.is_authenticated:
        context['pesquisas_recentes'] = Pesquisa.objects.filter(
            usuario=request.user
        ).order_by('-criado_em')[:5]

    return context