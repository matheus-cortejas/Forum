from django.contrib import admin
from .models import Categoria, Assunto

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ordem', 'slug')
    prepopulated_fields = {'slug': ('nome',)}
    ordering = ('ordem', 'nome')

@admin.register(Assunto)
class AssuntoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'ordem', 'slug')
    list_filter = ('categoria',)
    prepopulated_fields = {'slug': ('titulo',)}
    ordering = ('categoria', 'ordem', 'titulo')