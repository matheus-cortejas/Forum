from django.db import migrations
from django.contrib.auth.hashers import make_password
from django.utils.text import slugify

def create_sample_users(apps, schema_editor):
    Usuario = apps.get_model('accounts', 'Usuario')
    CargoMembro = apps.get_model('accounts', 'CargoMembro')
    
    # Criar cargos de exemplo
    cargos_data = [
        {
            'nome': 'Administrator',
            'cor': '#E53E3E',
            'pode_moderar': True,
            'pode_fixar_topicos': True,
            'pode_fechar_topicos': True,
            'pode_editar_outros_posts': True,
            'pode_excluir_outros_posts': True,
            'pode_banir_usuarios': True,
            'ordem': 1
        },
        {
            'nome': 'Moderator',
            'cor': '#38A169',
            'pode_moderar': True,
            'pode_fixar_topicos': True,
            'pode_fechar_topicos': True,
            'pode_editar_outros_posts': True,
            'pode_excluir_outros_posts': False,
            'pode_banir_usuarios': False,
            'ordem': 2
        },
        {
            'nome': 'VIP Member',
            'cor': '#D69E2E',
            'pode_moderar': False,
            'ordem': 3
        },
        {
            'nome': 'Active Member',
            'cor': '#3182CE',
            'pode_moderar': False,
            'ordem': 4
        }
    ]
    
    cargos_criados = {}
    for cargo_data in cargos_data:
        cargo, created = CargoMembro.objects.get_or_create(
            nome=cargo_data['nome'],
            defaults={
                'slug': slugify(cargo_data['nome']),
                'cor': cargo_data['cor'],
                'pode_moderar': cargo_data.get('pode_moderar', False),
                'pode_fixar_topicos': cargo_data.get('pode_fixar_topicos', False),
                'pode_fechar_topicos': cargo_data.get('pode_fechar_topicos', False),
                'pode_editar_outros_posts': cargo_data.get('pode_editar_outros_posts', False),
                'pode_excluir_outros_posts': cargo_data.get('pode_excluir_outros_posts', False),
                'pode_banir_usuarios': cargo_data.get('pode_banir_usuarios', False),
                'ordem': cargo_data['ordem']
            }
        )
        cargos_criados[cargo_data['nome']] = cargo
    
    # Criar usuários de exemplo
    usuarios_data = [
        {
            'username': 'admin',
            'email': 'admin@forum.com',
            'first_name': 'Administrator',
            'apelido': 'Admin',
            'biografia': 'Administrador do fórum',
            'total_itens': 150,
            'reputacao': 500,
            'answers': 25,
            'is_staff': True,
            'is_superuser': True,
            'cargo': 'Administrator'
        },
        {
            'username': 'moderator',
            'email': 'mod@forum.com',
            'first_name': 'Moderator',
            'apelido': 'Mod',
            'biografia': 'Moderador ativo do fórum',
            'total_itens': 75,
            'reputacao': 200,
            'answers': 15,
            'is_staff': True,
            'cargo': 'Moderator'
        },
        {
            'username': 'gamer_pro',
            'email': 'gamer@forum.com',
            'first_name': 'Pro',
            'last_name': 'Gamer',
            'apelido': 'ProGamer',
            'biografia': 'Apaixonado por games desde sempre!',
            'localizacao': 'São Paulo, SP',
            'total_itens': 120,
            'reputacao': 180,
            'answers': 8,
            'cargo': 'VIP Member'
        },
        {
            'username': 'tech_enthusiast',
            'email': 'tech@forum.com',
            'first_name': 'Tech',
            'last_name': 'User',
            'apelido': 'TechGuru',
            'biografia': 'Desenvolvedor e entusiasta de tecnologia',
            'localizacao': 'Rio de Janeiro, RJ',
            'site': 'https://techblog.com',
            'total_itens': 89,
            'reputacao': 145,
            'answers': 12,
            'cargo': 'Active Member'
        },
        {
            'username': 'newbie_user',
            'email': 'newbie@forum.com',
            'first_name': 'New',
            'last_name': 'User',
            'apelido': 'Newbie',
            'biografia': 'Novo no fórum, aprendendo sempre!',
            'total_itens': 5,
            'reputacao': 10,
            'answers': 0,
        }
    ]
    
    for user_data in usuarios_data:
        cargo = None
        if 'cargo' in user_data:
            cargo = cargos_criados.get(user_data['cargo'])
        
        usuario, created = Usuario.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data.get('last_name', ''),
                'password': make_password('123456'),  # Senha padrão para demo
                'apelido': user_data['apelido'],
                'biografia': user_data['biografia'],
                'localizacao': user_data.get('localizacao', ''),
                'site': user_data.get('site', ''),
                'total_itens': user_data['total_itens'],
                'reputacao': user_data['reputacao'],
                'answers': user_data['answers'],
                'is_staff': user_data.get('is_staff', False),
                'is_superuser': user_data.get('is_superuser', False),
                'is_active': True,
            }
        )
        
        if cargo and created:
            usuario.cargos.add(cargo)

def remove_sample_users(apps, schema_editor):
    Usuario = apps.get_model('accounts', 'Usuario')
    CargoMembro = apps.get_model('accounts', 'CargoMembro')
    
    # Remover usuários de exemplo (exceto superuser original)
    Usuario.objects.filter(username__in=[
        'admin', 'moderator', 'gamer_pro', 'tech_enthusiast', 'newbie_user'
    ]).delete()
    
    CargoMembro.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0005_alter_usuarioonline_usuario_and_more'),
    ]

    operations = [
        migrations.RunPython(create_sample_users, remove_sample_users),
    ]