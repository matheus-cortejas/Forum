from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from core.models import UltimaAtividade

class Command(BaseCommand):
    help = 'Remove atividades antigas do feed'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Manter atividades dos últimos N dias (padrão: 90)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas mostra quantas atividades seriam removidas sem remover'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        atividades_antigas = UltimaAtividade.objects.filter(criado_em__lt=cutoff_date)
        count = atividades_antigas.count()
        
        if dry_run:
            self.stdout.write(
                f'Seria removido: {count} atividades anteriores a {cutoff_date.date()}'
            )
        else:
            if count > 0:
                atividades_antigas.delete()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Removidas {count} atividades anteriores a {cutoff_date.date()}'
                    )
                )
            else:
                self.stdout.write('Nenhuma atividade antiga encontrada para remoção')
        
        total_restantes = UltimaAtividade.objects.count()
        self.stdout.write(f'Total de atividades restantes: {total_restantes}')
