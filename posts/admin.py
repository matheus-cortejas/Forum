from django.contrib import admin
from .models import Tag, TagEspecifica, Reacao, ReacaoPostagem, Postagem, Reply, ReacaoReply

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cor', 'ordem', 'is_sistema')
    list_filter = ('is_sistema',)
    search_fields = ('nome',)
    prepopulated_fields = {'slug': ('nome',)}
    list_editable = ('cor', 'ordem', 'is_sistema')

class TagEspecificaInline(admin.TabularInline):
    model = TagEspecifica
    extra = 1

@admin.register(Reacao)
class ReacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ordem', 'ativo', 'icone_preview')
    list_editable = ('ordem', 'ativo')
    search_fields = ('nome',)
    list_filter = ('ativo',)

    def icone_preview(self, obj):
        """Mostra preview do ícone no admin"""
        if obj.icone:
            return f'<img src="{obj.icone.url}" width="30" height="30" style="border-radius: 3px;" />'
        return "Sem ícone"
    icone_preview.allow_tags = True
    icone_preview.short_description = "Preview"

@admin.register(ReacaoPostagem)
class ReacaoPostagemAdmin(admin.ModelAdmin):
    list_display = ('postagem', 'reacao', 'usuario', 'criado_em')
    list_filter = ('reacao', 'criado_em')
    search_fields = ('postagem__titulo', 'usuario__username')
    raw_id_fields = ('postagem', 'usuario', 'reacao')
    date_hierarchy = 'criado_em'

@admin.register(Postagem)
class PostagemAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'assunto', 'autor', 'tag_sistema', 'fixo', 'fechado', 'criado_em', 'visualizacoes')
    list_filter = ('tipo', 'assunto', 'tag_sistema', 'fixo', 'fechado', 'criado_em')
    search_fields = ('titulo', 'autor__username')
    prepopulated_fields = {'slug': ('titulo',)}
    raw_id_fields = ('autor', 'assunto')
    date_hierarchy = 'criado_em'
    list_editable = ('fixo', 'fechado')
    inlines = [TagEspecificaInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('tipo', 'titulo', 'slug', 'autor', 'assunto', 'conteudo')
        }),
        ('Tags', {
            'fields': ('tag_sistema',)
        }),
        ('Status', {
            'fields': ('fixo', 'fechado', 'visualizacoes')
        })
    )

@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ('postagem', 'autor', 'criado_em', 'atualizado_em')
    list_filter = ('criado_em', 'postagem__assunto')
    search_fields = ('conteudo', 'autor__username', 'postagem__titulo')
    raw_id_fields = ('autor', 'postagem')
    date_hierarchy = 'criado_em'

# REMOVER DUPLICAÇÃO - apenas um ReacaoReplyAdmin
@admin.register(ReacaoReply)
class ReacaoReplyAdmin(admin.ModelAdmin):
    list_display = ('reply', 'reacao', 'usuario', 'criado_em')
    list_filter = ('reacao', 'criado_em')
    search_fields = ('reply__conteudo', 'usuario__username')
    raw_id_fields = ('reply', 'usuario', 'reacao')
    date_hierarchy = 'criado_em'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'reply__postagem', 'usuario', 'reacao'
        )