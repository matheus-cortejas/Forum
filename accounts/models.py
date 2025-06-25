from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver

class CargoMembro(models.Model):
    """Modelo para definir cargos e permissões de membros"""
    nome = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, blank=True)
    cor = models.CharField(max_length=20, default="#FFFFFF", help_text="Código de cor HEX para visualização do cargo")
    
    # Permissões específicas
    pode_moderar = models.BooleanField(default=False)
    pode_fixar_topicos = models.BooleanField(default=False)
    pode_fechar_topicos = models.BooleanField(default=False)
    pode_editar_outros_posts = models.BooleanField(default=False)
    pode_excluir_outros_posts = models.BooleanField(default=False)
    pode_banir_usuarios = models.BooleanField(default=False)
    
    # Ordem de hierarquia
    ordem = models.PositiveSmallIntegerField(default=0)
    
    class Meta:
        verbose_name = "Cargo de membro"
        verbose_name_plural = "Cargos de membros"
        ordering = ['ordem', 'nome']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.nome

class UserManager(BaseUserManager):
    """Define método de criação de usuários personalizados"""
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email deve ser fornecido')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)

class Usuario(AbstractUser):
    """Extensão do modelo de usuário padrão do Django com campos específicos para fórum"""
    # Informações básicas
    apelido = models.CharField(max_length=30, blank=True, help_text="Nome de exibição opcional")
    avatar = models.ImageField(upload_to='avatares/', null=True, blank=True)
    cargos = models.ManyToManyField(CargoMembro, blank=True, related_name='usuarios')
    
    # Dados de perfil
    data_nascimento = models.DateField(null=True, blank=True, verbose_name="Data de Nascimento")
    localizacao = models.CharField(max_length=100, blank=True, verbose_name="Localização")
    biografia = models.TextField(blank=True, verbose_name="Sobre mim")
    site = models.URLField(blank=True)
    
    # Estatísticas
    total_itens = models.PositiveIntegerField(default=0, help_text="Total de mensagens, tópicos e conteúdos")
    reputacao = models.IntegerField(default=0, help_text="Pontuação de reações recebidas")
    answers = models.PositiveIntegerField(default=0, help_text="Número de respostas marcadas como solução")
    # Removido: dias_ganhos
    
    # Timestamps
    cadastrado_em = models.DateTimeField(auto_now_add=True)
    ultimo_acesso = models.DateTimeField(null=True, blank=True)
      
    # Seguidores e estatísticas de perfil
    seguidores = models.ManyToManyField('self', symmetrical=False, related_name='seguindo', blank=True)
    
    objects = UserManager()
    
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
    
    def save(self, *args, **kwargs):
        if not self.apelido:
            self.apelido = self.username
        super().save(*args, **kwargs)
    
    def atualizar_ultimo_acesso(self):
        self.ultimo_acesso = timezone.now()
        self.save(update_fields=['ultimo_acesso'])
    
    def seguir(self, usuario):
        """Adiciona um usuário à lista de seguidos"""
        if not self.seguindo.filter(id=usuario.id).exists():
            self.seguindo.add(usuario)
    
    def deixar_de_seguir(self, usuario):
        """Remove um usuário da lista de seguidos"""
        self.seguindo.remove(usuario)
    
    def esta_seguindo(self, usuario):
        """Verifica se este usuário segue outro"""
        return self.seguindo.filter(id=usuario.id).exists()
    
    def get_total_seguidores(self):
        """Retorna o número de seguidores"""
        return self.seguidores.count()
    
    def get_total_seguindo(self):
        """Retorna o número de usuários seguidos"""
        return self.seguindo.count()
    
    def __str__(self):
        return self.username

class VisitaPerfil(models.Model):
    """Registra as visitas ao perfil de um usuário por outros usuários"""
    usuario_visitado = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='visitas_recebidas')
    visitante = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='visitas_realizadas')
    timestamp = models.DateTimeField(auto_now_add=True)
    data = models.DateField(auto_now_add=True)  # Campo de data separado para unique_together
    
    class Meta:
        verbose_name = "Visita de Perfil"
        verbose_name_plural = "Visitas de Perfil"
        ordering = ['-timestamp']
        # Agora usando o campo 'data' em vez de timestamp__date
        unique_together = [['usuario_visitado', 'visitante', 'data']]
    
    @staticmethod
    def registrar_visita(usuario_visitado, visitante):
        """Registra uma visita no perfil, apenas se for de outro usuário"""
        if usuario_visitado != visitante and visitante.is_authenticated:
            # Verificar se já existe visita hoje
            hoje = timezone.now().date()
            visita_hoje = VisitaPerfil.objects.filter(
                usuario_visitado=usuario_visitado,
                visitante=visitante,
                data=hoje
            ).first()
            
            # Se não existir, cria uma nova visita
            if not visita_hoje:
                VisitaPerfil.objects.create(
                    usuario_visitado=usuario_visitado,
                    visitante=visitante
                )

# Atualizar estatísticas quando um post é criado
@receiver(post_save, sender='posts.Postagem')
def atualizar_estatisticas_usuario(sender, instance, created, **kwargs):
    if created:
        usuario = instance.autor
        usuario.total_itens += 1
        usuario.save(update_fields=['total_itens'])
        
# Atualizar estatísticas quando uma resposta é criada
@receiver(post_save, sender='posts.Reply')
def atualizar_estatisticas_resposta(sender, instance, created, **kwargs):
    if created:
        usuario = instance.autor
        usuario.total_itens += 1
        usuario.save(update_fields=['total_itens'])