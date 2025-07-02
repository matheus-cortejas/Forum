from django import forms
from .models import Usuario

class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'nome_real', 'avatar', 'biografia', 'data_nascimento', 
            'localizacao', 'site'
        ]
        widgets = {
            'nome_real': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Seu nome real'
            }),
            'biografia': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Conte um pouco sobre você...',
                'maxlength': 500
            }),
            'data_nascimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'localizacao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sua localização'
            }),
            'site': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://seusite.com'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        labels = {
            'nome_real': 'Nome Real',
            'biografia': 'Sobre mim',
            'data_nascimento': 'Data de Nascimento',
            'localizacao': 'Localização',
            'site': 'Website',
            'avatar': 'Foto de Perfil'
        }
