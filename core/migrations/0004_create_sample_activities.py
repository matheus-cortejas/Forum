from django.db import migrations
from django.utils import timezone

def create_sample_activities(apps, schema_editor):
    UltimaAtividade = apps.get_model('core', 'UltimaAtividade')
    Postagem = apps.get_model('posts', 'Postagem')
    Reply = apps.get_model('posts', 'Reply')
    Usuario = apps.get_model('accounts', 'Usuario')
    
    # Buscar posts e usuários existentes
    postagens = Postagem.objects.all()[:3]
    replies = Reply.objects.all()[:5]
    usuarios = Usuario.objects.all()
    
    if not postagens.exists() or not usuarios.exists():
        return
    
    # Criar atividades de exemplo
    atividades_data = [
        {
            'tipo': 'NOVO_THREAD',
            'usuario': postagens[0].autor if postagens else usuarios.first(),
            'postagem': postagens[0] if postagens else None,
        },
        {
            'tipo': 'NOVA_REPLY',
            'usuario': replies[0].autor if replies else usuarios.first(),
            'postagem': replies[0].postagem if replies else None,
            'reply': replies[0] if replies else None,
        },
        {
            'tipo': 'NOVO_THREAD',
            'usuario': postagens[1].autor if len(postagens) > 1 else usuarios.first(),
            'postagem': postagens[1] if len(postagens) > 1 else None,
        }
    ]
    
    for atividade_data in atividades_data:
        if atividade_data['usuario']:
            UltimaAtividade.objects.create(
                tipo=atividade_data['tipo'],
                usuario=atividade_data['usuario'],
                postagem=atividade_data.get('postagem'),
                reply=atividade_data.get('reply'),
                criado_em=timezone.now()
            )

def remove_sample_activities(apps, schema_editor):
    UltimaAtividade = apps.get_model('core', 'UltimaAtividade')
    UltimaAtividade.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0003_onlinerecord'),
        ('posts', '0009_create_sample_posts'),
    ]

    operations = [
        migrations.RunPython(create_sample_activities, remove_sample_activities),
    ]