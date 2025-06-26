from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ReacaoPostagem, ReacaoReply

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