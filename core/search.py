from django.db.models import Q, Count
from datetime import datetime
from posts.models import Postagem as Post
from home.models import Categoria, Assunto
from django.contrib.auth import get_user_model

User = get_user_model()  # This will get accounts.Usuario

def search_posts(
    termo=None,
    apenas_titulo=False,
    autor=None,
    data_inicio=None,
    data_fim=None,
    min_respostas=0,
    prefixos=None,
    subforum=None,
    incluir_subforuns=True,
    ordenacao='relevance'
):
    """
    Realiza pesquisa nos posts do fórum com base em vários critérios.
    
    Parâmetros:
    - termo: Palavras-chave para pesquisa em título e conteúdo
    - apenas_titulo: Se True, pesquisa apenas no título
    - autor: Nome de usuário do autor
    - data_inicio: Data inicial para filtro
    - data_fim: Data final para filtro
    - min_respostas: Número mínimo de respostas
    - prefixos: Tags do sistema para filtrar
    - subforum: Nome do subforum para pesquisar
    - incluir_subforuns: Se True, inclui subforuns do fórum especificado
    - ordenacao: Método de ordenação ('relevance', 'date', 'replies')
    
    Retorna:
    - Queryset de posts filtrados
    """
    # Iniciar com todos os posts
    query = Post.objects.all()
    
    # Filtrar por palavras-chave
    if termo:
        keyword_list = termo.split()
        keyword_query = Q()
        for keyword in keyword_list:
            if apenas_titulo:
                keyword_query |= Q(titulo__icontains=keyword)
            else:
                keyword_query |= Q(titulo__icontains=keyword) | Q(conteudo__icontains=keyword)
        query = query.filter(keyword_query)
    
    # Filtrar por autor (melhorado para pesquisa exata de membro)
    if autor:
        # Pesquisa exata por username ou parcial
        query = query.filter(
            Q(autor__username__iexact=autor) | 
            Q(autor__username__icontains=autor) |
            Q(autor__first_name__icontains=autor) |
            Q(autor__last_name__icontains=autor)
        )
    
    # Filtrar por data
    if data_inicio:
        try:
            data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d").date()
            query = query.filter(criado_em__date__gte=data_inicio)
        except (ValueError, TypeError):
            pass
            
    if data_fim:
        try:
            data_fim = datetime.strptime(data_fim, "%Y-%m-%d").date()
            query = query.filter(criado_em__date__lte=data_fim)
        except (ValueError, TypeError):
            pass
    
    # Filtrar por número mínimo de respostas
    if min_respostas and min_respostas > 0:
        query = query.filter(respostas_count__gte=min_respostas)
    
    # Filtrar por prefixos (tags do sistema)
    if prefixos:
        prefixo_list = [p.strip() for p in prefixos.replace('[', '').replace(']', '').split(',')]
        if prefixo_list:
            query = query.filter(tag_sistema__nome__in=prefixo_list)

    # Filtrar por subforum
    if subforum:
        if incluir_subforuns:
            query = query.filter(assunto__nome__icontains=subforum)
        else:
            query = query.filter(assunto__nome__exact=subforum)
    
    # Ordenar resultados
    if ordenacao == 'date':
        query = query.order_by('-criado_em')
    elif ordenacao == 'replies':
        query = query.order_by('-respostas_count')
    elif ordenacao == 'relevance':
        # Ordenação por relevância pode ser customizada
        # Por padrão, vamos ordenar por data
        query = query.order_by('-criado_em')
    
    return query.select_related('autor', 'assunto', 'assunto__categoria').annotate(
        respostas_count=Count('replies', distinct=True)
    )

def search_users(
    username=None,
    email=None,
    data_registro_inicio=None,
    data_registro_fim=None,
    ordenacao='username'
):
    """
    Realiza pesquisa de usuários no fórum.
    
    Parâmetros:
    - username: Nome de usuário para pesquisa
    - email: Email para pesquisa (apenas para admins)
    - data_registro_inicio: Data inicial de registro
    - data_registro_fim: Data final de registro
    - ordenacao: Método de ordenação ('username', 'date_joined', 'posts_count')
    
    Retorna:
    - Queryset de usuários filtrados
    """
    query = User.objects.filter(is_active=True)
    
    # Filtrar por username
    if username:
        query = query.filter(
            Q(username__icontains=username) |
            Q(first_name__icontains=username) |
            Q(last_name__icontains=username)
        )
    
    # Filtrar por email (cuidado com privacidade)
    if email:
        query = query.filter(email__icontains=email)
    
    # Filtrar por data de registro
    if data_registro_inicio:
        try:
            data_inicio = datetime.strptime(data_registro_inicio, "%Y-%m-%d").date()
            query = query.filter(date_joined__date__gte=data_inicio)
        except (ValueError, TypeError):
            pass
            
    if data_registro_fim:
        try:
            data_fim = datetime.strptime(data_registro_fim, "%Y-%m-%d").date()
            query = query.filter(date_joined__date__lte=data_fim)
        except (ValueError, TypeError):
            pass
    
    # Tentar diferentes nomes de relacionamento para contar posts
    try:
        # Usar o related_name correto baseado no modelo Post
        query = query.annotate(posts_count=Count('postagem', distinct=True))
    except:
        try:
            # Fallback usando subquery
            from django.db.models import OuterRef, Subquery
            from posts.models import Postagem
            subquery = Postagem.objects.filter(autor=OuterRef('pk')).aggregate(count=Count('id'))
            query = query.extra(select={'posts_count': '(SELECT COUNT(*) FROM posts_postagem WHERE autor_id = accounts_usuario.id)'})
        except:
            # Se nada funcionar, adiciona um valor padrão
            query = query.extra(select={'posts_count': '0'})
    
    # Ordenar resultados
    if ordenacao == 'date_joined':
        query = query.order_by('-date_joined')
    elif ordenacao == 'posts_count':
        query = query.order_by('-posts_count')
    else:  # username
        query = query.order_by('username')
    
    return query.select_related()

def search_member_posts(
    username=None,
    tipo_conteudo='todos',
    data_inicio=None,
    data_fim=None,
    subforum=None,
    ordenacao='date'
):
    """
    Realiza pesquisa de postagens de um membro específico.
    
    Parâmetros:
    - username: Nome de usuário para pesquisa
    - tipo_conteudo: Tipo de conteúdo ('todos', 'THREAD', 'POST')
    - data_inicio: Data inicial para filtro
    - data_fim: Data final para filtro
    - subforum: Nome do subforum para pesquisar
    - ordenacao: Método de ordenação ('date', 'replies', 'views')
    
    Retorna:
    - Tuple (queryset de posts filtrados, objeto usuário encontrado)
    """
    # Primeiro, tentar encontrar o usuário
    membro_encontrado = None
    try:
        membro_encontrado = User.objects.get(
            Q(username__iexact=username) |
            Q(username__icontains=username)
        )
    except User.DoesNotExist:
        return None, None
    except User.MultipleObjectsReturned:
        # Se há múltiplos, pegar o que tem match exato primeiro
        membro_encontrado = User.objects.filter(username__iexact=username).first()
        if not membro_encontrado:
            membro_encontrado = User.objects.filter(username__icontains=username).first()
    
    if not membro_encontrado:
        return None, None
    
    # Buscar posts do membro
    query = Post.objects.filter(autor=membro_encontrado)
    
    # Filtrar por tipo de conteúdo
    if tipo_conteudo != 'todos':
        query = query.filter(tipo=tipo_conteudo)
    
    # Filtrar por data
    if data_inicio:
        try:
            data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d").date()
            query = query.filter(criado_em__date__gte=data_inicio)
        except (ValueError, TypeError):
            pass
            
    if data_fim:
        try:
            data_fim = datetime.strptime(data_fim, "%Y-%m-%d").date()
            query = query.filter(criado_em__date__lte=data_fim)
        except (ValueError, TypeError):
            pass
    
    # Filtrar por subforum
    if subforum:
        query = query.filter(assunto__nome__icontains=subforum)
    
    # Anotar com contagem de respostas
    query = query.annotate(respostas_count=Count('replies', distinct=True))
    
    # Ordenar resultados
    if ordenacao == 'replies':
        query = query.order_by('-respostas_count')
    elif ordenacao == 'views':
        query = query.order_by('-visualizacoes')
    else:  # date
        query = query.order_by('-criado_em')
    
    return query.select_related('autor', 'assunto', 'assunto__categoria'), membro_encontrado