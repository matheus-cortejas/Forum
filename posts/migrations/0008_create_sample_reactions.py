from django.db import migrations
import os
from django.core.files.base import ContentFile

def create_sample_reactions(apps, schema_editor):
    Reacao = apps.get_model('posts', 'Reacao')
    
    # Reações básicas do fórum
    reacoes_data = [
        {'nome': 'Like', 'ordem': 1, 'ativo': True},
        {'nome': 'Love', 'ordem': 2, 'ativo': True},
        {'nome': 'Laugh', 'ordem': 3, 'ativo': True},
        {'nome': 'Wow', 'ordem': 4, 'ativo': True},
        {'nome': 'Sad', 'ordem': 5, 'ativo': True},
        {'nome': 'Angry', 'ordem': 6, 'ativo': True},
        {'nome': 'Thanks', 'ordem': 7, 'ativo': True},
        {'nome': 'Confused', 'ordem': 8, 'ativo': True},
    ]
    
    for reacao_data in reacoes_data:
        # Criar reação sem arquivo de imagem (você pode adicionar depois)
        Reacao.objects.get_or_create(
            nome=reacao_data['nome'],
            defaults={
                'ordem': reacao_data['ordem'],
                'ativo': reacao_data['ativo'],
            }
        )

def remove_sample_reactions(apps, schema_editor):
    Reacao = apps.get_model('posts', 'Reacao')
    Reacao.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('posts', '0007_reacaoreply'),
    ]

    operations = [
        migrations.RunPython(create_sample_reactions, remove_sample_reactions),
    ]