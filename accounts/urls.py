from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Autenticação
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),  # Usar view customizada que aceita GET
    path('register/', views.register, name='register'),
    
    # Perfil
    path('profile/<str:username>/', views.PerfilDetailView.as_view(), name='perfil'),  # Para outros usuários
    path('profile/', views.profile, name='profile'),  # Para usuário logado
    path('perfil/editar/', views.EditarPerfilView.as_view(), name='editar_perfil'),
    path('seguir/<str:username>/', views.seguir_usuario, name='seguir_usuario'),

    # Membros
    path('members/', views.members, name='members'),
    path('online/', views.online, name='online'),
]