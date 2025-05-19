from django.contrib import admin
from .models import UltimaAtividade, Pesquisa

@admin.register(UltimaAtividade)
class UltimaAtividadeAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'postagem', 'criado_em', 'tempo_relativo')
    list_filter = ('tipo', 'criado_em')
    search_fields = ('usuario__username', 'postagem__titulo')
    raw_id_fields = ('usuario', 'postagem', 'reacao')
    date_hierarchy = 'criado_em'
    readonly_fields = ('tempo_relativo',)

@admin.register(Pesquisa)
class PesquisaAdmin(admin.ModelAdmin):
    list_display = ('termo', 'usuario', 'apenas_titulo', 'subforum', 'ordenacao', 'criado_em')
    list_filter = ('apenas_titulo', 'ordenacao', 'criado_em')
    search_fields = ('termo', 'usuario__username', 'subforum')
    raw_id_fields = ('usuario',)
    date_hierarchy = 'criado_em'
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('usuario', 'termo', 'apenas_titulo')
        }),
        ('Filtros', {
            'fields': ('data_inicio', 'data_fim', 'min_respostas', 'subforum')
        }),
        ('Ordenação', {
            'fields': ('ordenacao',)
        })
    )