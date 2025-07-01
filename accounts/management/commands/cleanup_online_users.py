from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import UsuarioOnline


class Command(BaseCommand):
    help = 'Limpa sessões de usuários online antigas (mais de 30 minutos)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--minutes',
            type=int,
            default=30,
            help='Minutos para considerar uma sessão como antiga (padrão: 30)',
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra quantas sessões seriam deletadas sem deletar de fato',
        )

    def handle(self, *args, **options):
        minutes = options['minutes']
        dry_run = options['dry_run']
        
        cutoff_time = timezone.now() - timedelta(minutes=minutes)
        
        # Contar sessões que serão deletadas
        old_sessions = UsuarioOnline.objects.filter(ultima_atividade__lt=cutoff_time)
        count = old_sessions.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: {count} sessões seriam deletadas (mais antigas que {minutes} minutos)'
                )
            )
            return
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('Nenhuma sessão antiga encontrada para limpar.')
            )
            return
        
        # Deletar sessões antigas
        deleted_count = old_sessions.delete()[0]
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Limpeza concluída: {deleted_count} sessões antigas foram removidas.'
            )
        )
        
        # Mostrar estatísticas atuais
        current_online = UsuarioOnline.objects.count()
        self.stdout.write(f'Usuários online atualmente: {current_online}')
