from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Filtro para obter item de dicionário de forma segura
    Uso: {{ dict|get_item:key }}
    """
    if not dictionary:
        return None
    
    try:
        if isinstance(key, str) and key.isdigit():
            key = int(key)
        elif hasattr(key, 'id'):
            key = key.id
        
        return dictionary.get(key, None)
    except (AttributeError, TypeError, ValueError):
        return None

@register.filter
def get_reaction_id(user_reaction):
    """
    Filtro auxiliar para obter ID da reação de forma segura
    """
    if user_reaction and hasattr(user_reaction, 'reacao') and user_reaction.reacao:
        return user_reaction.reacao.id
    return None

@register.filter
def has_user_reaction(reactions_dict, reply_id):
    """
    Verifica se usuário tem reação para uma reply específica
    """
    if not reactions_dict:
        return False
    
    try:
        key = int(reply_id) if isinstance(reply_id, str) else reply_id
        return key in reactions_dict and reactions_dict[key] is not None
    except (ValueError, TypeError):
        return False