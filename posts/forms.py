from django import forms
from .models import Postagem as Post, Reply, Tag

class PostagemForm(forms.ModelForm):
    tags_especificas = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Digite tags separadas por vírgula (opcional)',
            'class': 'form-control'
        }),
        help_text='Tags específicas separadas por vírgula. Ex: python, django, web'
    )
    
    class Meta:
        model = Post
        fields = ['tipo', 'titulo', 'conteudo', 'tag_sistema', 'fixo']
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_tipo'
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o título...'
            }),
            'conteudo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Digite o conteúdo...'
            }),
            'tag_sistema': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fixo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'tipo': 'Tipo de Postagem',
            'titulo': 'Título',
            'conteudo': 'Conteúdo',
            'tag_sistema': 'Tag do Sistema (Prefixo)',
            'fixo': 'Fixar no topo (apenas threads)'
        }
    
    def __init__(self, *args, **kwargs):
        # Extract request from kwargs if provided
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Adicionar classe vazia como primeira opção para tag_sistema
        self.fields['tag_sistema'].empty_label = "Nenhuma tag do sistema"
        
        # Se não for staff, remover campo fixo
        if self.request and not self.request.user.is_staff:
            if 'fixo' in self.fields:
                del self.fields['fixo']
    
    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')
        if not titulo or len(titulo.strip()) < 5:
            raise forms.ValidationError('O título deve ter pelo menos 5 caracteres.')
        return titulo.strip()
    
    def clean_conteudo(self):
        conteudo = self.cleaned_data.get('conteudo')
        if not conteudo or len(conteudo.strip()) < 10:
            raise forms.ValidationError('O conteúdo deve ter pelo menos 10 caracteres.')
        return conteudo.strip()
    
    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        fixo = cleaned_data.get('fixo')
        
        # Apenas threads podem ser fixas
        if fixo and tipo != 'THREAD':
            raise forms.ValidationError('Apenas threads podem ser fixadas.')
        
        return cleaned_data

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['conteudo']
        widgets = {
            'conteudo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Digite sua resposta...'
            })
        }
        labels = {
            'conteudo': 'Resposta'
        }
    
    def clean_conteudo(self):
        conteudo = self.cleaned_data.get('conteudo')
        if not conteudo or len(conteudo.strip()) < 5:
            raise forms.ValidationError('A resposta deve ter pelo menos 5 caracteres.')
        return conteudo.strip()
