# usuarios/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    TIPO_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('TUTOR', 'Tutor'),
        ('TUTORADO', 'Tutorado'),
    ]

    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        help_text="Tipo de usuário no sistema"
    )

    # Campos adicionais
    telefone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="Número de telefone para contato"
    )

    data_nascimento = models.DateField(
        blank=True,
        null=True,
        help_text="Data de nascimento do usuário"
    )

    foto_perfil = models.ImageField(
        upload_to='perfis/',
        blank=True,
        null=True,
        help_text="Foto de perfil do usuário"
    )

    endereco = models.TextField(
        blank=True,
        null=True,
        help_text="Endereço completo do usuário"
    )

    cidade = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Cidade onde reside"
    )

    estado = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        help_text="Estado (sigla) onde reside"
    )

    # Campos específicos para tutorados
    serie_escolar = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Série escolar atual (apenas para tutorados)"
    )

    ja_fez_enem = models.BooleanField(
        default=False,
        help_text="Indica se já fez o ENEM (apenas para tutorados)"
    )

    cursos_interesse = models.TextField(
        blank=True,
        null=True,
        help_text="Cursos de interesse (apenas para tutorados)"
    )

    # Campos de controle
    data_ultimo_acesso = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Data e hora do último acesso"
    )

    ativo = models.BooleanField(
        default=True,
        help_text="Indica se o usuário está ativo no sistema"
    )

    observacoes = models.TextField(
        blank=True,
        null=True,
        help_text="Observações gerais sobre o usuário"
    )

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ['first_name', 'last_name']

    def __str__(self):
        nome_completo = f"{self.first_name} {self.last_name}".strip()
        return nome_completo or self.username

    def get_nome_completo(self):
        """Retorna o nome completo do usuário"""
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def get_iniciais(self):
        """Retorna as iniciais do nome do usuário"""
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        return self.username[0].upper() if self.username else "U"

    def is_admin(self):
        """Verifica se o usuário é administrador"""
        return self.tipo == 'ADMIN'

    def is_tutor(self):
        """Verifica se o usuário é tutor"""
        return self.tipo == 'TUTOR'

    def is_tutorado(self):
        """Verifica se o usuário é tutorado"""
        return self.tipo == 'TUTORADO'

    def get_tipo_display_icon(self):
        """Retorna um ícone para o tipo de usuário"""
        icons = {
            'ADMIN': '👨‍💼',
            'TUTOR': '👨‍🏫',
            'TUTORADO': '👨‍🎓'
        }
        return icons.get(self.tipo, '👤')

    def atualizar_ultimo_acesso(self):
        """Atualiza a data do último acesso"""
        self.data_ultimo_acesso = timezone.now()
        self.save(update_fields=['data_ultimo_acesso'])

    def get_idade(self):
        """Calcula e retorna a idade do usuário"""
        if self.data_nascimento:
            today = timezone.now().date()
            return today.year - self.data_nascimento.year - (
                    (today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day)
            )
        return None

    def save(self, *args, **kwargs):
        """Override do save para fazer validações adicionais"""
        # Garantir que email seja único se fornecido
        if self.email:
            existing = CustomUser.objects.filter(email=self.email).exclude(pk=self.pk)
            if existing.exists():
                raise ValueError("Este email já está em uso por outro usuário.")

        # Primeira vez salvando - definir data de último acesso
        if not self.pk:
            self.data_ultimo_acesso = timezone.now()

        super().save(*args, **kwargs)


class PerfilTutor(models.Model):
    """Modelo para dados específicos de tutores"""
    usuario = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='perfil_tutor'
    )

    especialidade = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Área de especialidade do tutor"
    )

    experiencia = models.TextField(
        blank=True,
        null=True,
        help_text="Experiência profissional ou acadêmica"
    )

    disponibilidade = models.TextField(
        blank=True,
        null=True,
        help_text="Horários disponíveis para tutoria"
    )

    max_tutorados = models.PositiveIntegerField(
        default=10,
        help_text="Número máximo de tutorados que pode acompanhar"
    )

    class Meta:
        verbose_name = "Perfil do Tutor"
        verbose_name_plural = "Perfis dos Tutores"

    def __str__(self):
        return f"Perfil de {self.usuario.get_nome_completo()}"


class PerfilTutorado(models.Model):
    """Modelo para dados específicos de tutorados"""
    usuario = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='perfil_tutorado'
    )

    escola = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Nome da escola onde estuda"
    )

    turno_escolar = models.CharField(
        max_length=20,
        choices=[
            ('MATUTINO', 'Matutino'),
            ('VESPERTINO', 'Vespertino'),
            ('NOTURNO', 'Noturno'),
            ('INTEGRAL', 'Integral'),
        ],
        blank=True,
        null=True,
        help_text="Turno que estuda"
    )

    responsavel_nome = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Nome do responsável"
    )

    responsavel_telefone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="Telefone do responsável"
    )

    objetivo_principal = models.TextField(
        blank=True,
        null=True,
        help_text="Principal objetivo com a tutoria"
    )

    class Meta:
        verbose_name = "Perfil do Tutorado"
        verbose_name_plural = "Perfis dos Tutorados"

    def __str__(self):
        return f"Perfil de {self.usuario.get_nome_completo()}"