from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Categoria, Assunto
from posts.models import Postagem as Post

def home(request):
    context = {
        'categorias': Categoria.objects.prefetch_related('assuntos').all()
    }
    return render(request, 'forum/forums.html', context)

def assunto_detail(request, categoria_slug, assunto_slug):
    assunto = get_object_or_404(Assunto, slug=assunto_slug)
    
    # Buscar threads fixas
    threads_fixas = Post.objects.filter(
        assunto=assunto,
        tipo='THREAD',
        fixo=True
    ).select_related('autor').order_by('-criado_em')
    
    # Buscar threads normais (com paginação)
    threads_list = Post.objects.filter(
        assunto=assunto,
        tipo='THREAD',
        fixo=False
    ).select_related('autor').order_by('-criado_em')
    
    # Configurar paginação
    paginator = Paginator(threads_list, 20)
    page = request.GET.get('page')
    threads_normais = paginator.get_page(page)
    
    # Buscar últimos posts (não threads)
    ultimos_posts = Post.objects.filter(
        assunto=assunto,
        tipo='POST'  # Posts são as mensagens dentro das threads
    ).select_related('autor').order_by('-criado_em')[:10]
    
    context = {
        'assunto': assunto,
        'threads_fixas': threads_fixas,
        'threads_normais': threads_normais,
        'ultimos_posts': ultimos_posts  # Mantido como ultimos_posts
    }
    
    return render(request, 'forum/assunto_detail.html', context)