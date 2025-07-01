from django.contrib import admin
from .models import UltimaAtividade, Pesquisa

@admin.register(UltimaAtividade)
class UltimaAtividadeAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'get_target_display', 'criado_em', 'get_tempo_relativo')
    list_filter = ('tipo', 'criado_em', 'reacao')
    search_fields = ('usuario__username', 'postagem__titulo', 'reply__conteudo')
    raw_id_fields = ('usuario', 'postagem', 'reply', 'reacao')
    date_hierarchy = 'criado_em'
    readonly_fields = ('get_tempo_relativo', 'get_narrative_display')
    
    def get_target_display(self, obj):
        if obj.reply:
            return f"Reply em: {obj.reply.postagem.titulo}"
        elif obj.postagem:
            return obj.postagem.titulo
        return "Sem alvo"
    get_target_display.short_description = 'Alvo'
    
    def get_tempo_relativo(self, obj):
        return obj.criado_em
    get_tempo_relativo.short_description = 'Tempo Relativo'
    
    def get_narrative_display(self, obj):
        return obj.get_narrative_text()
    get_narrative_display.short_description = 'Narrativa'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('usuario', 'tipo', 'criado_em')
        }),
        ('Alvos', {
            'fields': ('postagem', 'reply', 'reacao')
        }),
        ('Visualização', {
            'fields': ('get_narrative_display',),
            'classes': ('collapse',)
        })
    )

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