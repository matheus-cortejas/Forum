from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count, Max, Prefetch
from .models import Categoria, Assunto
from posts.models import Postagem as Post, Reply, Tag, TagEspecifica
from django.contrib.auth import get_user_model

def home(request):
    context = {
        'categorias': Categoria.objects.prefetch_related('assuntos').all()
    }
    return render(request, 'forum/forums.html', context)

def assunto_detail(request, categoria_slug, assunto_slug):
    assunto = get_object_or_404(Assunto, slug=assunto_slug)
    User = get_user_model()
    
    # Parâmetros de filtro
    tipo_filtro = request.GET.get('tipo', 'all')
    prefixo = request.GET.get('prefixo', '')
    tags_usuario = request.GET.get('tags', '')
    iniciada_por = request.GET.get('autor', '')
    tipo_organizacao = request.GET.get('ordem', 'recente')
    page = request.GET.get('page', 1)
    
    # Query base para threads e posts
    queryset = Post.objects.filter(assunto=assunto)
    
    # Filtro por tipo (thread/post/todos)
    if tipo_filtro == 'thread':
        queryset = queryset.filter(tipo='THREAD')
    elif tipo_filtro == 'post':
        queryset = queryset.filter(tipo='POST')
    # Se 'all', não filtra por tipo
    
    # Filtro por prefixo (tag do sistema)
    if prefixo:
        try:
            tag_sistema = Tag.objects.get(slug=prefixo, is_sistema=True)
            queryset = queryset.filter(tag_sistema=tag_sistema)
        except Tag.DoesNotExist:
            pass
    
    # Filtro por tags de usuário
    if tags_usuario:
        tags_list = [tag.strip() for tag in tags_usuario.split(',') if tag.strip()]
        if tags_list:
            for tag in tags_list:
                queryset = queryset.filter(tags_especificas__nome__icontains=tag)
    
    # Filtro por autor
    if iniciada_por:
        try:
            autor = User.objects.get(username__icontains=iniciada_por)
            queryset = queryset.filter(autor=autor)
        except User.DoesNotExist:
            pass
    
    # Aplicar select_related e prefetch_related
    queryset = queryset.select_related('autor', 'tag_sistema').prefetch_related(
        'tags_especificas',
        Prefetch('replies', queryset=Reply.objects.select_related('autor'))  # CORRETO
    )
    
    # Ordenação
    if tipo_organizacao == 'antigo':
        queryset = queryset.order_by('criado_em')
    elif tipo_organizacao == 'visualizacoes':
        queryset = queryset.order_by('-visualizacoes')
    elif tipo_organizacao == 'atividade':
        queryset = queryset.annotate(
            ultima_atividade=Max('replies__criado_em')
        ).order_by('-ultima_atividade', '-criado_em')
    else:  # 'recente' (padrão)
        queryset = queryset.order_by('-criado_em')
    
    # Separar threads fixas (apenas se mostrando threads)
    threads_fixas = []
    if tipo_filtro in ['all', 'thread']:
        threads_fixas = queryset.filter(tipo='THREAD', fixo=True).order_by('-criado_em')
        # Remover threads fixas da query principal para evitar duplicação
        queryset = queryset.exclude(tipo='THREAD', fixo=True)
    
    # Paginação mantendo filtros
    paginator = Paginator(queryset, 20)
    
    # Criar URL para manter filtros na paginação
    filtros_url = []
    if tipo_filtro != 'all':
        filtros_url.append(f'tipo={tipo_filtro}')
    if prefixo:
        filtros_url.append(f'prefixo={prefixo}')
    if tags_usuario:
        filtros_url.append(f'tags={tags_usuario}')
    if iniciada_por:
        filtros_url.append(f'autor={iniciada_por}')
    if tipo_organizacao != 'recente':
        filtros_url.append(f'ordem={tipo_organizacao}')
    
    filtros_query_string = '&'.join(filtros_url)
    
    try:
        postagens = paginator.page(page)
    except:
        postagens = paginator.page(1)
    
    # Buscar últimos posts para sidebar (não afetado por filtros)
    ultimos_posts = Post.objects.filter(
        assunto=assunto,
        tipo='POST'
    ).select_related('autor', 'tag_sistema').order_by('-criado_em')[:10]
    
    context = {
        'assunto': assunto,
        'threads_fixas': threads_fixas,
        'postagens': postagens,
        'ultimos_posts': ultimos_posts,
        'filtros_ativos': {
            'tipo': tipo_filtro,
            'prefixo': prefixo,
            'tags': tags_usuario,
            'autor': iniciada_por,
            'ordem': tipo_organizacao,
        },
        'filtros_query_string': filtros_query_string,
        'total_resultados': paginator.count,
    }
    
    return render(request, 'forum/assunto_detail.html', context)