from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.inclusion_tag('accounts/widgets/online_users_widget.html')
def online_users_widget(limit=5):
    """
    Template tag para exibir widget de usuários online
    Uso: {% load online_tags %}{% online_users_widget 10 %}
    """
    try:
        from accounts.models import UsuarioOnline
        
        # Tempo limite para considerar online (15 minutos)
        cutoff_time = timezone.now() - timedelta(minutes=15)
        
        # Buscar usuários online
        online_users = UsuarioOnline.objects.filter(
            ultima_atividade__gte=cutoff_time
        ).select_related('usuario').order_by('-ultima_atividade')[:limit]
        
        # Separar por categoria
        members = []
        guests = []
        bots = []
        
        for user_online in online_users:
            if user_online.is_bot:
                bots.append(user_online)
            elif user_online.usuario:
                members.append(user_online)
            else:
                guests.append(user_online)
        
        return {
            'members': members,
            'guests': guests,
            'bots': bots,
            'total_count': len(online_users),
        }
    except ImportError:
        return {
            'members': [],
            'guests': [],
            'bots': [],
            'total_count': 0,
        }

@register.simple_tag
def online_count():
    """
    Tag simples para retornar o número total de usuários online
    Uso: {% load online_tags %}{% online_count %}
    """
    try:
        from accounts.models import UsuarioOnline
        
        cutoff_time = timezone.now() - timedelta(minutes=15)
        return UsuarioOnline.objects.filter(ultima_atividade__gte=cutoff_time).count()
    except ImportError:
        return 0

@register.simple_tag
def members_online_count():
    """
    Tag para retornar o número de membros online
    """
    try:
        from accounts.models import UsuarioOnline
        
        cutoff_time = timezone.now() - timedelta(minutes=15)
        return UsuarioOnline.objects.filter(
            ultima_atividade__gte=cutoff_time,
            is_authenticated=True,
            is_bot=False
        ).count()
    except ImportError:
        return 0

@register.filter
def time_since_activity(activity_time):
    """
    Filtro para formatar tempo desde última atividade
    """
    if not activity_time:
        return "desconhecido"
    
    time_diff = timezone.now() - activity_time
    
    if time_diff.total_seconds() < 60:
        return "agora mesmo"
    elif time_diff.total_seconds() < 3600:
        minutes = int(time_diff.total_seconds() / 60)
        return f"{minutes} min atrás"
    elif time_diff.total_seconds() < 86400:
        hours = int(time_diff.total_seconds() / 3600)
        return f"{hours}h atrás"
    else:
        days = int(time_diff.total_seconds() / 86400)
        return f"{days}d atrás"
