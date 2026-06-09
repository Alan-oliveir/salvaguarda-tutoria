# tutorias/models.py

import secrets
from django.db import models
from django.conf import settings


def _gerar_token_unico():
    while True:
        token = secrets.token_urlsafe(8)
        if not Tutorado.objects.filter(token=token).exists():
            return token


class Tutorado(models.Model):
    SERIE_CHOICES = [
        ('1EM', '1º Ano do Ensino Médio'),
        ('2EM', '2º Ano do Ensino Médio'),
        ('3EM', '3º Ano do Ensino Médio'),
        ('FORM', 'Já formado / Cursinho'),
    ]

    tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tutorados'
    )
    nome = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='fotos_tutorados/', blank=True, null=True)
    estado = models.CharField(max_length=50, blank=True)
    cidade = models.CharField(max_length=50, blank=True)
    serie = models.CharField(max_length=4, choices=SERIE_CHOICES, default='3EM')
    idade = models.PositiveIntegerField(null=True, blank=True)
    fez_enem = models.BooleanField(default=False)
    cursos_interesse = models.TextField(blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    token = models.CharField(max_length=16, blank=True, unique=True)
    criado_em = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = _gerar_token_unico()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Tutorado'
        verbose_name_plural = 'Tutorados'
        ordering = ['nome']


class Reuniao(models.Model):
    MATERIA_CHOICES = [
        ('MAT', 'Matemática'),
        ('POR', 'Português / Redação'),
        ('CIE', 'Ciências da Natureza'),
        ('HUM', 'Ciências Humanas'),
        ('LIN', 'Linguagens'),
        ('GER', 'Geral / Orientação'),
    ]

    tutorado = models.ForeignKey(
        Tutorado,
        on_delete=models.CASCADE,
        related_name='reunioes'
    )
    data = models.DateField()
    horario = models.TimeField()
    link = models.URLField(blank=True, help_text='Link do Google Meet, Zoom, etc.')
    topicos = models.TextField(blank=True)
    duracao_minutos = models.PositiveIntegerField(default=60)
    observacoes = models.TextField(blank=True)
    presenca = models.BooleanField(default=False)
    materia = models.CharField(max_length=3, choices=MATERIA_CHOICES, default='GER')

    def __str__(self):
        return f'Reunião com {self.tutorado.nome} em {self.data}'

    class Meta:
        verbose_name = 'Reunião'
        verbose_name_plural = 'Reuniões'
        ordering = ['-data', '-horario']