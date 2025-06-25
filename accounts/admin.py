from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, CargoMembro, VisitaPerfil

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Admin customizado para o modelo Usuario"""
    
    # Campos exibidos na lista
    list_display = ['username', 'email', 'apelido', 'is_active', 'is_staff', 'cadastrado_em']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'cadastrado_em']
    search_fields = ['username', 'email', 'apelido']
    ordering = ['-cadastrado_em']
    
    # Campos no formulário de edição
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {
            'fields': ('apelido', 'avatar', 'biografia', 'data_nascimento', 
                      'localizacao', 'site', 'cargos')
        }),
        ('Estatísticas', {
            'fields': ('total_itens', 'reputacao', 'answers', 'ultimo_acesso')
        }),
    )
    
    # Campos no formulário de criação
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais', {
            'fields': ('email', 'apelido')
        }),
    )
    
    # Campos many-to-many
    filter_horizontal = ['groups', 'user_permissions', 'cargos', 'seguidores']

@admin.register(CargoMembro)
class CargoMembroAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cor', 'ordem']
    list_editable = ['cor', 'ordem']
    ordering = ['ordem']

@admin.register(VisitaPerfil)
class VisitaPerfilAdmin(admin.ModelAdmin):
    # Corrigido: usar os campos corretos do modelo
    list_display = ['usuario_visitado', 'visitante', 'timestamp']  # Era 'data_visita'
    list_filter = ['timestamp', 'data']  # Era 'data_visita'
    search_fields = ['usuario_visitado__username', 'visitante__username']
    ordering = ['-timestamp']  # Era 'data_visita'