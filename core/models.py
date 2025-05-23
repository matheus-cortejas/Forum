from django.db import models
from django.conf import settings
from posts.models import Postagem, Reacao
from django.utils import timezone

class UltimaAtividade(models.Model):
    """Registra as últimas atividades dos usuários para o feed de novidades"""
    TIPO_CHOICES = (
        ('NOVO_POST', 'Novo Post'),
        ('NOVA_REPLY', 'Nova Resposta'),
        ('NOVA_REACAO', 'Nova Reação'),
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='atividades'
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    postagem = models.ForeignKey(
        Postagem,
        on_delete=models.CASCADE,
        related_name='atividades'
    )
    reacao = models.ForeignKey(
        Reacao,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='atividades'
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Última Atividade'
        verbose_name_plural = 'Últimas Atividades'

    def __str__(self):
        return f'{self.usuario} {self.get_tipo_display()} em {self.postagem}'

    def tempo_relativo(self):
        """Retorna tempo em formato relativo (ex: '5 minutos atrás')"""
        agora = timezone.now()
        diff = agora - self.criado_em
        
        if diff.days > 0:
            return f'{diff.days} dias atrás'
        elif diff.seconds > 3600:
            horas = diff.seconds // 3600
            return f'{horas} horas atrás'
        else:
            minutos = diff.seconds // 60
            return f'{minutos} minutos atrás'

class Pesquisa(models.Model):
    """Modelo para armazenar parâmetros de pesquisa"""
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pesquisas'
    )
    termo = models.CharField('Palavras-chave', max_length=200)
    apenas_titulo = models.BooleanField('Pesquisar apenas por título', default=False)
    data_inicio = models.DateField('Data inicial', null=True, blank=True)
    data_fim = models.DateField('Data final', null=True, blank=True)
    min_respostas = models.PositiveIntegerField('Número mínimo de respostas', default=0)
    subforum = models.CharField('Pesquisar no Fórum', max_length=100, blank=True)
    ordenacao = models.CharField(
        'Ordenar por',
        max_length=20,
        choices=(
            ('relevance', 'Relevância'),
            ('date', 'Data'),
            ('replies', 'Mais Respondidos')
        ),
        default='relevance'
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Pesquisa'
        verbose_name_plural = 'Pesquisas'

    def __str__(self):
        return f'Pesquisa: {self.termo} por {self.usuario}'