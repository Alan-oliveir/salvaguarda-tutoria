# tutorias/models.py

from django.conf import settings
from django.db import models


class Reuniao(models.Model):
    MATERIA_CHOICES = [
        ('MAT', 'Matemática'),
        ('POR', 'Português / Redação'),
        ('CIE', 'Ciências da Natureza'),
        ('HUM', 'Ciências Humanas'),
        ('LIN', 'Linguagens'),
        ('GER', 'Geral / Orientação'),
    ]

    # tutor que criou a reunião
    tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reunioes_como_tutor',
        limit_choices_to={'tipo': 'TUTOR'},
    )

    # tutorado é agora um CustomUser real
    tutorado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reunioes_como_tutorado',
        limit_choices_to={'tipo': 'TUTORADO'},
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
        return f'Reunião com {self.tutorado.get_nome_completo()} em {self.data}'

    class Meta:
        verbose_name = 'Reunião'
        verbose_name_plural = 'Reuniões'
        ordering = ['-data', '-horario']
