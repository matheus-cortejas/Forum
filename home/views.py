from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count, Max, Prefetch
from .models import Categoria, Assunto
from posts.models import Postagem as Post, Reply, Tag, TagEspecifica
from django.contrib.auth import get_user_model
from datetime import datetime

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
    prefixo = request.GET.get('prefixo', '').strip()
    tags_usuario = request.GET.get('tags', '').strip()
    iniciada_por = request.GET.get('autor', '').strip()
    data_inicio = request.GET.get('data_inicio', '').strip()
    data_fim = request.GET.get('data_fim', '').strip()
    tipo_organizacao = request.GET.get('ordem', 'recente')
    page = request.GET.get('page', 1)
    
    # Query base para threads e posts
    queryset = Post.objects.filter(assunto=assunto)
    
    # Filtro por tipo
    if tipo_filtro == 'thread':
        queryset = queryset.filter(tipo='THREAD')
    elif tipo_filtro == 'post':
        queryset = queryset.filter(tipo='POST')
    
    # Filtro por prefixo
    if prefixo:
        queryset = queryset.filter(
            Q(tag_sistema__slug=prefixo) | 
            Q(tag_sistema__nome__icontains=prefixo)
        )
    
    # Filtro por tags de usuário
    if tags_usuario:
        tags_list = [tag.strip() for tag in tags_usuario.split(',') if tag.strip()]
        if tags_list:
            # Usar Q objects para OR entre tags
            tag_queries = Q()
            for tag in tags_list:
                tag_queries |= Q(tags_especificas__nome__icontains=tag)
            queryset = queryset.filter(tag_queries).distinct()
    
    # Filtro por autor 
    if iniciada_por:
        queryset = queryset.filter(
            Q(autor__username__icontains=iniciada_por) |
            Q(autor__first_name__icontains=iniciada_por) |
            Q(autor__last_name__icontains=iniciada_por)
        ).distinct()
    
    # Filtro por data de início
    if data_inicio:
        try:
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d')
            queryset = queryset.filter(criado_em__date__gte=data_inicio_obj.date())
        except ValueError:
            pass
    
    # Filtro por data de fim
    if data_fim:
        try:
            data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d')
            queryset = queryset.filter(criado_em__date__lte=data_fim_obj.date())
        except ValueError:
            pass
    
    # Aplicar select_related e prefetch_related ANTES da ordenação
    queryset = queryset.select_related(
        'autor', 
        'tag_sistema',
        'assunto',
        'assunto__categoria'
    ).prefetch_related(
        'tags_especificas',
        Prefetch(
            'replies', 
            queryset=Reply.objects.select_related('autor').order_by('-criado_em')
        )
    )
    
    if tipo_organizacao == 'antigo':
        queryset = queryset.order_by('criado_em')
    elif tipo_organizacao == 'visualizacoes':
        queryset = queryset.order_by('-visualizacoes', '-criado_em')
    elif tipo_organizacao == 'respostas':
        queryset = queryset.annotate(
            total_respostas=Count('replies')
        ).order_by('-total_respostas', '-criado_em')
    elif tipo_organizacao == 'atividade':
        queryset = queryset.annotate(
            ultima_atividade=Max('replies__criado_em')
        ).order_by('-ultima_atividade', '-criado_em')
    elif tipo_organizacao == 'autor':
        queryset = queryset.order_by('autor__username', '-criado_em')
    else: 
        queryset = queryset.order_by('-criado_em')
    
    threads_fixas = []
    if tipo_filtro in ['all', 'thread']:
        threads_fixas_query = Post.objects.filter(
            assunto=assunto,
            tipo='THREAD',
            fixo=True
        )
        
        if prefixo:
            threads_fixas_query = threads_fixas_query.filter(
                Q(tag_sistema__slug=prefixo) | 
                Q(tag_sistema__nome__icontains=prefixo)
            )
        
        if tags_usuario:
            tags_list = [tag.strip() for tag in tags_usuario.split(',') if tag.strip()]
            if tags_list:
                tag_queries = Q()
                for tag in tags_list:
                    tag_queries |= Q(tags_especificas__nome__icontains=tag)
                threads_fixas_query = threads_fixas_query.filter(tag_queries).distinct()
        
        if iniciada_por:
            threads_fixas_query = threads_fixas_query.filter(
                Q(autor__username__icontains=iniciada_por) |
                Q(autor__first_name__icontains=iniciada_por) |
                Q(autor__last_name__icontains=iniciada_por)
            ).distinct()
        
        if data_inicio:
            try:
                data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d')
                threads_fixas_query = threads_fixas_query.filter(criado_em__date__gte=data_inicio_obj.date())
            except ValueError:
                pass
        
        if data_fim:
            try:
                data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d')
                threads_fixas_query = threads_fixas_query.filter(criado_em__date__lte=data_fim_obj.date())
            except ValueError:
                pass
        
        threads_fixas = threads_fixas_query.select_related(
            'autor', 'tag_sistema'
        ).prefetch_related('tags_especificas').order_by('-criado_em')

        queryset = queryset.exclude(tipo='THREAD', fixo=True)
    
    paginator = Paginator(queryset, 20)
    total_resultados = paginator.count + len(threads_fixas)
    
    try:
        postagens = paginator.page(page)
    except:
        postagens = paginator.page(1)
    
    filtros_url = []
    if tipo_filtro != 'all':
        filtros_url.append(f'tipo={tipo_filtro}')
    if prefixo:
        filtros_url.append(f'prefixo={prefixo}')
    if tags_usuario:
        filtros_url.append(f'tags={tags_usuario}')
    if iniciada_por:
        filtros_url.append(f'autor={iniciada_por}')
    if data_inicio:
        filtros_url.append(f'data_inicio={data_inicio}')
    if data_fim:
        filtros_url.append(f'data_fim={data_fim}')
    if tipo_organizacao != 'recente':
        filtros_url.append(f'ordem={tipo_organizacao}')
    
    filtros_query_string = '&'.join(filtros_url)
    
    # Últimos posts
    ultimos_posts = Post.objects.filter(
        assunto=assunto,
        tipo='POST'
    ).select_related('autor', 'tag_sistema').order_by('-criado_em')[:10]
    
    # Tags mais usadas no assunto 
    tags_populares = TagEspecifica.objects.filter(
        postagem__assunto=assunto
    ).annotate(
        uso_count=Count('postagem')
    ).order_by('-uso_count')[:10]
    
    # Autores mais ativos no assunto
    autores_ativos = User.objects.filter(
        postagem__assunto=assunto
    ).annotate(
        total_posts_assunto=Count('postagem')  
    ).order_by('-total_posts_assunto')[:5]
    
    
    context = {
        'assunto': assunto,
        'threads_fixas': threads_fixas,
        'postagens': postagens,
        'ultimos_posts': ultimos_posts,
        'tags_populares': tags_populares,
        'autores_ativos': autores_ativos,
        'filtros_ativos': {
            'tipo': tipo_filtro,
            'prefixo': prefixo,
            'tags': tags_usuario,
            'autor': iniciada_por,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'ordem': tipo_organizacao,
        },
        'filtros_query_string': filtros_query_string,
        'total_resultados': total_resultados,
        # Verificar se há filtros ativos
        'tem_filtros_ativos': any([
            tipo_filtro != 'all',
            prefixo,
            tags_usuario,
            iniciada_por,
            data_inicio,
            data_fim,
            tipo_organizacao != 'recente'
        ]),
        'user_authenticated': request.user.is_authenticated,
    }
    
    return render(request, 'forum/assunto_detail.html', context)