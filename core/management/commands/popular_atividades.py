from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from posts.models import Postagem, Reply, ReacaoPostagem, ReacaoReply
from core.models import UltimaAtividade

class Command(BaseCommand):
    help = 'Popula o feed de atividades com dados existentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Número de dias para buscar atividades (padrão: 30)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpa todas as atividades existentes antes de popular'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Limpando atividades existentes...')
            UltimaAtividade.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Atividades limpas!'))

        days = options['days']
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(f'Buscando atividades dos últimos {days} dias...')

        # Postagens (threads e posts)
        postagens = Postagem.objects.filter(criado_em__gte=cutoff_date).order_by('criado_em')
        created_count = 0
        
        for postagem in postagens:
            tipo = 'NOVO_THREAD' if postagem.tipo == 'THREAD' else 'NOVO_POST'
            atividade, created = UltimaAtividade.objects.get_or_create(
                usuario=postagem.autor,
                tipo=tipo,
                postagem=postagem,
                criado_em=postagem.criado_em,
                defaults={'criado_em': postagem.criado_em}
            )
            if created:
                created_count += 1

        self.stdout.write(f'Criadas {created_count} atividades de postagens')

        # Replies
        replies = Reply.objects.filter(criado_em__gte=cutoff_date).order_by('criado_em')
        created_count = 0
        
        for reply in replies:
            atividade, created = UltimaAtividade.objects.get_or_create(
                usuario=reply.autor,
                tipo='NOVA_REPLY',
                postagem=reply.postagem,
                reply=reply,
                criado_em=reply.criado_em,
                defaults={'criado_em': reply.criado_em}
            )
            if created:
                created_count += 1

        self.stdout.write(f'Criadas {created_count} atividades de replies')

        # Reações em postagens
        reacoes_post = ReacaoPostagem.objects.filter(criado_em__gte=cutoff_date).order_by('criado_em')
        created_count = 0
        
        for reacao in reacoes_post:
            atividade, created = UltimaAtividade.objects.get_or_create(
                usuario=reacao.usuario,
                tipo='NOVA_REACAO_POST',
                postagem=reacao.postagem,
                reacao=reacao.reacao,
                criado_em=reacao.criado_em,
                defaults={'criado_em': reacao.criado_em}
            )
            if created:
                created_count += 1

        self.stdout.write(f'Criadas {created_count} atividades de reações em posts')

        # Reações em replies
        reacoes_reply = ReacaoReply.objects.filter(criado_em__gte=cutoff_date).order_by('criado_em')
        created_count = 0
        
        for reacao in reacoes_reply:
            atividade, created = UltimaAtividade.objects.get_or_create(
                usuario=reacao.usuario,
                tipo='NOVA_REACAO_REPLY',
                postagem=reacao.reply.postagem,
                reply=reacao.reply,
                reacao=reacao.reacao,
                criado_em=reacao.criado_em,
                defaults={'criado_em': reacao.criado_em}
            )
            if created:
                created_count += 1

        self.stdout.write(f'Criadas {created_count} atividades de reações em replies')

        total_atividades = UltimaAtividade.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'Processo concluído! Total de atividades: {total_atividades}'
            )
        )
