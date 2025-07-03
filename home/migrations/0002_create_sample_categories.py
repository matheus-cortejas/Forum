from django.db import migrations
from django.utils.text import slugify

def create_sample_categories(apps, schema_editor):
    Categoria = apps.get_model('home', 'Categoria')
    Assunto = apps.get_model('home', 'Assunto')
    
    # Categorias de exemplo
    categorias_data = [
        {
            'nome': 'Games',
            'ordem': 1,
            'assuntos': [
                {'titulo': 'God of War', 'descricao': 'Discussões sobre a série God of War'},
                {'titulo': 'The Last of Us', 'descricao': 'Tudo sobre The Last of Us'},
                {'titulo': 'Spider-Man', 'descricao': 'Marvel\'s Spider-Man discussions'},
                {'titulo': 'General Gaming', 'descricao': 'Discussões gerais sobre games'},
            ]
        },
        {
            'nome': 'Technology',
            'ordem': 2,
            'assuntos': [
                {'titulo': 'Programming', 'descricao': 'Desenvolvimento e programação'},
                {'titulo': 'Hardware', 'descricao': 'Discussões sobre hardware'},
                {'titulo': 'Software', 'descricao': 'Reviews e discussões de software'},
                {'titulo': 'AI & Machine Learning', 'descricao': 'Inteligência Artificial e ML'},
            ]
        },
        {
            'nome': 'General',
            'ordem': 3,
            'assuntos': [
                {'titulo': 'Off Topic', 'descricao': 'Conversas gerais'},
                {'titulo': 'News', 'descricao': 'Notícias e atualidades'},
                {'titulo': 'Help & Support', 'descricao': 'Ajuda e suporte do fórum'},
                {'titulo': 'Feedback', 'descricao': 'Sugestões e feedback'},
            ]
        },
        {
            'nome': 'Entertainment',
            'ordem': 4,
            'assuntos': [
                {'titulo': 'Movies', 'descricao': 'Discussões sobre filmes'},
                {'titulo': 'TV Shows', 'descricao': 'Séries de TV'},
                {'titulo': 'Music', 'descricao': 'Discussões musicais'},
                {'titulo': 'Books', 'descricao': 'Literatura e livros'},
            ]
        }
    ]
    
    for cat_data in categorias_data:
        categoria, created = Categoria.objects.get_or_create(
            nome=cat_data['nome'],
            defaults={
                'slug': slugify(cat_data['nome']),
                'ordem': cat_data['ordem']
            }
        )
        
        # Criar assuntos para esta categoria
        for i, assunto_data in enumerate(cat_data['assuntos'], 1):
            Assunto.objects.get_or_create(
                titulo=assunto_data['titulo'],
                categoria=categoria,
                defaults={
                    'slug': slugify(assunto_data['titulo']),
                    'descricao': assunto_data['descricao'],
                    'ordem': i
                }
            )

def remove_sample_categories(apps, schema_editor):
    Categoria = apps.get_model('home', 'Categoria')
    Assunto = apps.get_model('home', 'Assunto')
    Assunto.objects.all().delete()
    Categoria.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('home', '0001_initial'),
        ('posts', '0006_create_sample_tags'),
    ]

    operations = [
        migrations.RunPython(create_sample_categories, remove_sample_categories),
    ]