from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Postagem, Reply, ReacaoPostagem, ReacaoReply
from core.models import UltimaAtividade
from django.utils import timezone

@receiver(post_save, sender=Postagem)
def registrar_atividade_postagem(sender, instance, created, **kwargs):
    """Registra atividade quando uma nova postagem é criada"""
    if created:
        tipo_atividade = 'NOVO_THREAD' if instance.tipo == 'THREAD' else 'NOVO_POST'
        try:
            UltimaAtividade.objects.create(
                usuario=instance.autor,
                tipo=tipo_atividade,
                postagem=instance
            )
        except Exception as e:
            print(f"Erro ao registrar atividade de postagem: {e}")

@receiver(post_save, sender=Reply)
def registrar_atividade_reply(sender, instance, created, **kwargs):
    """Registra atividade quando uma nova reply é criada"""
    if created:
        try:
            UltimaAtividade.objects.create(
                usuario=instance.autor,
                tipo='NOVA_REPLY',
                postagem=instance.postagem,
                reply=instance
            )
        except Exception as e:
            print(f"Erro ao registrar atividade de reply: {e}")

@receiver(post_save, sender=ReacaoPostagem)
def registrar_atividade_reacao_postagem(sender, instance, created, **kwargs):
    """Registra atividade quando uma reação é adicionada a uma postagem"""
    if created:
        try:
            UltimaAtividade.objects.create(
                usuario=instance.usuario,
                tipo='NOVA_REACAO_POST',
                postagem=instance.postagem,
                reacao=instance.reacao
            )
        except Exception as e:
            print(f"Erro ao registrar atividade de reação em postagem: {e}")

@receiver(post_save, sender=ReacaoReply)
def registrar_atividade_reacao_reply(sender, instance, created, **kwargs):
    """Registra atividade quando uma reação é adicionada a uma reply"""
    if created:
        try:
            UltimaAtividade.objects.create(
                usuario=instance.usuario,
                tipo='NOVA_REACAO_REPLY',
                postagem=instance.reply.postagem,
                reply=instance.reply,
                reacao=instance.reacao
            )
        except Exception as e:
            print(f"Erro ao registrar atividade de reação em reply: {e}")

@receiver(post_save, sender=Postagem)
def atualizar_thread_count_assunto(sender, instance, created, **kwargs):
    """Atualiza contador de threads no assunto"""
    if created and instance.tipo == 'THREAD':
        try:
            from django.db.models import F
            instance.assunto.__class__.objects.filter(
                id=instance.assunto.id
            ).update(
                total_threads=F('total_threads') + 1
            )
        except Exception as e:
            print(f"Erro ao atualizar contador de threads: {e}")

@receiver(post_delete, sender=Postagem)
def decrementar_thread_count_assunto(sender, instance, **kwargs):
    """Decrementa contador de threads no assunto"""
    if instance.tipo == 'THREAD':
        try:
            from django.db.models import F
            instance.assunto.__class__.objects.filter(
                id=instance.assunto.id
            ).update(
                total_threads=F('total_threads') - 1
            )
        except Exception as e:
            print(f"Erro ao decrementar contador de threads: {e}")

@receiver(post_save, sender=Reply)
def atualizar_reply_count_postagem(sender, instance, created, **kwargs):
    """Atualiza contador de replies na postagem"""
    if created:
        try:
            from django.db.models import F
            instance.postagem.__class__.objects.filter(
                id=instance.postagem.id
            ).update(
                total_respostas=F('total_respostas') + 1,
                atualizado_em=timezone.now()
            )
        except Exception as e:
            print(f"Erro ao atualizar contador de replies: {e}")

@receiver(post_delete, sender=Reply)
def decrementar_reply_count_postagem(sender, instance, **kwargs):
    """Decrementa contador de replies na postagem"""
    try:
        from django.db.models import F
        from django.utils import timezone
        instance.postagem.__class__.objects.filter(
            id=instance.postagem.id
        ).update(
            total_respostas=F('total_respostas') - 1,
            atualizado_em=timezone.now()
        )
    except Exception as e:
        print(f"Erro ao decrementar contador de replies: {e}")