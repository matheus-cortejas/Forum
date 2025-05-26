from django.db import migrations

def create_sample_tags(apps, schema_editor):
    Tag = apps.get_model('posts', 'Tag')
    
    tags_sistema = [
        {'nome': 'Dúvida', 'cor': '#FF6B6B', 'ordem': 1, 'slug': 'duvida'},
        {'nome': 'Discussão', 'cor': '#4ECDC4', 'ordem': 2, 'slug': 'discussao'},
        {'nome': 'Tutorial', 'cor': '#45B7D1', 'ordem': 3, 'slug': 'tutorial'},
        {'nome': 'Anúncio', 'cor': '#FFA726', 'ordem': 4, 'slug': 'anuncio'},
        {'nome': 'Resolvido', 'cor': '#66BB6A', 'ordem': 5, 'slug': 'resolvido'},
    ]
    
    for tag_data in tags_sistema:
        Tag.objects.get_or_create(
            nome=tag_data['nome'],
            defaults={
                'cor': tag_data['cor'],
                'ordem': tag_data['ordem'],
                'slug': tag_data['slug'],
                'is_sistema': True
            }
        )

def remove_sample_tags(apps, schema_editor):
    Tag = apps.get_model('posts', 'Tag')
    Tag.objects.filter(is_sistema=True).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_alter_tag_cor'),
    ]

    operations = [
        migrations.RunPython(create_sample_tags, remove_sample_tags),
    ]
