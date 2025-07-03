from django.db import migrations
from django.utils.text import slugify
from django.utils import timezone

def create_sample_posts(apps, schema_editor):
    Postagem = apps.get_model('posts', 'Postagem')
    Reply = apps.get_model('posts', 'Reply')
    TagEspecifica = apps.get_model('posts', 'TagEspecifica')
    Tag = apps.get_model('posts', 'Tag')
    Usuario = apps.get_model('accounts', 'Usuario')
    Assunto = apps.get_model('home', 'Assunto')
    
    # Buscar usuários e assuntos criados
    try:
        admin = Usuario.objects.get(username='admin')
        gamer = Usuario.objects.get(username='gamer_pro')
        tech = Usuario.objects.get(username='tech_enthusiast')
        newbie = Usuario.objects.get(username='newbie_user')
    except Usuario.DoesNotExist:
        # Se os usuários não existem, não criar posts
        return
    
    try:
        assunto_gow = Assunto.objects.get(titulo='God of War')
        assunto_programming = Assunto.objects.get(titulo='Programming')
        assunto_general = Assunto.objects.get(titulo='General Gaming')
        assunto_help = Assunto.objects.get(titulo='Help & Support')
    except Assunto.DoesNotExist:
        # Se os assuntos não existem, não criar posts
        return
    
    # Buscar tags do sistema
    tag_duvida = Tag.objects.filter(nome='Dúvida').first()
    tag_discussao = Tag.objects.filter(nome='Discussão').first()
    tag_tutorial = Tag.objects.filter(nome='Tutorial').first()
    
    # Posts de exemplo
    posts_data = [
        {
            'titulo': 'God of War Ragnarök - Impressões iniciais',
            'conteudo': '''Acabei de terminar as primeiras 10 horas de God of War Ragnarök e estou impressionado!
            
A continuação da história do Kratos e Atreus está incrível. Os gráficos melhoraram ainda mais e o combate está mais fluido.

O que vocês acharam do jogo? Quais foram suas partes favoritas até agora?

**Sem spoilers por favor!**''',
            'autor': gamer,
            'assunto': assunto_gow,
            'tipo': 'THREAD',
            'tag_sistema': tag_discussao,
            'tags_especificas': ['ragnarok', 'playstation', 'norse-mythology'],
            'visualizacoes': 156,
            'replies': [
                {
                    'autor': admin,
                    'conteudo': 'Concordo totalmente! A evolução dos personagens está fantástica. A relação pai e filho está cada vez melhor desenvolvida.'
                },
                {
                    'autor': tech,
                    'conteudo': 'Tecnicamente o jogo é impressionante. As transições sem loading e os detalhes ambientais são de outro nível!'
                },
                {
                    'autor': newbie,
                    'conteudo': 'Ainda não joguei, mas depois dessas reviews vou comprar com certeza!'
                }
            ]
        },
        {
            'titulo': 'Tutorial: Configurando ambiente Python para Django',
            'conteudo': '''Guia completo para configurar seu ambiente de desenvolvimento Python com Django.

## Pré-requisitos
- Python 3.8+
- pip
- virtualenv (recomendado)

## Passo a passo

### 1. Criar ambiente virtual
```bash
python -m venv meu_projeto
cd meu_projeto
source bin/activate  # Linux/Mac
# ou
Scripts\\activate  # Windows
```

### 2. Instalar Django
```bash
pip install django
```

### 3. Criar projeto
```bash
django-admin startproject meusite
cd meusite
python manage.py runserver
```

Pronto! Seu ambiente Django está configurado e rodando em http://127.0.0.1:8000/

Alguma dúvida? Postem nos comentários!''',
            'autor': tech,
            'assunto': assunto_programming,
            'tipo': 'THREAD',
            'tag_sistema': tag_tutorial,
            'tags_especificas': ['python', 'django', 'tutorial', 'iniciante'],
            'visualizacoes': 89,
            'replies': [
                {
                    'autor': newbie,
                    'conteudo': 'Excelente tutorial! Muito claro e direto ao ponto. Consegui configurar tudo seguindo os passos.'
                },
                {
                    'autor': admin,
                    'conteudo': 'Ótimo conteúdo! Vou fixar este tópico para que mais pessoas vejam.'
                }
            ]
        },
        {
            'titulo': 'Qual o melhor jogo de 2024 na opinião de vocês?',
            'conteudo': '''Estamos chegando ao final do ano e queria saber qual foi o jogo que mais impressionou vocês em 2024.

Algumas opções que me vêm à cabeça:
- Baldur's Gate 3
- Marvel's Spider-Man 2  
- Alan Wake 2
- Super Mario Bros. Wonder
- Starfield

E vocês? Qual foi o jogo do ano para vocês?''',
            'autor': gamer,
            'assunto': assunto_general,
            'tipo': 'THREAD',
            'tag_sistema': tag_discussao,
            'tags_especificas': ['goty', '2024', 'games'],
            'visualizacoes': 234,
            'replies': [
                {
                    'autor': tech,
                    'conteudo': 'Para mim foi Baldur\'s Gate 3, sem dúvidas. A profundidade do RPG é incrível!'
                },
                {
                    'autor': admin,
                    'conteudo': 'Spider-Man 2 me surpreendeu muito. O mundo aberto melhorou demais comparado ao primeiro.'
                }
            ]
        },
        {
            'titulo': 'Como fazer upload de avatar?',
            'conteudo': '''Pessoal, estou tentando fazer upload do meu avatar mas não estou conseguindo.

Clico em "Editar Perfil" mas não aparece a opção de alterar a foto. Alguém pode me ajudar?

O arquivo está em JPG e tem menos de 1MB.''',
            'autor': newbie,
            'assunto': assunto_help,
            'tipo': 'THREAD',
            'tag_sistema': tag_duvida,
            'tags_especificas': ['avatar', 'perfil', 'upload'],
            'visualizacoes': 45,
            'replies': [
                {
                    'autor': admin,
                    'conteudo': '''Olá! Para alterar seu avatar:
                    
1. Clique no seu nome no canto superior direito
2. Selecione "Meu Perfil"  
3. Clique em "Editar Perfil"
4. Na seção "Avatar", clique em "Escolher arquivo"
5. Selecione sua imagem e clique em "Salvar"

Se ainda não funcionar, me avise que vou verificar.'''
                },
                {
                    'autor': newbie,
                    'conteudo': 'Funcionou! Muito obrigado pela ajuda! 😊'
                }
            ]
        }
    ]
    
    # Criar as postagens
    for post_data in posts_data:
        postagem, created = Postagem.objects.get_or_create(
            titulo=post_data['titulo'],
            defaults={
                'slug': slugify(post_data['titulo']),
                'conteudo': post_data['conteudo'],
                'autor': post_data['autor'],
                'assunto': post_data['assunto'],
                'tipo': post_data['tipo'],
                'tag_sistema': post_data.get('tag_sistema'),
                'visualizacoes': post_data['visualizacoes']
            }
        )
        
        if created:
            # Adicionar tags específicas
            for tag_nome in post_data.get('tags_especificas', []):
                TagEspecifica.objects.get_or_create(
                    postagem=postagem,
                    nome=tag_nome
                )
            
            # Criar replies
            for reply_data in post_data.get('replies', []):
                Reply.objects.create(
                    postagem=postagem,
                    autor=reply_data['autor'],
                    conteudo=reply_data['conteudo']
                )

def remove_sample_posts(apps, schema_editor):
    Postagem = apps.get_model('posts', 'Postagem')
    Reply = apps.get_model('posts', 'Reply')
    TagEspecifica = apps.get_model('posts', 'TagEspecifica')
    
    TagEspecifica.objects.all().delete()
    Reply.objects.all().delete()
    Postagem.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('posts', '0008_create_sample_reactions'),
        ('accounts', '0006_create_sample_users'),
        ('home', '0002_create_sample_categories'),
    ]

    operations = [
        migrations.RunPython(create_sample_posts, remove_sample_posts),
    ]