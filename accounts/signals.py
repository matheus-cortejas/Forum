from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import F

@receiver(post_save, sender='posts.Postagem')
def atualizar_estatisticas_postagem(sender, instance, created, **kwargs):
    """Atualiza estatísticas quando uma postagem é criada"""
    if created:
        # Usar F() expressions para evitar race conditions
        instance.autor.__class__.objects.filter(id=instance.autor.id).update(
            total_itens=F('total_itens') + 1,
            posts_count=F('posts_count') + 1
        )

@receiver(post_delete, sender='posts.Postagem')
def decrementar_estatisticas_postagem(sender, instance, **kwargs):
    """Decrementa estatísticas quando uma postagem é deletada"""
    instance.autor.__class__.objects.filter(id=instance.autor.id).update(
        total_itens=F('total_itens') - 1,
        posts_count=F('posts_count') - 1
    )

@receiver(post_save, sender='posts.Reply')
def atualizar_estatisticas_reply(sender, instance, created, **kwargs):
    """Atualiza estatísticas quando uma reply é criada"""
    if created:
        instance.autor.__class__.objects.filter(id=instance.autor.id).update(
            total_itens=F('total_itens') + 1,
            answers=F('answers') + 1
        )

@receiver(post_delete, sender='posts.Reply')
def decrementar_estatisticas_reply(sender, instance, **kwargs):
    """Decrementa estatísticas quando uma reply é deletada"""
    instance.autor.__class__.objects.filter(id=instance.autor.id).update(
        total_itens=F('total_itens') - 1,
        answers=F('answers') - 1
    )

@receiver(post_save, sender='posts.ReacaoPostagem')
def atualizar_reputacao_postagem(sender, instance, created, **kwargs):
    """Aumenta reputação quando recebe reação em postagem"""
    if created:
        instance.postagem.autor.__class__.objects.filter(
            id=instance.postagem.autor.id
        ).update(
            reputacao=F('reputacao') + 1
        )

@receiver(post_delete, sender='posts.ReacaoPostagem')
def decrementar_reputacao_postagem(sender, instance, **kwargs):
    """Diminui reputação quando reação é removida de postagem"""
    instance.postagem.autor.__class__.objects.filter(
        id=instance.postagem.autor.id
    ).update(
        reputacao=F('reputacao') - 1
    )

@receiver(post_save, sender='posts.ReacaoReply')
def atualizar_reputacao_reply(sender, instance, created, **kwargs):
    """Aumenta reputação quando recebe reação em reply"""
    if created:
        instance.reply.autor.__class__.objects.filter(
            id=instance.reply.autor.id
        ).update(
            reputacao=F('reputacao') + 1
        )

@receiver(post_delete, sender='posts.ReacaoReply')
def decrementar_reputacao_reply(sender, instance, **kwargs):
    """Diminui reputação quando reação é removida de reply"""
    instance.reply.autor.__class__.objects.filter(
        id=instance.reply.autor.id
    ).update(
        reputacao=F('reputacao') - 1
    )