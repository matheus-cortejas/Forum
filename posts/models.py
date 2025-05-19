from django.db import models
from django.conf import settings
from home.models import Assunto
from django.utils.text import slugify

class Tag(models.Model):
    """Tags do sistema criadas pelo admin"""
    nome = models.CharField(max_length=30, unique=True)
    cor = models.CharField(max_length=20, blank=True)
    slug = models.SlugField(unique=True, blank=True)
    ordem = models.PositiveIntegerField(default=0)
    is_sistema = models.BooleanField(default=False, help_text='Tag obrigatória do sistema (ex: Dúvida, Discussão)')

    class Meta:
        ordering = ['ordem', 'nome']
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

class TagEspecifica(models.Model):
    """Tags específicas criadas pelo usuário para cada postagem"""
    postagem = models.ForeignKey('Postagem', related_name='tags_especificas', on_delete=models.CASCADE)
    nome = models.CharField(max_length=30)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nome']
        unique_together = ['postagem', 'nome']

    def __str__(self):
        return self.nome

class Reacao(models.Model):
    """Reações disponíveis criadas pelo admin"""
    nome = models.CharField(max_length=30, unique=True)
    icone = models.ImageField(upload_to='reacoes/')
    ordem = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ['ordem']
        verbose_name = 'Reação'
        verbose_name_plural = 'Reações'

    def __str__(self):
        return self.nome

class ReacaoPostagem(models.Model):
    """Registro de reações dos usuários nas postagens"""
    postagem = models.ForeignKey('Postagem', related_name='reacoes', on_delete=models.CASCADE)
    reacao = models.ForeignKey(Reacao, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['postagem', 'usuario']

    def __str__(self):
        return f'{self.usuario} reagiu com {self.reacao} em {self.postagem}'

class Postagem(models.Model):
    TIPO_CHOICES = (
        ('THREAD', 'Thread/Tópico'),
        ('POST', 'Post Normal')
    )

    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='POST')
    assunto = models.ForeignKey(Assunto, related_name='postagens', on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField(default='')
    slug = models.SlugField(unique=True, blank=True)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tag_sistema = models.ForeignKey(
        Tag, 
        on_delete=models.PROTECT, 
        limit_choices_to={'is_sistema': True},
        null=True,  # Add this temporarily
        blank=True  # Add this temporarily
    )
    fixo = models.BooleanField(default=False)
    fechado = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    visualizacoes = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-fixo', '-criado_em']
        verbose_name = 'Postagem'
        verbose_name_plural = 'Postagens'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def get_reacoes_count(self):
        """Retorna contagem de reações agrupadas por tipo"""
        return self.reacoes.values('reacao__nome').annotate(total=models.Count('id'))

    def get_user_reaction(self, user):
        """Retorna a reação do usuário atual, se existir"""
        return self.reacoes.filter(usuario=user).first()

    def __str__(self):
        return f'[{self.get_tipo_display()}] {self.titulo}'

class Reply(models.Model):
    postagem = models.ForeignKey(Postagem, related_name='replies', on_delete=models.CASCADE)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    conteudo = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Reply'
        verbose_name_plural = 'Replies'
        ordering = ['criado_em']

    def __str__(self):
        return f'Reply de {self.autor} em {self.postagem}'