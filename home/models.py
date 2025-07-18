# Create your models here.
from django.db import models
from django.utils.text import slugify

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordem', 'nome']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

class Assunto(models.Model):
    categoria = models.ForeignKey(Categoria, related_name='assuntos', on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    descricao = models.TextField(blank=True)
    imagem = models.ImageField(upload_to='assuntos/', blank=True, null=True)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordem', 'titulo']

    def total_threads(self):
        return self.postagens.filter(tipo='THREAD').count()

    def total_posts(self):
        return self.postagens.filter(tipo='POST').count()

    def latest_post(self):
        return self.postagens.order_by('-criado_em').first()
    
    def total_respostas(self):
        from posts.models import Reply
        return Reply.objects.filter(postagem__assunto=self).count()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo    