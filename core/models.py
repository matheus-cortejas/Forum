from django.db import models
from django.conf import settings
from posts.models import Postagem, Reacao
from django.utils import timezone

class UltimaAtividade(models.Model):
    """Registra as últimas atividades dos usuários para o feed de novidades"""
    TIPO_CHOICES = (
        ('NOVO_POST', 'Novo Post'),
        ('NOVA_REPLY', 'Nova Resposta'),
        ('NOVA_REACAO_POST', 'Nova Reação em Post'),
        ('NOVA_REACAO_REPLY', 'Nova Reação em Reply'),
        ('NOVO_THREAD', 'Novo Tópico'),
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='atividades'
    )
    tipo = models.CharField(max_length=25, choices=TIPO_CHOICES)
    postagem = models.ForeignKey(
        Postagem,
        on_delete=models.CASCADE,
        related_name='atividades',
        null=True,
        blank=True
    )
    reply = models.ForeignKey(
        'posts.Reply',
        on_delete=models.CASCADE,
        related_name='atividades',
        null=True,
        blank=True
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
        return f'{self.usuario} {self.get_tipo_display()}'

    def get_target_object(self):
        """Retorna o objeto alvo da atividade (postagem ou reply)"""
        if self.reply:
            return self.reply
        return self.postagem

    def get_target_post(self):
        """Retorna sempre a postagem principal (thread ou post)"""
        if self.reply:
            return self.reply.postagem
        return self.postagem

    def get_narrative_text(self):
        """Retorna texto narrativo para a atividade"""
        target_post = self.get_target_post()
        
        if self.tipo == 'NOVO_THREAD':
            return f"criou um novo tópico"
        elif self.tipo == 'NOVO_POST':
            return f"criou um novo post"
        elif self.tipo == 'NOVA_REPLY':
            return f"respondeu no tópico"
        elif self.tipo == 'NOVA_REACAO_POST':
            return f"reagiu com {self.reacao.nome} ao post"
        elif self.tipo == 'NOVA_REACAO_REPLY':
            return f"reagiu com {self.reacao.nome} à resposta"
        return f"realizou uma atividade"

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
        settings.AUTH_USER_MODEL,  # This correctly references accounts.Usuario
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
    
class OnlineRecord(models.Model):
    record_count = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Record de Usuários Online"
    
    def __str__(self):
        return f"Record: {self.record_count} usuários"
    
    @classmethod
    def get_current(cls):
        """Pega o record atual, cria se não existir"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj.record_count
    
    @classmethod
    def update_if_higher(cls, new_count):
        """Atualiza só se for maior"""
        obj, created = cls.objects.get_or_create(pk=1)
        if new_count > obj.record_count:
            obj.record_count = new_count
            obj.save()
        return obj.record_count        