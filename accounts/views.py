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
    template_name = 'accounts/perfil.html'
    context_object_name = 'usuario_perfil'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario_perfil = self.get_object()
        
        # Registrar a visita ao perfil
        if self.request.user.is_authenticated:
            VisitaPerfil.registrar_visita(usuario_perfil, self.request.user)
        
        # Adicionar contexto adicional
        context['ultimos_visitantes'] = usuario_perfil.visitas_recebidas.all()[:5]
        context['total_seguidores'] = usuario_perfil.get_total_seguidores()
        context['seguindo'] = self.request.user.is_authenticated and self.request.user.esta_seguindo(usuario_perfil)
        
        # Últimas atividades (posts, respostas, etc.)
        from posts.models import Postagem, Reply
        context['ultimas_postagens'] = Postagem.objects.filter(autor=usuario_perfil).order_by('-criado_em')[:5]
        context['ultimas_respostas'] = Reply.objects.filter(autor=usuario_perfil).order_by('-criado_em')[:5]
        
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
    tipo = request.GET.get('tipo')
    if tipo == 'mais_mensagens':
        # Exemplo: ordena por total_itens (mensagens)
        members = Usuario.objects.all().order_by('-total_itens')[:50]
        return render(request, 'accounts/members_list.html', {'members': members, 'tipo': tipo})
    else:
        return render(request, 'accounts/members.html')

def online(request):
    return render(request, 'accounts/online.html')

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
