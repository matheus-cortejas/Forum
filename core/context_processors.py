from django.db.models import Count
from posts.models import Postagem
from django.contrib.auth import get_user_model
from .models import UltimaAtividade, Pesquisa

def forum_stats(request):
    """Context processor para estatísticas do fórum"""
    User = get_user_model()
    
    online_record = 8000

    # Simulação de usuários online
    online_members = [
        {'username': 'Admin1', 'role': 'admin'},
        {'username': 'Mod1', 'role': 'moderator'},
        {'username': 'VIPUser', 'role': 'vip'},
        {'username': 'RegularUser', 'role': 'user'},
    ]
    online_guests = 45  # Simulado

    return {
        'trending_threads': Postagem.objects.filter(tipo='THREAD').select_related('autor', 'assunto').order_by('-visualizacoes')[:5],
        'recent_posts': Postagem.objects.filter(tipo='POST').select_related('autor', 'assunto').order_by('-criado_em')[:5],
        'forum_stats': {
            'total_topics': Postagem.objects.filter(tipo='THREAD').count(),
            'total_posts': Postagem.objects.filter(tipo='POST').count(),
            'total_members': User.objects.count(),
            'newest_member': User.objects.order_by('-date_joined').first(),
            'online_record': online_record,
            'online_members': online_members,
            'online_guests': online_guests,
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