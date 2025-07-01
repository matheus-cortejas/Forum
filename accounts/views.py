from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm

from .models import Usuario, VisitaPerfil

class PerfilDetailView(DetailView):
    """View para exibir perfil de um usuário"""
    model = Usuario
    template_name = 'accounts/profile.html'  # CORRIGIDO: usar profile.html
    context_object_name = 'usuario'  # CORRIGIDO: usar 'usuario' em vez de 'usuario_perfil'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario_perfil = self.get_object()
        
        # Registrar a visita ao perfil
        if self.request.user.is_authenticated and self.request.user != usuario_perfil:
            VisitaPerfil.registrar_visita(usuario_perfil, self.request.user)
        
        # Buscar atividades recentes
        try:
            from posts.models import Post, Reply
            # Últimas postagens do usuário
            ultimas_postagens = Post.objects.filter(autor=usuario_perfil).order_by('-criado_em')[:5]
            # Últimas respostas do usuário
            ultimas_respostas = Reply.objects.filter(autor=usuario_perfil).order_by('-criado_em')[:5]
            
            # Combinar e ordenar atividades por data
            atividades = []
            
            for post in ultimas_postagens:
                atividades.append({
                    'tipo': 'post',
                    'titulo': post.titulo,
                    'conteudo': post.conteudo[:150] + '...' if len(post.conteudo) > 150 else post.conteudo,
                    'data': post.criado_em,
                    'url': f'/posts/{post.assunto.categoria.slug}/{post.assunto.slug}/{post.id}/'
                })
                
            for reply in ultimas_respostas:
                if hasattr(reply, 'postagem'):
                    atividades.append({
                        'tipo': 'reply',
                        'titulo': f'Comentou em: {reply.postagem.titulo}',
                        'conteudo': reply.conteudo[:150] + '...' if len(reply.conteudo) > 150 else reply.conteudo,
                        'data': reply.criado_em,
                        'url': f'/posts/{reply.postagem.assunto.categoria.slug}/{reply.postagem.assunto.slug}/{reply.postagem.id}/'
                    })
            
            # Ordenar por data (mais recentes primeiro)
            atividades = sorted(atividades, key=lambda x: x['data'], reverse=True)[:10]
            
        except ImportError:
            ultimas_postagens = []
            ultimas_respostas = []
            atividades = []
        
        # Adicionar contexto adicional
        context.update({
            'ultimos_visitantes': usuario_perfil.visitas_recebidas.all()[:5] if hasattr(usuario_perfil, 'visitas_recebidas') else [],
            'total_seguidores': usuario_perfil.get_total_seguidores() if hasattr(usuario_perfil, 'get_total_seguidores') else 0,
            'seguindo': self.request.user.is_authenticated and self.request.user.esta_seguindo(usuario_perfil) if hasattr(self.request.user, 'esta_seguindo') else False,
            'ultimas_postagens': ultimas_postagens,
            'ultimas_respostas': ultimas_respostas,
            'atividades': atividades,
            'data_cadastro': usuario_perfil.date_joined,
            'ultimo_acesso': usuario_perfil.ultimo_acesso if hasattr(usuario_perfil, 'ultimo_acesso') else usuario_perfil.last_login,
            'is_own_profile': self.request.user == usuario_perfil,
        })
        
        return context
    
@login_required
def seguir_usuario(request, username):
    """View para seguir/deixar de seguir um usuário"""
    usuario_alvo = get_object_or_404(Usuario, username=username)
    usuario_atual = request.user
    
    if usuario_atual == usuario_alvo:
        messages.error(request, "Você não pode seguir a si mesmo.")
        return redirect('perfil', username=username)
    
    if usuario_atual.esta_seguindo(usuario_alvo):
        usuario_atual.deixar_de_seguir(usuario_alvo)
        acao = "deixou de seguir"
    else:
        usuario_atual.seguir(usuario_alvo)
        acao = "começou a seguir"
    
    # Se for uma requisição AJAX, retorna JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'seguindo': usuario_atual.esta_seguindo(usuario_alvo),
            'total_seguidores': usuario_alvo.get_total_seguidores()
        })
        
    messages.success(request, f"Você {acao} {usuario_alvo.username}.")
    return redirect('perfil', username=username)

class EditarPerfilView(LoginRequiredMixin, UpdateView):
    """View para editar o próprio perfil"""
    model = Usuario
    template_name = 'accounts/editar_perfil.html'
    fields = ['apelido', 'avatar', 'biografia', 'data_nascimento', 
              'localizacao', 'site', 'altura', 'peso', 'objetivo']
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def get_success_url(self):
        return reverse_lazy('perfil', kwargs={'username': self.request.user.username})

def login(request):
    """View para login de usuário"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                # Atualizar último acesso
                user.atualizar_ultimo_acesso()
                messages.success(request, f'Bem-vindo de volta, {user.username}!')
                # Redirecionar para próxima página ou home
                next_page = request.GET.get('next')
                return redirect(next_page if next_page else 'home')
            else:
                messages.error(request, 'Nome de usuário ou senha incorretos.')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def register(request):
    """View para registro de usuário"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Validações básicas
        if not username or not email or not password:
            messages.error(request, 'Todos os campos são obrigatórios.')
        elif password != password_confirm:
            messages.error(request, 'As senhas não coincidem.')
        elif Usuario.objects.filter(username=username).exists():
            messages.error(request, 'Nome de usuário já existe.')
        elif Usuario.objects.filter(email=email).exists():
            messages.error(request, 'E-mail já está cadastrado.')
        elif len(password) < 8:
            messages.error(request, 'A senha deve ter pelo menos 8 caracteres.')
        else:
            try:
                # Criar usuário
                user = Usuario.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                messages.success(request, 'Conta criada com sucesso! Faça login para continuar.')
                return redirect('login')
            except Exception as e:
                # Log do erro real
                print(f"Erro ao criar usuário: {e}")
                messages.error(request, f'Erro ao criar conta: {str(e)}')
    
    return render(request, 'accounts/register.html')

def logout_view(request):
    """View de logout que aceita GET e POST"""
    if request.user.is_authenticated:
        username = request.user.username
        auth_logout(request)
        messages.success(request, f'Você saiu da sua conta, {username}. Até logo!')
    return redirect('home')

def members(request):
    """View para página de membros com diferentes filtros"""
    from django.db.models import Count, Q
    from datetime import datetime, timedelta
    
    tipo = request.GET.get('tipo')
    busca = request.GET.get('busca', '').strip()
    
    # Se há busca, mostra a lista filtrada
    if busca:
        members = Usuario.objects.filter(
            Q(username__icontains=busca) | 
            Q(apelido__icontains=busca) |
            Q(first_name__icontains=busca) |
            Q(last_name__icontains=busca)
        ).order_by('-total_itens')[:50]
        return render(request, 'accounts/members_list.html', {
            'members': members, 
            'tipo': 'busca',
            'busca_termo': busca
        })
    
    # Se há filtro específico, mostra a lista filtrada
    if tipo:
        return members_list(request)
    
    # Página principal de membros notáveis
    hoje = datetime.now().date()
    semana_passada = hoje - timedelta(days=7)
    mes_passado = hoje - timedelta(days=30)
    
    try:
        from posts.models import Postagem, Reply
        
        # Mais mensagens (total)
        mais_mensagens = Usuario.objects.filter(total_itens__gt=0).order_by('-total_itens')[:10]
        
        # Mais mensagens hoje
        posts_hoje = Postagem.objects.filter(criado_em__date=hoje).values('autor').annotate(count=Count('id'))
        replies_hoje = Reply.objects.filter(criado_em__date=hoje).values('autor').annotate(count=Count('id'))
        
        # Combinar posts e replies de hoje
        usuarios_hoje = {}
        for post in posts_hoje:
            usuarios_hoje[post['autor']] = usuarios_hoje.get(post['autor'], 0) + post['count']
        for reply in replies_hoje:
            usuarios_hoje[reply['autor']] = usuarios_hoje.get(reply['autor'], 0) + reply['count']
        
        # Ordenar por mensagens hoje
        mais_hoje_ids = sorted(usuarios_hoje.items(), key=lambda x: x[1], reverse=True)[:10]
        mais_hoje = []
        for user_id, count in mais_hoje_ids:
            user = Usuario.objects.get(id=user_id)
            user.mensagens_hoje = count
            mais_hoje.append(user)
        
        # Mais mensagens este mês
        posts_mes = Postagem.objects.filter(criado_em__gte=mes_passado).values('autor').annotate(count=Count('id'))
        replies_mes = Reply.objects.filter(criado_em__gte=mes_passado).values('autor').annotate(count=Count('id'))
        
        usuarios_mes = {}
        for post in posts_mes:
            usuarios_mes[post['autor']] = usuarios_mes.get(post['autor'], 0) + post['count']
        for reply in replies_mes:
            usuarios_mes[reply['autor']] = usuarios_mes.get(reply['autor'], 0) + reply['count']
        
        mais_mes_ids = sorted(usuarios_mes.items(), key=lambda x: x[1], reverse=True)[:10]
        mais_mes = []
        for user_id, count in mais_mes_ids:
            user = Usuario.objects.get(id=user_id)
            user.mensagens_mes = count
            mais_mes.append(user)
        
        # Mais mensagens esta semana
        posts_semana = Postagem.objects.filter(criado_em__gte=semana_passada).values('autor').annotate(count=Count('id'))
        replies_semana = Reply.objects.filter(criado_em__gte=semana_passada).values('autor').annotate(count=Count('id'))
        
        usuarios_semana = {}
        for post in posts_semana:
            usuarios_semana[post['autor']] = usuarios_semana.get(post['autor'], 0) + post['count']
        for reply in replies_semana:
            usuarios_semana[reply['autor']] = usuarios_semana.get(reply['autor'], 0) + reply['count']
        
        mais_semana_ids = sorted(usuarios_semana.items(), key=lambda x: x[1], reverse=True)[:10]
        mais_semana = []
        for user_id, count in mais_semana_ids:
            user = Usuario.objects.get(id=user_id)
            user.mensagens_semana = count
            mais_semana.append(user)
        
    except ImportError:
        mais_mensagens = Usuario.objects.order_by('-total_itens')[:10]
        mais_hoje = []
        mais_mes = []
        mais_semana = []
    
    # Aniversariantes (usuários com aniversário hoje)
    aniversariantes = Usuario.objects.filter(data_nascimento__month=hoje.month, data_nascimento__day=hoje.day)[:10]
    
    # Maior pontuação de reação
    mais_reacoes = Usuario.objects.filter(reputacao__gt=0).order_by('-reputacao')[:10]
    
    # Mais soluções
    mais_solucoes = Usuario.objects.filter(answers__gt=0).order_by('-answers')[:10]
    
    # Staff e moderadores
    staff = Usuario.objects.filter(is_staff=True)[:10]
    moderadores = Usuario.objects.filter(cargos__pode_moderar=True).distinct()[:10]
    
    # Novos membros (últimos 7 dias) para ambas as páginas
    novos_membros = Usuario.objects.filter(date_joined__gte=semana_passada).order_by('-date_joined')[:5]
    
    context = {
        'mais_mensagens': mais_mensagens,
        'mais_hoje': mais_hoje,
        'mais_mes': mais_mes,
        'mais_semana': mais_semana,
        'aniversariantes': aniversariantes,
        'mais_reacoes': mais_reacoes,
        'mais_solucoes': mais_solucoes,
        'staff': staff,
        'moderadores': moderadores,
        'novos_membros': novos_membros,
    }
    
    return render(request, 'accounts/members.html', context)

def members_list(request):
    """View para listagem específica de membros baseada no tipo"""
    from django.db.models import Count, Q
    from datetime import datetime, timedelta
    
    tipo = request.GET.get('tipo', 'mais_mensagens')
    busca = request.GET.get('busca', '').strip()
    
    hoje = datetime.now().date()
    semana_passada = hoje - timedelta(days=7)
    mes_passado = hoje - timedelta(days=30)
    
    # Filtro de busca
    queryset = Usuario.objects.all()
    if busca:
        queryset = queryset.filter(
            Q(username__icontains=busca) | 
            Q(apelido__icontains=busca) |
            Q(first_name__icontains=busca) |
            Q(last_name__icontains=busca)
        )
    
    # Aplicar filtros específicos
    if tipo == 'mais_mensagens':
        members = queryset.order_by('-total_itens')[:50]
        titulo = "Membros com mais mensagens"
        
    elif tipo == 'mais_hoje':
        try:
            from posts.models import Postagem, Reply
            
            # Contar posts e replies de hoje para cada usuário
            posts_hoje = Postagem.objects.filter(criado_em__date=hoje).values('autor').annotate(count=Count('id'))
            replies_hoje = Reply.objects.filter(criado_em__date=hoje).values('autor').annotate(count=Count('id'))
            
            usuarios_hoje = {}
            for post in posts_hoje:
                usuarios_hoje[post['autor']] = usuarios_hoje.get(post['autor'], 0) + post['count']
            for reply in replies_hoje:
                usuarios_hoje[reply['autor']] = usuarios_hoje.get(reply['autor'], 0) + reply['count']
            
            # Filtrar por usuários que postaram hoje
            user_ids = list(usuarios_hoje.keys())
            if busca:
                members_base = queryset.filter(id__in=user_ids)
            else:
                members_base = Usuario.objects.filter(id__in=user_ids)
            
            # Adicionar contagem de mensagens de hoje
            members = []
            for user in members_base:
                user.mensagens_periodo = usuarios_hoje.get(user.id, 0)
                members.append(user)
            
            # Ordenar por mensagens de hoje
            members = sorted(members, key=lambda x: x.mensagens_periodo, reverse=True)[:50]
            
        except ImportError:
            members = []
        
        titulo = "Membros com mais mensagens hoje"
        
    elif tipo == 'mais_mes':
        try:
            from posts.models import Postagem, Reply
            
            posts_mes = Postagem.objects.filter(criado_em__gte=mes_passado).values('autor').annotate(count=Count('id'))
            replies_mes = Reply.objects.filter(criado_em__gte=mes_passado).values('autor').annotate(count=Count('id'))
            
            usuarios_mes = {}
            for post in posts_mes:
                usuarios_mes[post['autor']] = usuarios_mes.get(post['autor'], 0) + post['count']
            for reply in replies_mes:
                usuarios_mes[reply['autor']] = usuarios_mes.get(reply['autor'], 0) + reply['count']
            
            user_ids = list(usuarios_mes.keys())
            if busca:
                members_base = queryset.filter(id__in=user_ids)
            else:
                members_base = Usuario.objects.filter(id__in=user_ids)
            
            members = []
            for user in members_base:
                user.mensagens_periodo = usuarios_mes.get(user.id, 0)
                members.append(user)
            
            members = sorted(members, key=lambda x: x.mensagens_periodo, reverse=True)[:50]
            
        except ImportError:
            members = []
        
        titulo = "Membros com mais mensagens este mês"
        
    elif tipo == 'mais_semana':
        try:
            from posts.models import Postagem, Reply
            
            posts_semana = Postagem.objects.filter(criado_em__gte=semana_passada).values('autor').annotate(count=Count('id'))
            replies_semana = Reply.objects.filter(criado_em__gte=semana_passada).values('autor').annotate(count=Count('id'))
            
            usuarios_semana = {}
            for post in posts_semana:
                usuarios_semana[post['autor']] = usuarios_semana.get(post['autor'], 0) + post['count']
            for reply in replies_semana:
                usuarios_semana[reply['autor']] = usuarios_semana.get(reply['autor'], 0) + reply['count']
            
            user_ids = list(usuarios_semana.keys())
            if busca:
                members_base = queryset.filter(id__in=user_ids)
            else:
                members_base = Usuario.objects.filter(id__in=user_ids)
            
            members = []
            for user in members_base:
                user.mensagens_periodo = usuarios_semana.get(user.id, 0)
                members.append(user)
            
            members = sorted(members, key=lambda x: x.mensagens_periodo, reverse=True)[:50]
            
        except ImportError:
            members = []
        
        titulo = "Membros com mais mensagens esta semana"
        
    elif tipo == 'aniversariantes':
        members = queryset.filter(data_nascimento__month=hoje.month, data_nascimento__day=hoje.day)[:50]
        titulo = "Aniversariantes de hoje"
        
    elif tipo == 'mais_reacoes':
        members = queryset.filter(reputacao__gt=0).order_by('-reputacao')[:50]
        titulo = "Membros com maior pontuação de reação"
        
    elif tipo == 'mais_solucoes':
        members = queryset.filter(answers__gt=0).order_by('-answers')[:50]
        titulo = "Membros com mais soluções"
        
    elif tipo == 'staff':
        members = queryset.filter(is_staff=True)[:50]
        titulo = "Membros do staff"
        
    elif tipo == 'moderadores':
        members = queryset.filter(cargos__pode_moderar=True).distinct()[:50]
        titulo = "Moderadores"
        
    else:
        members = queryset.order_by('-total_itens')[:50]
        titulo = "Todos os membros"
    
    # Novos membros para a sidebar
    novos_membros = Usuario.objects.filter(date_joined__gte=semana_passada).order_by('-date_joined')[:5]
    
    context = {
        'members': members,
        'tipo': tipo,
        'titulo': titulo,
        'busca_termo': busca,
        'novos_membros': novos_membros,
    }
    
    return render(request, 'accounts/members_list.html', context)

def online(request):
    """View para exibir usuários online"""
    from django.utils import timezone
    from datetime import timedelta
    from .models import UsuarioOnline
    
    # Filtro baseado na aba selecionada
    tab = request.GET.get('tab', 'all')
    
    # Tempo limite para considerar online (15 minutos)
    cutoff_time = timezone.now() - timedelta(minutes=15)
    
    # Base queryset
    base_queryset = UsuarioOnline.objects.filter(ultima_atividade__gte=cutoff_time)
    
    # Aplicar filtros baseados na aba
    if tab == 'members':
        online_users = base_queryset.filter(is_authenticated=True, is_bot=False)
    elif tab == 'guests':
        online_users = base_queryset.filter(is_authenticated=False, is_bot=False)
    elif tab == 'bots':
        online_users = base_queryset.filter(is_bot=True)
    else:  # tab == 'all'
        online_users = base_queryset
    
    # Ordenar por última atividade
    online_users = online_users.select_related('usuario').order_by('-ultima_atividade')
    
    # Estatísticas
    stats = {
        'total_online': base_queryset.count(),
        'members_online': base_queryset.filter(is_authenticated=True, is_bot=False).count(),
        'guests_online': base_queryset.filter(is_authenticated=False, is_bot=False).count(),
        'bots_online': base_queryset.filter(is_bot=True).count(),
    }
    
    # Preparar dados para o template
    online_list = []
    for user_online in online_users:
        # Calcular tempo desde última atividade
        time_diff = timezone.now() - user_online.ultima_atividade
        if time_diff.total_seconds() < 60:
            last_seen = "agora mesmo"
        elif time_diff.total_seconds() < 3600:
            minutes = int(time_diff.total_seconds() / 60)
            last_seen = f"{minutes} minuto{'s' if minutes != 1 else ''} atrás"
        else:
            hours = int(time_diff.total_seconds() / 3600)
            last_seen = f"{hours} hora{'s' if hours != 1 else ''} atrás"
        
        # Determinar ação atual baseada na página
        action = get_user_action(user_online.pagina_atual)
        
        # Adicionar à lista
        online_data = {
            'user_online': user_online,
            'last_seen': last_seen,
            'action': action,
        }
        online_list.append(online_data)
    
    context = {
        'online_list': online_list,
        'stats': stats,
        'current_tab': tab,
    }
    
    return render(request, 'accounts/online.html', context)

def get_user_action(path):
    """Determinar ação do usuário baseada no caminho atual"""
    if not path or path == '/':
        return "Visualizando a página inicial"
    
    # Padrões específicos do fórum
    if '/posts/' in path:
        segments = path.strip('/').split('/')
        if len(segments) >= 4:
            return f"Lendo tópico em <b>{segments[1].title()}</b>"
        else:
            return "Visualizando tópicos"
    elif '/accounts/members/' in path:
        if '?tipo=' in path:
            tipo = path.split('tipo=')[1].split('&')[0]
            tipos_map = {
                'mais_mensagens': 'membros com mais mensagens',
                'mais_hoje': 'membros mais ativos hoje',
                'mais_reacoes': 'membros com mais reações',
                'staff': 'membros do staff',
                'moderadores': 'moderadores'
            }
            return f"Visualizando {tipos_map.get(tipo, 'membros')}"
        else:
            return "Visualizando membros notáveis"
    elif '/accounts/online/' in path:
        return "Visualizando usuários online"
    elif '/accounts/profile/' in path:
        segments = path.strip('/').split('/')
        if len(segments) >= 3:
            return f"Visualizando perfil de <b>{segments[2]}</b>"
        else:
            return "Visualizando perfil"
    elif '/login/' in path:
        return "Fazendo login"
    elif '/register/' in path:
        return "Se registrando"
    elif '/logout/' in path:
        return "Fazendo logout"
    elif path.startswith('/admin/'):
        return "No painel administrativo"
    elif '/api/' in path:
        return "Acessando API"
    elif '/search/' in path:
        return "Fazendo uma pesquisa"
    else:
        # Tentar extrair informações mais específicas
        segments = path.strip('/').split('/')
        if len(segments) >= 1 and segments[0]:
            section_map = {
                'home': 'página inicial',
                'core': 'navegando',
                'static': 'carregando recursos',
                'media': 'visualizando mídia'
            }
            section = section_map.get(segments[0], segments[0])
            return f"Navegando em <b>{section}</b>"
        else:
            return "Navegando pelo fórum"

def profile(request):
    """Exibir perfil do usuário logado"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    usuario = request.user
    
    # Buscar atividades recentes
    try:
        from posts.models import Postagem, Reply
        # Últimas postagens do usuário
        ultimas_postagens = Postagem.objects.filter(autor=usuario).order_by('-criado_em')[:5]
        # Últimas respostas do usuário
        ultimas_respostas = Reply.objects.filter(autor=usuario).order_by('-criado_em')[:5]
        
        # Combinar e ordenar atividades por data
        atividades = []
        
        for post in ultimas_postagens:
            atividades.append({
                'tipo': 'post',
                'titulo': post.titulo,
                'conteudo': post.conteudo[:150] + '...' if len(post.conteudo) > 150 else post.conteudo,
                'data': post.criado_em,
                'url': f'/posts/{post.id}/'  # Ajustar URL conforme necessário
            })
            
        for reply in ultimas_respostas:
            atividades.append({
                'tipo': 'reply',
                'titulo': f'Comentou em: {reply.postagem.titulo if hasattr(reply, "postagem") else "Post"}',
                'conteudo': reply.conteudo[:150] + '...' if len(reply.conteudo) > 150 else reply.conteudo,
                'data': reply.criado_em,
                'url': f'/posts/{reply.postagem.id}/' if hasattr(reply, "postagem") else '#'
            })
        
        # Ordenar por data (mais recentes primeiro)
        atividades = sorted(atividades, key=lambda x: x['data'], reverse=True)[:10]
        
    except ImportError:
        ultimas_postagens = []
        ultimas_respostas = []
        atividades = []
    
    # Buscar últimos visitantes
    ultimos_visitantes = usuario.visitas_recebidas.all()[:5] if hasattr(usuario, 'visitas_recebidas') else []
    
    context = {
        'usuario': usuario,
        'ultimas_postagens': ultimas_postagens,
        'ultimas_respostas': ultimas_respostas,
        'atividades': atividades,
        'ultimos_visitantes': ultimos_visitantes,
        'total_seguidores': usuario.get_total_seguidores() if hasattr(usuario, 'get_total_seguidores') else 0,
        'data_cadastro': usuario.date_joined,
        'ultimo_acesso': usuario.ultimo_acesso if hasattr(usuario, 'ultimo_acesso') else usuario.last_login,
    }
    
    return render(request, 'accounts/profile.html', context)
