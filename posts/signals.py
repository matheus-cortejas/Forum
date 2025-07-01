from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ReacaoPostagem, ReacaoReply, Postagem, Reply
from core.models import UltimaAtividade

@receiver(post_save, sender=Postagem)
def registrar_atividade_postagem(sender, instance, created, **kwargs):
    """Registra atividade quando uma nova postagem é criada"""
    if created:
        tipo_atividade = 'NOVO_THREAD' if instance.tipo == 'THREAD' else 'NOVO_POST'
        UltimaAtividade.objects.create(
            usuario=instance.autor,
            tipo=tipo_atividade,
            postagem=instance
        )

@receiver(post_save, sender=Reply)
def registrar_atividade_reply(sender, instance, created, **kwargs):
    """Registra atividade quando uma nova reply é criada"""
    if created:
        UltimaAtividade.objects.create(
            usuario=instance.autor,
            tipo='NOVA_REPLY',
            postagem=instance.postagem,
            reply=instance
        )

@receiver(post_save, sender=ReacaoPostagem)
def registrar_atividade_reacao_postagem(sender, instance, created, **kwargs):
    """Registra atividade quando uma reação é adicionada a uma postagem"""
    if created:
        UltimaAtividade.objects.create(
            usuario=instance.usuario,
            tipo='NOVA_REACAO_POST',
            postagem=instance.postagem,
            reacao=instance.reacao
        )

@receiver(post_save, sender=ReacaoReply)
def registrar_atividade_reacao_reply(sender, instance, created, **kwargs):
    """Registra atividade quando uma reação é adicionada a uma reply"""
    if created:
        UltimaAtividade.objects.create(
            usuario=instance.usuario,
            tipo='NOVA_REACAO_REPLY',
            postagem=instance.reply.postagem,
            reply=instance.reply,
            reacao=instance.reacao
        )

@receiver(post_save, sender=ReacaoPostagem)
def aumentar_reputacao_postagem(sender, instance, created, **kwargs):
    """Aumenta reputação quando recebe reação em postagem"""
    if created:
        autor = instance.postagem.autor
        autor.reputacao = (autor.reputacao or 0) + 1
        autor.save(update_fields=['reputacao'])

@receiver(post_delete, sender=ReacaoPostagem)
def diminuir_reputacao_postagem(sender, instance, **kwargs):
    """Diminui reputação quando remove reação em postagem"""
    autor = instance.postagem.autor
    autor.reputacao = max(0, (autor.reputacao or 1) - 1)
    autor.save(update_fields=['reputacao'])

@receiver(post_save, sender=ReacaoReply)
def aumentar_reputacao_reply(sender, instance, created, **kwargs):
    """Aumenta reputação quando recebe reação em reply"""
    if created:
        autor = instance.reply.autor
        autor.reputacao = (autor.reputacao or 0) + 1
        autor.save(update_fields=['reputacao'])

@receiver(post_delete, sender=ReacaoReply)
def diminuir_reputacao_reply(sender, instance, **kwargs):
    """Diminui reputação quando remove reação em reply"""
    autor = instance.reply.autor
    autor.reputacao = max(0, (autor.reputacao or 1) - 1)
    autor.save(update_fields=['reputacao'])