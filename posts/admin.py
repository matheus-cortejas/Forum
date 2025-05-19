from django.contrib import admin
from .models import Tag, TagEspecifica, Reacao, ReacaoPostagem, Postagem, Reply

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
    list_display = ('nome', 'ordem', 'ativo')
    list_editable = ('ordem', 'ativo')
    search_fields = ('nome',)
    list_filter = ('ativo',)

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