from django.contrib import admin
from .models import Tag, Topico, Post

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cor', 'slug')
    search_fields = ('nome',)
    prepopulated_fields = {'slug': ('nome',)}

@admin.register(Topico)
class TopicoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'assunto', 'autor', 'fixo', 'fechado', 'criado_em', 'visualizacoes')
    list_filter = ('assunto', 'tags', 'fixo', 'fechado', 'criado_em')
    search_fields = ('titulo', 'autor__username')
    prepopulated_fields = {'slug': ('titulo',)}
    raw_id_fields = ('autor',)
    date_hierarchy = 'criado_em'
    filter_horizontal = ('tags',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('topico', 'autor', 'criado_em', 'atualizado_em')
    list_filter = ('criado_em', 'atualizado_em')
    search_fields = ('conteudo', 'autor__username', 'topico__titulo')
    raw_id_fields = ('autor', 'topico')
    date_hierarchy = 'criado_em'