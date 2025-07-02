from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

@receiver(post_save, sender='posts.Postagem')
def atualizar_estatisticas_usuario(sender, instance, created, **kwargs):
    if created:
        usuario = instance.autor
        usuario.total_itens += 1
        usuario.save(update_fields=['total_itens'])

@receiver(post_save, sender='posts.Reply')
def atualizar_estatisticas_resposta(sender, instance, created, **kwargs):
    if created:
        usuario = instance.autor
        usuario.total_itens += 1
        usuario.save(update_fields=['total_itens'])

@receiver(post_save, sender='posts.Postagem')
def atualizar_posts_count(sender, instance, created, **kwargs):
    if created:
        usuario = instance.autor
        usuario.posts_count = sender.objects.filter(autor=usuario).count()
        usuario.save(update_fields=['posts_count'])

@receiver(post_save, sender='posts.Reply')
def atualizar_answers_count(sender, instance, created, **kwargs):
    if created:
        usuario = instance.autor
        usuario.answers = sender.objects.filter(autor=usuario).count()
        usuario.save(update_fields=['answers'])

@receiver(post_save, sender='posts.ReacaoPostagem')
def atualizar_reputacao_post(sender, instance, created, **kwargs):
    if created:
        post_autor = instance.postagem.autor
        post_autor.reputacao += 1
        post_autor.save(update_fields=['reputacao'])

@receiver(post_save, sender='posts.ReacaoReply')
def atualizar_reputacao_reply(sender, instance, created, **kwargs):
    if created:
        reply_autor = instance.reply.autor
        reply_autor.reputacao += 1
        reply_autor.save(update_fields=['reputacao'])

@receiver(post_delete, sender='posts.ReacaoPostagem')
def diminuir_reputacao_post(sender, instance, **kwargs):
    post_autor = instance.postagem.autor
    post_autor.reputacao = max(0, post_autor.reputacao - 1)
    post_autor.save(update_fields=['reputacao'])

@receiver(post_delete, sender='posts.ReacaoReply')
def diminuir_reputacao_reply(sender, instance, **kwargs):
    reply_autor = instance.reply.autor
    reply_autor.reputacao = max(0, reply_autor.reputacao - 1)
    reply_autor.save(update_fields=['reputacao'])