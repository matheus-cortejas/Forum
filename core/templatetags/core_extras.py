from django import template
from django.utils import timezone
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def tempo_relativo(value):
    """Retorna tempo em formato relativo mais detalhado"""
    if not value:
        return ''
    
    agora = timezone.now()
    if isinstance(value, datetime):
        diff = agora - value
    else:
        return value
    
    segundos = diff.total_seconds()
    
    # Menos de 1 minuto
    if segundos < 60:
        return 'agora mesmo'
    
    # Menos de 1 hora
    elif segundos < 3600:
        minutos = int(segundos // 60)
        if minutos == 1:
            return '1 minuto atrás'
        return f'{minutos} minutos atrás'
    
    # Menos de 1 dia
    elif segundos < 86400:
        horas = int(segundos // 3600)
        if horas == 1:
            return '1 hora atrás'
        return f'{horas} horas atrás'
    
    # Menos de 1 semana
    elif diff.days < 7:
        if diff.days == 1:
            return 'ontem'
        return f'{diff.days} dias atrás'
    
    # Menos de 1 mês
    elif diff.days < 30:
        semanas = diff.days // 7
        if semanas == 1:
            return '1 semana atrás'
        return f'{semanas} semanas atrás'
    
    # Menos de 1 ano
    elif diff.days < 365:
        meses = diff.days // 30
        if meses == 1:
            return '1 mês atrás'
        return f'{meses} meses atrás'
    
    # Mais de 1 ano
    else:
        anos = diff.days // 365
        if anos == 1:
            return '1 ano atrás'
        return f'{anos} anos atrás'

@register.filter
def get_user_role_display(user):
    """Retorna o papel do usuário de forma amigável"""
    if user.is_staff:
        return 'Staff'
    if user.groups.filter(name='Moderadores').exists():
        return 'Moderador'
    return 'Membro'

@register.filter
def get_user_role_class(user):
    """Retorna a classe CSS para o papel do usuário"""
    if user.is_staff:
        return 'user-staff'
    if user.groups.filter(name='Moderadores').exists():
        return 'user-moderator'
    return 'user-member'

@register.inclusion_tag('core/widgets/atividades_widget.html')
def atividades_recentes_widget(limit=5):
    """Widget com as atividades mais recentes"""
    from core.models import UltimaAtividade
    
    atividades_recentes = UltimaAtividade.objects.select_related(
        'usuario', 'postagem', 'reply', 'reacao',
        'postagem__assunto', 'postagem__autor'
    ).order_by('-criado_em')[:limit]
    
    return {
        'atividades_recentes': atividades_recentes
    }
