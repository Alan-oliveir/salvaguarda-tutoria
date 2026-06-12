# usuarios/models.py

import secrets

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    TIPO_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('TUTOR', 'Tutor'),
        ('TUTORADO', 'Tutorado'),
    ]

    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    telefone = models.CharField(max_length=15, blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)
    foto_perfil = models.ImageField(upload_to='perfis/', blank=True, null=True)
    endereco = models.TextField(blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    data_ultimo_acesso = models.DateTimeField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    observacoes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def get_nome_completo(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def get_iniciais(self):
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        return self.username[0].upper() if self.username else 'U'

    def is_admin(self):
        return self.tipo == 'ADMIN'

    def is_tutor(self):
        return self.tipo == 'TUTOR'

    def is_tutorado(self):
        return self.tipo == 'TUTORADO'

    def get_tipo_display_icon(self):
        return {'ADMIN': '👨‍💼', 'TUTOR': '👨‍🏫', 'TUTORADO': '👨‍🎓'}.get(self.tipo, '👤')

    def atualizar_ultimo_acesso(self):
        self.data_ultimo_acesso = timezone.now()
        self.save(update_fields=['data_ultimo_acesso'])

    def get_idade(self):
        if self.data_nascimento:
            today = timezone.now().date()
            return today.year - self.data_nascimento.year - (
                    (today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day)
            )
        return None

    def save(self, *args, **kwargs):
        if self.email:
            existing = CustomUser.objects.filter(email=self.email).exclude(pk=self.pk)
            if existing.exists():
                raise ValueError('Este email já está em uso por outro usuário.')
        if not self.pk:
            self.data_ultimo_acesso = timezone.now()
        super().save(*args, **kwargs)


class PerfilTutor(models.Model):
    usuario = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='perfil_tutor'
    )
    especialidade = models.CharField(max_length=100, blank=True, null=True)
    experiencia = models.TextField(blank=True, null=True)
    disponibilidade = models.TextField(blank=True, null=True)
    max_tutorados = models.PositiveIntegerField(default=10)

    class Meta:
        verbose_name = 'Perfil do Tutor'
        verbose_name_plural = 'Perfis dos Tutores'

    def __str__(self):
        return f'Perfil de {self.usuario.get_nome_completo()}'

    def tutorados_ativos(self):
        """Retorna os PerfilTutorado vinculados a este tutor."""
        return PerfilTutorado.objects.filter(tutor=self.usuario)


def _gerar_token_unico():
    while True:
        token = secrets.token_urlsafe(8)
        if not PerfilTutorado.objects.filter(token=token).exists():
            return token


class PerfilTutorado(models.Model):
    SERIE_CHOICES = [
        ('1EM', '1º Ano do Ensino Médio'),
        ('2EM', '2º Ano do Ensino Médio'),
        ('3EM', '3º Ano do Ensino Médio'),
        ('FORM', 'Já formado / Cursinho'),
    ]

    TURNO_CHOICES = [
        ('MATUTINO', 'Matutino'),
        ('VESPERTINO', 'Vespertino'),
        ('NOTURNO', 'Noturno'),
        ('INTEGRAL', 'Integral'),
    ]

    usuario = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='perfil_tutorado'
    )

    # Vínculo com tutor (null = ainda sem tutor atribuído)
    tutor = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tutorados',
        limit_choices_to={'tipo': 'TUTOR'},
    )

    # Dados acadêmicos (antes viviam no model Tutorado)
    serie = models.CharField(max_length=4, choices=SERIE_CHOICES, default='3EM')
    fez_enem = models.BooleanField(default=False)
    cursos_interesse = models.TextField(blank=True)
    escola = models.CharField(max_length=200, blank=True, null=True)
    turno_escolar = models.CharField(max_length=20, choices=TURNO_CHOICES, blank=True, null=True)

    # Dados de contato do aluno (complementam o CustomUser)
    whatsapp = models.CharField(max_length=20, blank=True)

    # Responsável
    responsavel_nome = models.CharField(max_length=200, blank=True, null=True)
    responsavel_telefone = models.CharField(max_length=15, blank=True, null=True)

    # Objetivos
    objetivo_principal = models.TextField(blank=True, null=True)

    # Token de acesso (para link direto futuro)
    token = models.CharField(max_length=16, blank=True, unique=True)

    class Meta:
        verbose_name = 'Perfil do Tutorado'
        verbose_name_plural = 'Perfis dos Tutorados'

    def __str__(self):
        return f'Perfil de {self.usuario.get_nome_completo()}'

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = _gerar_token_unico()
        super().save(*args, **kwargs)
