# Generated by Django 5.2 on 2025-07-02 12:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_usuario_nome_real_usuario_posts_count_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuarioonline',
            name='usuario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sessoes_online', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='usuarioonline',
            index=models.Index(fields=['usuario'], name='accounts_us_usuario_83a2aa_idx'),
        ),
        migrations.AddIndex(
            model_name='usuarioonline',
            index=models.Index(fields=['ultima_atividade'], name='accounts_us_ultima__0bcd38_idx'),
        ),
        migrations.AddIndex(
            model_name='usuarioonline',
            index=models.Index(fields=['is_authenticated'], name='accounts_us_is_auth_c1cca6_idx'),
        ),
    ]
