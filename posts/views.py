from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q, Prefetch
from .models import Postagem as Post, Reply, ReacaoPostagem
from home.models import Assunto
from django.core.paginator import Paginator
from itertools import chain
from operator import attrgetter
from core.context_processors import filtros_forum
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

def ultimas_atividades(request):
    """Lista todas as atividades recentes (threads, posts, etc) com filtros"""
    filtros = filtros_forum(request)
    tipo = request.GET.get('tipo', 'all')
    prefixo = request.GET.get('prefixo', '')
    tags_usuario = request.GET.get('tags', '')
    iniciada_por = request.GET.get('autor', '')
    tipo_organizacao = request.GET.get('ordem', 'recente')
    page = request.GET.get('page', 1)
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    ordem_crescente = request.GET.get('ordem_crescente', 'desc') == 'asc'

    threads = Post.objects.filter(tipo='THREAD')
    posts = Post.objects.filter(tipo='POST')

    # Filtros
    if tipo == 'thread':
        queryset = threads
    elif tipo == 'post':
        queryset = posts
    else:
        queryset = Post.objects.all()

    if prefixo:
        queryset = queryset.filter(tag_sistema__slug=prefixo)
    if tags_usuario:
        tags_list = [tag.strip() for tag in tags_usuario.split(',') if tag.strip()]
        for tag in tags_list:
            queryset = queryset.filter(tags_especificas__nome__icontains=tag)
    if iniciada_por:
        queryset = queryset.filter(autor__username__icontains=iniciada_por)
    if data_inicio:
        try:
            from datetime import datetime
            data_inicio_dt = datetime.strptime(data_inicio, "%Y-%m-%d")
            queryset = queryset.filter(criado_em__date__gte=data_inicio_dt)
        except Exception:
            pass
    if data_fim:
        try:
            from datetime import datetime
            data_fim_dt = datetime.strptime(data_fim, "%Y-%m-%d")
            queryset = queryset.filter(criado_em__date__lte=data_fim_dt)
        except Exception:
            pass

    # Ordenação
    if tipo_organizacao == 'antigo':
        queryset = queryset.order_by('criado_em' if ordem_crescente else '-criado_em')
    elif tipo_organizacao == 'visualizacoes':
        queryset = queryset.order_by('visualizacoes' if ordem_crescente else '-visualizacoes')
    elif tipo_organizacao == 'atividade':
        queryset = queryset.annotate(ultima_atividade=F('atualizado_em')).order_by('ultima_atividade' if ordem_crescente else '-ultima_atividade', 'criado_em' if ordem_crescente else '-criado_em')
    else:
        queryset = queryset.order_by('criado_em' if ordem_crescente else '-criado_em')

    queryset = queryset.select_related('autor', 'assunto', 'tag_sistema').prefetch_related('tags_especificas')
    paginator = Paginator(queryset, 20)
    try:
        atividades = paginator.page(page)
    except:
        atividades = paginator.page(1)

    return render(request, 'posts/ultimas_atividades.html', {
        'atividades': atividades,
        'filtros_ativos': {
            'tipo': tipo,
            'prefixo': prefixo,
            'tags': tags_usuario,
            'autor': iniciada_por,
            'ordem': tipo_organizacao,
        },
        'tipos_filtro': filtros['tipos_filtro'],
        'tags_sistema_filtro': filtros['tags_sistema_filtro'],
        'tags_populares': filtros['tags_populares'],
        'tipos_organizacao': filtros['tipos_organizacao'],
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'ordem_crescente': ordem_crescente,
    })

def recent_threads(request):
    """Lista as threads mais recentes"""
    objetos = Post.objects.filter(
        tipo='THREAD'
    ).select_related('autor', 'assunto').order_by('-criado_em')[:50]
    return render(request, 'posts/list.html', {
        'objetos': objetos,
        'titulo': 'Tópicos Recentes',
        'tipo': 'thread'
    })

def recent_posts(request):
    """Lista os posts mais recentes"""
    objetos = Post.objects.filter(
        tipo='POST'
    ).select_related('autor', 'assunto').order_by('-criado_em')[:50]
    return render(request, 'posts/list.html', {
        'objetos': objetos,
        'titulo': 'Posts Recentes',
        'tipo': 'post'
    })

def thread_detail(request, categoria_slug, assunto_slug, thread_id):
    """Redireciona para a view genérica de postagem (thread)"""
    return postagem_detail(request, categoria_slug, assunto_slug, thread_id)

def post_detail(request, categoria_slug, assunto_slug, post_id):
    """Redireciona para a view genérica de postagem (post)"""
    return postagem_detail(request, categoria_slug, assunto_slug, post_id)

def postagem_detail(request, categoria_slug, assunto_slug, postagem_id):
    """View para exibir uma postagem (thread ou post) e suas respostas"""
    
    postagem = get_object_or_404(
        Post.objects.select_related('autor', 'assunto', 'tag_sistema'),
        id=postagem_id,
        assunto__slug=assunto_slug,
        assunto__categoria__slug=categoria_slug
    )
    
    # Incrementa visualizações
    Post.objects.filter(id=postagem_id).update(visualizacoes=F('visualizacoes') + 1)
    
    # Buscar replies
    replies = Reply.objects.filter(postagem=postagem)\
        .select_related('autor')\
        .order_by('criado_em')
    
    # Buscar reações
    reacoes = postagem.get_reacoes_count()
    user_reaction = None
    if request.user.is_authenticated:
        user_reaction = postagem.get_user_reaction(request.user)
    
    context = {
        'postagem': postagem,
        'replies': replies,
        'reacoes': reacoes,
        'user_reaction': user_reaction
    }
    
    return render(request, 'posts/detail.html', context)

def threads(request):
    """Lista todos os tópicos (threads) com filtros"""
    filtros = filtros_forum(request)
    prefixo = request.GET.get('prefixo', '')
    tags_usuario = request.GET.get('tags', '')
    iniciada_por = request.GET.get('autor', '')
    tipo_organizacao = request.GET.get('ordem', 'recente')
    page = request.GET.get('page', 1)
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    ordem_crescente = request.GET.get('ordem_crescente', 'desc') == 'asc'

    queryset = Post.objects.filter(tipo='THREAD')
    if prefixo:
        queryset = queryset.filter(tag_sistema__slug=prefixo)
    if tags_usuario:
        tags_list = [tag.strip() for tag in tags_usuario.split(',') if tag.strip()]
        for tag in tags_list:
            queryset = queryset.filter(tags_especificas__nome__icontains=tag)
    if iniciada_por:
        queryset = queryset.filter(autor__username__icontains=iniciada_por)
    if data_inicio:
        try:
            from datetime import datetime
            data_inicio_dt = datetime.strptime(data_inicio, "%Y-%m-%d")
            queryset = queryset.filter(criado_em__date__gte=data_inicio_dt)
        except Exception:
            pass
    if data_fim:
        try:
            from datetime import datetime
            data_fim_dt = datetime.strptime(data_fim, "%Y-%m-%d")
            queryset = queryset.filter(criado_em__date__lte=data_fim_dt)
        except Exception:
            pass

    if tipo_organizacao == 'antigo':
        queryset = queryset.order_by('criado_em' if ordem_crescente else '-criado_em')
    elif tipo_organizacao == 'visualizacoes':
        queryset = queryset.order_by('visualizacoes' if ordem_crescente else '-visualizacoes')
    elif tipo_organizacao == 'atividade':
        queryset = queryset.annotate(ultima_atividade=F('atualizado_em')).order_by('ultima_atividade' if ordem_crescente else '-ultima_atividade', 'criado_em' if ordem_crescente else '-criado_em')
    else:
        queryset = queryset.order_by('criado_em' if ordem_crescente else '-criado_em')

    queryset = queryset.select_related('autor', 'assunto', 'tag_sistema').prefetch_related('tags_especificas')
    paginator = Paginator(queryset, 20)
    try:
        threads = paginator.page(page)
    except:
        threads = paginator.page(1)

    return render(request, 'posts/list.html', {
        'objetos': threads,
        'titulo': 'Todos os Tópicos',
        'tipo': 'thread',
        'filtros_ativos': {
            'prefixo': prefixo,
            'tags': tags_usuario,
            'autor': iniciada_por,
            'ordem': tipo_organizacao,
        },
        'tipos_filtro': filtros['tipos_filtro'],
        'tags_sistema_filtro': filtros['tags_sistema_filtro'],
        'tags_populares': filtros['tags_populares'],
        'tipos_organizacao': filtros['tipos_organizacao'],
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'ordem_crescente': ordem_crescente,
    })

def posts(request):
    """Lista todos os posts com filtros"""
    filtros = filtros_forum(request)
    prefixo = request.GET.get('prefixo', '')
    tags_usuario = request.GET.get('tags', '')
    iniciada_por = request.GET.get('autor', '')
    tipo_organizacao = request.GET.get('ordem', 'recente')
    page = request.GET.get('page', 1)
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    ordem_crescente = request.GET.get('ordem_crescente', 'desc') == 'asc'

    queryset = Post.objects.filter(tipo='POST')
    if prefixo:
        queryset = queryset.filter(tag_sistema__slug=prefixo)
    if tags_usuario:
        tags_list = [tag.strip() for tag in tags_usuario.split(',') if tag.strip()]
        for tag in tags_list:
            queryset = queryset.filter(tags_especificas__nome__icontains=tag)
    if iniciada_por:
        queryset = queryset.filter(autor__username__icontains=iniciada_por)
    if data_inicio:
        try:
            from datetime import datetime
            data_inicio_dt = datetime.strptime(data_inicio, "%Y-%m-%d")
            queryset = queryset.filter(criado_em__date__gte=data_inicio_dt)
        except Exception:
            pass
    if data_fim:
        try:
            from datetime import datetime
            data_fim_dt = datetime.strptime(data_fim, "%Y-%m-%d")
            queryset = queryset.filter(criado_em__date__lte=data_fim_dt)
        except Exception:
            pass

    if tipo_organizacao == 'antigo':
        queryset = queryset.order_by('criado_em' if ordem_crescente else '-criado_em')
    elif tipo_organizacao == 'visualizacoes':
        queryset = queryset.order_by('visualizacoes' if ordem_crescente else '-visualizacoes')
    elif tipo_organizacao == 'atividade':
        queryset = queryset.annotate(ultima_atividade=F('atualizado_em')).order_by('ultima_atividade' if ordem_crescente else '-ultima_atividade', 'criado_em' if ordem_crescente else '-criado_em')
    else:
        queryset = queryset.order_by('criado_em' if ordem_crescente else '-criado_em')

    queryset = queryset.select_related('autor', 'assunto', 'tag_sistema').prefetch_related('tags_especificas')
    paginator = Paginator(queryset, 20)
    try:
        posts = paginator.page(page)
    except:
        posts = paginator.page(1)

    return render(request, 'posts/list.html', {
        'objetos': posts,
        'titulo': 'Todos os Posts',
        'tipo': 'post',
        'filtros_ativos': {
            'prefixo': prefixo,
            'tags': tags_usuario,
            'autor': iniciada_por,
            'ordem': tipo_organizacao,
        },
        'tipos_filtro': filtros['tipos_filtro'],
        'tags_sistema_filtro': filtros['tags_sistema_filtro'],
        'tags_populares': filtros['tags_populares'],
        'tipos_organizacao': filtros['tipos_organizacao'],
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'ordem_crescente': ordem_crescente,
    })

@login_required
def add_reply(request, categoria_slug, assunto_slug, thread_id):
    """View para adicionar uma resposta a uma thread"""
    
    thread = get_object_or_404(
        Post,
        id=thread_id,
        tipo='THREAD',
        assunto__slug=assunto_slug,
        assunto__categoria__slug=categoria_slug
    )
    
    if request.method == 'POST':
        conteudo = request.POST.get('conteudo', '').strip()
        
        if not conteudo:
            messages.error(request, 'O conteúdo da resposta não pode estar vazio.')
        elif len(conteudo) < 10:
            messages.error(request, 'A resposta deve ter pelo menos 10 caracteres.')
        elif len(conteudo) > 10000:
            messages.error(request, 'A resposta não pode ter mais de 10.000 caracteres.')
        else:
            try:
                reply = Reply.objects.create(
                    postagem=thread,
                    autor=request.user,
                    conteudo=conteudo
                )
                
                # Atualizar contador de respostas do usuário
                request.user.answers = (request.user.answers or 0) + 1
                request.user.total_itens = (request.user.total_itens or 0) + 1
                request.user.save(update_fields=['answers', 'total_itens'])
                
                messages.success(request, 'Resposta adicionada com sucesso!')
                
                # Se for requisição AJAX, retornar JSON
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Resposta adicionada com sucesso!',
                        'reply_id': reply.id,
                        'reply_html': render_reply_html(reply, request.user)
                    })
                
            except Exception as e:
                messages.error(request, f'Erro ao salvar resposta: {str(e)}')
    
    return redirect('postagem_detail', 
                   categoria_slug=categoria_slug,
                   assunto_slug=assunto_slug,
                   postagem_id=thread_id)

@login_required
@require_POST
def edit_reply(request, reply_id):
    """View para editar uma resposta"""
    
    reply = get_object_or_404(Reply, id=reply_id, autor=request.user)
    
    conteudo = request.POST.get('conteudo', '').strip()
    
    if not conteudo:
        return JsonResponse({'success': False, 'error': 'Conteúdo não pode estar vazio'})
    
    if len(conteudo) < 10:
        return JsonResponse({'success': False, 'error': 'Resposta deve ter pelo menos 10 caracteres'})
    
    if len(conteudo) > 10000:
        return JsonResponse({'success': False, 'error': 'Resposta não pode ter mais de 10.000 caracteres'})
    
    reply.conteudo = conteudo
    reply.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Resposta editada com sucesso!',
        'conteudo': reply.conteudo,
        'data_edicao': reply.atualizado_em.strftime('%d/%m/%Y %H:%M')
    })

@login_required
@require_POST
def delete_reply(request, reply_id):
    """View para deletar uma resposta"""
    
    reply = get_object_or_404(Reply, id=reply_id)
    
    # Verificar permissões
    if reply.autor != request.user and not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Sem permissão para deletar esta resposta'})
    
    # Atualizar contadores do usuário
    reply.autor.answers = max(0, (reply.autor.answers or 1) - 1)
    reply.autor.total_itens = max(0, (reply.autor.total_itens or 1) - 1)
    reply.autor.save(update_fields=['answers', 'total_itens'])
    
    reply.delete()
    
    return JsonResponse({
        'success': True,
        'message': 'Resposta deletada com sucesso!'
    })

def render_reply_html(reply, current_user):
    """Função auxiliar para renderizar HTML de uma resposta"""
    from django.template.loader import render_to_string
    
    return render_to_string('posts/partials/reply_item.html', {
        'reply': reply,
        'user': current_user
    })

@login_required
def add_reaction(request, categoria_slug, assunto_slug, postagem_id):
    """View para adicionar/alterar reação em uma postagem"""
    
    if request.method == 'POST':
        postagem = get_object_or_404(
            Post,
            id=postagem_id,
            assunto__slug=assunto_slug,
            assunto__categoria__slug=categoria_slug
        )
        
        reacao_id = request.POST.get('reacao')
        if reacao_id:
            ReacaoPostagem.objects.update_or_create(
                postagem=postagem,
                usuario=request.user,
                defaults={'reacao_id': reacao_id}
            )
    
    return redirect('postagem_detail', 
                   categoria_slug=categoria_slug,
                   assunto_slug=assunto_slug,
                   postagem_id=postagem_id)

