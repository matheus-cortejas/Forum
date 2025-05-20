from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from .models import Postagem as Post, Reply, ReacaoPostagem
from home.models import Assunto
from django.core.paginator import Paginator
from itertools import chain
from operator import attrgetter

def ultimas_atividades(request):
    """Lista todas as atividades recentes (threads, posts, etc)"""
    # Buscar threads recentes
    threads = Post.objects.filter(
        tipo='THREAD'
    ).select_related('autor', 'assunto')[:20]
    
    # Buscar posts recentes
    posts = Post.objects.filter(
        tipo='POST'
    ).select_related('autor', 'assunto')[:20]
    
    # Combinar e ordenar por data
    todas_atividades = sorted(
        chain(threads, posts),
        key=attrgetter('criado_em'),
        reverse=True
    )[:50]
    
    return render(request, 'posts/ultimas_atividades.html', {
        'atividades': todas_atividades
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
    ).select_related('autor', 'thread', 'assunto').order_by('-criado_em')[:50]
    return render(request, 'posts/list.html', {
        'objetos': objetos,
        'titulo': 'Posts Recentes',
        'tipo': 'post'
    })

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
    """Lista todos os tópicos (threads) com filtros e ordenação por visualizações"""
    threads_qs = Post.objects.filter(tipo='THREAD').select_related('autor', 'assunto')
    # Filtros podem ser aplicados aqui usando request.GET
    threads_qs = threads_qs.order_by('-visualizacoes')
    paginator = Paginator(threads_qs, 20)
    page = request.GET.get('page')
    threads = paginator.get_page(page)
    return render(request, 'posts/list.html', {
        'objetos': threads,
        'titulo': 'Todos os Tópicos',
        'tipo': 'thread'
    })

def posts(request):
    """Lista todos os posts com filtros e ordenação por visualizações"""
    posts_qs = Post.objects.filter(tipo='POST').select_related('autor', 'thread', 'assunto')
    # Filtros podem ser aplicados aqui usando request.GET
    posts_qs = posts_qs.order_by('-visualizacoes')
    paginator = Paginator(posts_qs, 20)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    return render(request, 'posts/list.html', {
        'objetos': posts,
        'titulo': 'Todos os Posts',
        'tipo': 'post'
    })

# Lógica para depois
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
        conteudo = request.POST.get('conteudo')
        if conteudo:
            Reply.objects.create(
                postagem=thread,
                autor=request.user,
                conteudo=conteudo
            )
        
        return redirect('postagem_detail', 
                       categoria_slug=categoria_slug,
                       assunto_slug=assunto_slug,
                       postagem_id=thread_id)
    
    return redirect('postagem_detail', 
                   categoria_slug=categoria_slug,
                   assunto_slug=assunto_slug,
                   postagem_id=thread_id)

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

