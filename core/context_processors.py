from django.db.models import Count
from posts.models import Postagem, Tag, TagEspecifica
from django.contrib.auth import get_user_model
from .models import UltimaAtividade, Pesquisa, OnlineRecord

def forum_stats(request):
    """Context processor para estatísticas do fórum"""
    User = get_user_model()
    
    online_record = OnlineRecord.get_current()

    # Obter usuários online reais
    try:
        from accounts.models import UsuarioOnline
        from django.utils import timezone
        from datetime import timedelta
        
        # Tempo limite para considerar online (15 minutos)
        cutoff_time = timezone.now() - timedelta(minutes=15)
        
        # Buscar usuários autenticados online
        online_members_queryset = UsuarioOnline.objects.filter(
            ultima_atividade__gte=cutoff_time,
            is_authenticated=True,
            is_bot=False,
            usuario__isnull=False
        ).select_related('usuario')[:10]  # Limitar a 10 para performance
        
        # Preparar lista de membros online
        online_members = []
        for user_online in online_members_queryset:
            if user_online.usuario:
                # Determinar role baseado no status do usuário
                if user_online.usuario.is_superuser:
                    role = 'admin'
                elif user_online.usuario.is_staff:
                    role = 'staff'
                elif hasattr(user_online.usuario, 'cargos') and user_online.usuario.cargos.filter(pode_moderar=True).exists():
                    role = 'moderator'
                else:
                    role = 'user'
                
                online_members.append({
                    'username': user_online.usuario.get_display_name(),
                    'role': role,
                    'user_obj': user_online.usuario,
                })
        
        # Contar visitantes online
        online_guests = UsuarioOnline.objects.filter(
            ultima_atividade__gte=cutoff_time,
            is_authenticated=False,
            is_bot=False
        ).count()

        total_online = len(online_members) + online_guests
        online_record = OnlineRecord.update_if_higher(total_online)        
        
    except ImportError:
        # Fallback para dados simulados se o modelo não existir
        online_members = [
            {'username': 'Admin1', 'role': 'admin'},
            {'username': 'Mod1', 'role': 'moderator'},
            {'username': 'VIPUser', 'role': 'vip'},
            {'username': 'RegularUser', 'role': 'user'},
        ]
        online_guests = 45

    return {
        'trending_threads': Postagem.objects.filter(tipo='THREAD').select_related('autor', 'assunto', 'tag_sistema').prefetch_related('tags_especificas').order_by('-visualizacoes')[:5],
        'recent_posts': Postagem.objects.filter(tipo='POST').select_related('autor', 'assunto', 'tag_sistema').prefetch_related('tags_especificas').order_by('-criado_em')[:5],
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

def filtros_forum(request):
    """Context processor para opções de filtro do fórum"""
    User = get_user_model()
    
    # Cache de tags do sistema (baixo volume, alta reutilização)
    tags_sistema = Tag.objects.filter(is_sistema=True).order_by('ordem', 'nome')
    
    # Otimização: buscar apenas autores com postagens e limitar resultados
    autores_com_posts = User.objects.annotate(
        post_count=Count('postagem')
    ).filter(
        post_count__gt=0
    ).order_by('-post_count', 'username')[:50]  # Ordenados por número de posts
    
    # Estatísticas de tags mais usadas
    tags_populares = TagEspecifica.objects.values('nome').annotate(
        count=Count('nome')
    ).order_by('-count')[:10]
    
    return {
        'tipos_filtro': [
            {'value': 'all', 'label': 'Tudo'},
            {'value': 'thread', 'label': 'Threads'},
            {'value': 'post', 'label': 'Posts'},
        ],
        'tags_sistema_filtro': tags_sistema,
        'autores_filtro': autores_com_posts,
        'tags_populares': tags_populares,
        'tipos_organizacao': [
            {'value': 'recente', 'label': 'Mais Recentes'},
            {'value': 'antigo', 'label': 'Mais Antigos'},
            {'value': 'visualizacoes', 'label': 'Mais Visualizados'},
            {'value': 'atividade', 'label': 'Atividade Recente'},
        ]
    }

def online_stats(request):
    """Context processor para estatísticas de usuários online"""
    try:
        from accounts.models import UsuarioOnline
        from django.utils import timezone
        from datetime import timedelta
        
        # Tempo limite para considerar online (15 minutos)
        cutoff_time = timezone.now() - timedelta(minutes=15)
        
        # Contar usuários online por categoria
        online_queryset = UsuarioOnline.objects.filter(ultima_atividade__gte=cutoff_time)
        
        online_stats = {
            'total_online': online_queryset.count(),
            'members_online': online_queryset.filter(is_authenticated=True, is_bot=False).count(),
            'guests_online': online_queryset.filter(is_authenticated=False, is_bot=False).count(),
            'bots_online': online_queryset.filter(is_bot=True).count(),
        }
        
        return {'online_stats': online_stats}
    except:
        # Fallback caso o modelo não exista ainda
        return {
            'online_stats': {
                'total_online': 0,
                'members_online': 0,
                'guests_online': 0,
                'bots_online': 0,
            }
        }