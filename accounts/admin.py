from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, CargoMembro, VisitaPerfil, UsuarioOnline

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
    list_display = ['usuario_visitado', 'visitante', 'timestamp'] 
    list_filter = ['timestamp', 'data']  
    search_fields = ['usuario_visitado__username', 'visitante__username']
    ordering = ['-timestamp'] 

@admin.register(UsuarioOnline)
class UsuarioOnlineAdmin(admin.ModelAdmin):
    """Admin para o modelo UsuarioOnline"""
    list_display = ['get_display_name', 'is_authenticated', 'is_bot', 'bot_name', 'pagina_atual', 'ultima_atividade']
    list_filter = ['is_authenticated', 'is_bot', 'ultima_atividade']
    search_fields = ['usuario__username', 'bot_name', 'ip_address', 'session_key']
    readonly_fields = ['session_key', 'ip_address', 'user_agent', 'ultima_atividade']
    ordering = ['-ultima_atividade']
    
    def get_display_name(self, obj):
        if obj.is_bot:
            return f"Bot: {obj.bot_name}"
        elif obj.usuario:
            return f"Membro: {obj.usuario.username}"
        else:
            return "Visitante"
    get_display_name.short_description = "Usuário"
    
    def has_add_permission(self, request):
        # Não permitir adicionar manualmente
        return False
    
    actions = ['cleanup_old_sessions']
    
    def cleanup_old_sessions(self, request, queryset):
        """Action para limpar sessões antigas"""
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_time = timezone.now() - timedelta(minutes=30)
        deleted_count = UsuarioOnline.objects.filter(ultima_atividade__lt=cutoff_time).delete()[0]
        
        self.message_user(request, f"{deleted_count} sessões antigas foram removidas.")
    cleanup_old_sessions.short_description = "Limpar sessões antigas (30+ min)"