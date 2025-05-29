from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone

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


def logout(request):
    return render(request, 'accounts/logout.html')

def login(request):
    return render(request, 'accounts/login.html')

def register(request):
    return render(request, 'accounts/register.html')

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
    return render(request, 'accounts/profile.html')
