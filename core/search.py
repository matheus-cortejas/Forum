from django.db.models import Q
from datetime import datetime
from posts.models import Postagem as Post
from home.models import Categoria, Assunto

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
    
    # Filtrar por autor
    if autor:
        query = query.filter(autor__username__icontains=autor)
    
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
    
    return query.select_related('autor', 'assunto', 'assunto__categoria')