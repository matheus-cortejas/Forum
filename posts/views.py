from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.text import slugify
from django.core.exceptions import PermissionDenied
from django.db.models import F, Q, Prefetch
from django.core.paginator import Paginator
from itertools import chain
from operator import attrgetter

from .models import (
    Postagem as Post, 
    Reply, 
    ReacaoPostagem, 
    ReacaoReply,  
    Reacao,
    TagEspecifica
)

from home.models import Assunto
from core.context_processors import filtros_forum
from .forms import PostagemForm, ReplyForm

@login_required
def criar_post(request, categoria_slug, assunto_slug):
    assunto = get_object_or_404(Assunto, slug=assunto_slug)
    
    if request.method == 'POST':
        form = PostagemForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            post = form.save(commit=False)
            post.autor = request.user
            post.assunto = assunto
            
            # Gerar slug único
            base_slug = slugify(post.titulo)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            post.slug = slug
            
            # SALVAR O POST PRIMEIRO
            post.save()
            
            # AGORA salvar as tags específicas (DEPOIS que o post já tem ID)
            tags_especificas = form.cleaned_data.get('tags_especificas', '')
            if tags_especificas:
                tags_list = [tag.strip() for tag in tags_especificas.split(',') if tag.strip()]
                for tag_nome in tags_list:
                    # Criar/buscar tag sem associar a postagem específica
                    tag, created = TagEspecifica.objects.get_or_create(
                        nome=tag_nome,
                        defaults={'nome': tag_nome}
                    )
                    # Adicionar a tag ao post usando many-to-many
                    post.tags_especificas.add(tag)
            
            messages.success(request, f'{post.get_tipo_display()} criado com sucesso!')
            
            # Redirecionar para a view correta
            return redirect('postagem_detail', 
                          categoria_slug=categoria_slug, 
                          assunto_slug=assunto_slug, 
                          postagem_id=post.id)
    else:
        form = PostagemForm(request=request)
    
    context = {
        'form': form,
        'assunto': assunto,
        'is_editing': False,
    }
    return render(request, 'posts/criar_editar_post.html', context)

@login_required
def editar_post(request, categoria_slug, assunto_slug, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Verificar permissões
    if post.autor != request.user and not request.user.is_staff:
        raise PermissionDenied("Você não tem permissão para editar este post.")
    
    if request.method == 'POST':
        form = PostagemForm(request.POST, request.FILES, instance=post, request=request)
        if form.is_valid():
            # Verificar se o título mudou para gerar novo slug
            if form.cleaned_data['titulo'] != post.titulo:
                base_slug = slugify(form.cleaned_data['titulo'])
                slug = base_slug
                counter = 1
                while Post.objects.filter(slug=slug).exclude(id=post.id).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                form.instance.slug = slug
            
            # SALVAR O POST PRIMEIRO
            post = form.save()
            
            # LIMPAR tags antigas e adicionar novas - CORREÇÃO AQUI
            post.tags_especificas.set([])  # Use set([]) ao invés de clear()
            tags_especificas = form.cleaned_data.get('tags_especificas', '')
            if tags_especificas:
                tags_list = [tag.strip() for tag in tags_especificas.split(',') if tag.strip()]
                tags_to_add = []
                for tag_nome in tags_list:
                    tag, created = TagEspecifica.objects.get_or_create(nome=tag_nome)
                    tags_to_add.append(tag)
                # Adicionar todas as tags de uma vez
                post.tags_especificas.add(*tags_to_add)
            
            messages.success(request, f'{post.get_tipo_display()} editado com sucesso!')
            
            # Redirecionar para a view correta
            return redirect('postagem_detail', 
                          categoria_slug=categoria_slug, 
                          assunto_slug=assunto_slug, 
                          postagem_id=post.id)
    else:
        # Preparar tags para o formulário
        tags_iniciais = ', '.join([tag.nome for tag in post.tags_especificas.all()])
        form = PostagemForm(instance=post, initial={'tags_especificas': tags_iniciais}, request=request)
    
    context = {
        'form': form,
        'post': post,
        'assunto': post.assunto,
        'is_editing': True,
    }
    return render(request, 'posts/criar_editar_post.html', context)

def ultimas_atividades(request):
    """Feed de atividades recentes com narrativa"""
    from core.models import UltimaAtividade
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    # Parâmetros de filtro
    tipo_filtro = request.GET.get('tipo', 'todas')
    periodo = request.GET.get('periodo', 'todas')
    autor_filtro = request.GET.get('autor', '')
    page = request.GET.get('page', 1)

    # Query base
    atividades = UltimaAtividade.objects.select_related(
        'usuario', 'postagem', 'reply', 'reacao',
        'postagem__assunto', 'postagem__autor',
        'reply__postagem', 'reply__postagem__assunto'
    ).prefetch_related(
        'postagem__tags_especificas',
        'usuario__groups'
    )

    # Filtro por tipo de atividade
    if tipo_filtro != 'todas':
        if tipo_filtro == 'novos_topicos':
            atividades = atividades.filter(tipo='NOVO_THREAD')
        elif tipo_filtro == 'novas_respostas':
            atividades = atividades.filter(tipo='NOVA_REPLY')
        elif tipo_filtro == 'novas_reacoes':
            atividades = atividades.filter(tipo__in=['NOVA_REACAO_POST', 'NOVA_REACAO_REPLY'])
        elif tipo_filtro == 'novos_posts':
            atividades = atividades.filter(tipo='NOVO_POST')

    # Filtro por período
    if periodo != 'todas':
        now = timezone.now()
        if periodo == 'hoje':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif periodo == 'esta_semana':
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif periodo == 'este_mes':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif periodo == 'ultimos_7_dias':
            start_date = now - timedelta(days=7)
        elif periodo == 'ultimos_30_dias':
            start_date = now - timedelta(days=30)
        else:
            start_date = None
            
        if start_date:
            atividades = atividades.filter(criado_em__gte=start_date)

    # Filtro por autor
    if autor_filtro:
        atividades = atividades.filter(usuario__username__icontains=autor_filtro)

    # Ordenação e paginação
    atividades = atividades.order_by('-criado_em')
    
    # Estatísticas rápidas
    stats = {
        'total_atividades': atividades.count(),
        'atividades_hoje': UltimaAtividade.objects.filter(
            criado_em__date=timezone.now().date()
        ).count(),
        'novos_topicos_hoje': UltimaAtividade.objects.filter(
            tipo='NOVO_THREAD',
            criado_em__date=timezone.now().date()
        ).count(),
        'novas_respostas_hoje': UltimaAtividade.objects.filter(
            tipo='NOVA_REPLY',
            criado_em__date=timezone.now().date()
        ).count(),
    }

    # Paginação
    paginator = Paginator(atividades, 25)
    try:
        atividades_page = paginator.page(page)
    except:
        atividades_page = paginator.page(1)

    # Opções para filtros
    tipos_atividade = [
        ('todas', 'Todas as Atividades'),
        ('novos_topicos', 'Novos Tópicos'),
        ('novas_respostas', 'Novas Respostas'),
        ('novos_posts', 'Novos Posts'),
        ('novas_reacoes', 'Novas Reações'),
    ]

    periodos = [
        ('todas', 'Todos os Períodos'),
        ('hoje', 'Hoje'),
        ('esta_semana', 'Esta Semana'),
        ('este_mes', 'Este Mês'),
        ('ultimos_7_dias', 'Últimos 7 Dias'),
        ('ultimos_30_dias', 'Últimos 30 Dias'),
    ]

    return render(request, 'posts/ultimas_atividades.html', {
        'atividades': atividades_page,
        'stats': stats,
        'filtros_ativos': {
            'tipo': tipo_filtro,
            'periodo': periodo,
            'autor': autor_filtro,
        },
        'tipos_atividade': tipos_atividade,
        'periodos': periodos,
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

# Views simplificadas para compatibilidade - TODAS usam o mesmo template
def thread_detail(request, categoria_slug, assunto_slug, thread_id):
    """Redireciona para a view unificada de postagem"""
    return postagem_detail(request, categoria_slug, assunto_slug, thread_id)

def post_detail(request, categoria_slug, assunto_slug, post_id):
    """Redireciona para a view unificada de postagem"""
    return postagem_detail(request, categoria_slug, assunto_slug, post_id)

def postagem_detail(request, categoria_slug, assunto_slug, postagem_id):
    """View unificada para exibir uma postagem (thread ou post) usando o template existente"""
    
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
    
    # Buscar reações disponíveis
    try:
        reacoes_disponiveis = Reacao.objects.filter(ativo=True).order_by('ordem')
    except:
        reacoes_disponiveis = []
    
    context = {
        'postagem': postagem,
        'replies': replies,
        'reacoes_disponiveis': reacoes_disponiveis,
    }
    
    # SEMPRE usar o template existente posts/detail.html
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
@require_POST
def deletar_post(request, categoria_slug, assunto_slug, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Verificar permissões
    if post.autor != request.user and not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Sem permissão'}, status=403)
    
    tipo = post.get_tipo_display()
    post.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': f'{tipo} deletado com sucesso!'})
    
    messages.success(request, f'{tipo} deletado com sucesso!')
    return redirect('assunto_detail', categoria_slug=categoria_slug, assunto_slug=assunto_slug)

# Reply views - corrigir redirecionamentos
@login_required
def add_reply(request, categoria_slug, assunto_slug, postagem_id):
    post = get_object_or_404(Post, id=postagem_id)
    
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.autor = request.user
            reply.postagem = post
            reply.save()
            
            messages.success(request, 'Resposta adicionada com sucesso!')
            
            # SEMPRE redirecionar para a view unificada
            return redirect('postagem_detail', 
                          categoria_slug=categoria_slug, 
                          assunto_slug=assunto_slug, 
                          postagem_id=post.id)
    else:
        form = ReplyForm()
    
    context = {
        'form': form,
        'post': post,
        'assunto': post.assunto,
    }
    return render(request, 'posts/add_reply.html', context)

@login_required
def edit_reply(request, categoria_slug, assunto_slug, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)
    
    # Verificar permissões
    if reply.autor != request.user and not request.user.is_staff:
        raise PermissionDenied("Você não tem permissão para editar esta resposta.")
    
    if request.method == 'POST':
        form = ReplyForm(request.POST, instance=reply)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resposta editada com sucesso!')
            
            # SEMPRE redirecionar para a view unificada
            return redirect('postagem_detail', 
                          categoria_slug=categoria_slug, 
                          assunto_slug=assunto_slug, 
                          postagem_id=reply.postagem.id)
    else:
        form = ReplyForm(instance=reply)
    
    context = {
        'form': form,
        'reply': reply,
        'post': reply.postagem,
        'assunto': reply.postagem.assunto,
    }
    return render(request, 'posts/edit_reply.html', context)

@login_required
@require_POST
def delete_reply(request, categoria_slug, assunto_slug, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)
    
    # Verificar permissões
    if reply.autor != request.user and not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Sem permissão'}, status=403)
    
    post = reply.postagem
    reply.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'Resposta deletada com sucesso!'})
    
    messages.success(request, 'Resposta deletada com sucesso!')
    
    # SEMPRE redirecionar para a view unificada
    return redirect('postagem_detail', 
                  categoria_slug=categoria_slug, 
                  assunto_slug=assunto_slug, 
                  postagem_id=post.id)

@login_required
@require_POST
def add_reaction_postagem(request, categoria_slug, assunto_slug, postagem_id):
    """View para adicionar/alterar reação em uma postagem"""
    
    postagem = get_object_or_404(
        Post,
        id=postagem_id,
        assunto__slug=assunto_slug,
        assunto__categoria__slug=categoria_slug
    )
    
    reacao_id = request.POST.get('reacao_id')
    
    if not reacao_id:
        return JsonResponse({'success': False, 'error': 'Reação não especificada'})
    
    try:
        reacao = get_object_or_404(Reacao, id=reacao_id, ativo=True)
        
        # Verificar se usuário já reagiu
        existing_reaction = ReacaoPostagem.objects.filter(
            postagem=postagem,
            usuario=request.user
        ).first()
        
        if existing_reaction:
            if existing_reaction.reacao.id == int(reacao_id):
                # Remover reação se for a mesma
                existing_reaction.delete()
                action = 'removed'
                
            else:
                # Alterar reação (não muda reputação)
                existing_reaction.reacao = reacao
                existing_reaction.save()
                action = 'changed'
        else:
            # Adicionar nova reação
            ReacaoPostagem.objects.create(
                postagem=postagem,
                usuario=request.user,
                reacao=reacao
            )
            action = 'added'
        
        # CORRIGIR: Buscar reações com URLs corretas
        from django.db.models import Count
        reacoes_query = ReacaoPostagem.objects.filter(postagem=postagem)\
            .select_related('reacao')\
            .values('reacao__id', 'reacao__nome', 'reacao__icone', 'reacao__ordem')\
            .annotate(count=Count('id'))\
            .order_by('reacao__ordem')
        
        user_reaction = ReacaoPostagem.objects.filter(
            postagem=postagem, 
            usuario=request.user
        ).select_related('reacao').first()
        
        # Converter para formato serializável com URLs corretas
        reacoes_data = []
        for reacao_data in reacoes_query:
            # Construir URL da imagem corretamente
            icone_url = ''
            if reacao_data['reacao__icone']:
                icone_url = f"/media/{reacao_data['reacao__icone']}"
            
            reacoes_data.append({
                'reacao__nome': reacao_data['reacao__nome'],
                'reacao__id': reacao_data['reacao__id'],
                'reacao__icone': icone_url,
                'count': reacao_data['count']
            })
        
        return JsonResponse({
            'success': True,
            'action': action,
            'reacoes': reacoes_data,
            'user_reaction_id': user_reaction.reacao.id if user_reaction else None
        })
        
    except Exception as e:
        import traceback
        print(f"Erro em add_reaction_postagem: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
def add_reaction_reply(request, reply_id):
    """View para adicionar/alterar reação em uma resposta"""
    
    reply = get_object_or_404(Reply, id=reply_id)
    reacao_id = request.POST.get('reacao_id')
    
    if not reacao_id:
        return JsonResponse({'success': False, 'error': 'Reação não especificada'})
    
    try:
        reacao = get_object_or_404(Reacao, id=reacao_id, ativo=True)
        
        # Verificar se usuário já reagiu
        existing_reaction = ReacaoReply.objects.filter(
            reply=reply,
            usuario=request.user
        ).first()
        
        if existing_reaction:
            if existing_reaction.reacao.id == int(reacao_id):
                # Remover reação se for a mesma
                existing_reaction.delete()
                action = 'removed'
                
            else:
                # Alterar reação (não muda reputação)
                existing_reaction.reacao = reacao
                existing_reaction.save()
                action = 'changed'
        else:
            # Adicionar nova reação
            ReacaoReply.objects.create(
                reply=reply,
                usuario=request.user,
                reacao=reacao
            )
            action = 'added'
            
        # CORRIGIR: Buscar reações com URLs corretas
        from django.db.models import Count
        reacoes_query = ReacaoReply.objects.filter(reply=reply)\
            .select_related('reacao')\
            .values('reacao__id', 'reacao__nome', 'reacao__icone', 'reacao__ordem')\
            .annotate(count=Count('id'))\
            .order_by('reacao__ordem')
        
        user_reaction = ReacaoReply.objects.filter(
            reply=reply, 
            usuario=request.user
        ).select_related('reacao').first()
        
        # Converter para formato serializável com URLs corretas
        reacoes_data = []
        for reacao_data in reacoes_query:
            # Construir URL da imagem corretamente
            icone_url = ''
            if reacao_data['reacao__icone']:
                icone_url = f"/media/{reacao_data['reacao__icone']}"
            
            reacoes_data.append({
                'reacao__nome': reacao_data['reacao__nome'],
                'reacao__id': reacao_data['reacao__id'],
                'reacao__icone': icone_url,
                'count': reacao_data['count']
            })
        
        return JsonResponse({
            'success': True,
            'action': action,
            'reacoes': reacoes_data,
            'user_reaction_id': user_reaction.reacao.id if user_reaction else None
        })
        
    except Exception as e:
        import traceback
        print(f"Erro em add_reaction_reply: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'success': False, 'error': str(e)})

def ultimas_atividades_stats(request):
    """API endpoint para estatísticas das atividades (para auto-refresh)"""
    from django.http import JsonResponse
    from core.models import UltimaAtividade
    from django.utils import timezone
    
    stats = {
        'total_atividades': UltimaAtividade.objects.count(),
        'atividades_hoje': UltimaAtividade.objects.filter(
            criado_em__date=timezone.now().date()
        ).count(),
        'novos_topicos_hoje': UltimaAtividade.objects.filter(
            tipo='NOVO_THREAD',
            criado_em__date=timezone.now().date()
        ).count(),
        'novas_respostas_hoje': UltimaAtividade.objects.filter(
            tipo='NOVA_REPLY',
            criado_em__date=timezone.now().date()
        ).count(),
    }
    
    return JsonResponse(stats)