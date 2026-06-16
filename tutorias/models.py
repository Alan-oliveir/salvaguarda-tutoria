# tutorias/models.py

from django.conf import settings
from django.db import models


class DisponibilidadeRecorrente(models.Model):
    """Blocos semanais fixos em que o tutor está disponível."""

    DIAS_SEMANA = [
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]

    tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='disponibilidades',
        limit_choices_to={'tipo': 'TUTOR'},
    )
    dia_semana = models.IntegerField(choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Disponibilidade'
        verbose_name_plural = 'Disponibilidades'
        ordering = ['dia_semana', 'hora_inicio']
        # Impede blocos duplicados para o mesmo tutor/dia/horário
        unique_together = [('tutor', 'dia_semana', 'hora_inicio')]

    def __str__(self):
        return (
            f'{self.get_dia_semana_display()} '
            f'{self.hora_inicio.strftime("%H:%M")}–{self.hora_fim.strftime("%H:%M")} '
            f'({self.tutor})'
        )


class Reuniao(models.Model):
    MATERIA_CHOICES = [
        ('MAT', 'Matemática'),
        ('POR', 'Português / Redação'),
        ('CIE', 'Ciências da Natureza'),
        ('HUM', 'Ciências Humanas'),
        ('LIN', 'Linguagens'),
        ('GER', 'Geral / Orientação'),
    ]

    STATUS_CHOICES = [
        ('CONFIRMADA', 'Confirmada'),
        ('CANCELADA',  'Cancelada'),
        ('REALIZADA',  'Realizada'),
    ]

    tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reunioes_como_tutor',
        limit_choices_to={'tipo': 'TUTOR'},
    )
    tutorado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reunioes_como_tutorado',
        limit_choices_to={'tipo': 'TUTORADO'},
    )

    data            = models.DateField()
    horario         = models.TimeField()
    duracao_minutos = models.PositiveIntegerField(default=60)
    materia         = models.CharField(max_length=3, choices=MATERIA_CHOICES, default='GER')
    link            = models.URLField(blank=True)
    topicos         = models.TextField(blank=True)
    observacoes     = models.TextField(blank=True)
    presenca        = models.BooleanField(default=False)
    status          = models.CharField(max_length=12, choices=STATUS_CHOICES, default='CONFIRMADA')

    agendado_por = models.CharField(
        max_length=10,
        choices=[('TUTOR', 'Tutor'), ('TUTORADO', 'Tutorado')],
        default='TUTOR',
        help_text='Quem criou o agendamento',
    )

    class Meta:
        verbose_name = 'Reunião'
        verbose_name_plural = 'Reuniões'
        ordering = ['-data', '-horario']

    def __str__(self):
        return f'Reunião com {self.tutorado.get_nome_completo()} em {self.data}'

    def hora_fim(self):
        from datetime import datetime, timedelta
        dt = datetime.combine(self.data, self.horario)
        return (dt + timedelta(minutes=self.duracao_minutos)).time()

    @property
    def pode_cancelar(self):
        return self.status == 'CONFIRMADA'

    @property
    def pode_realizar(self):
        from datetime import date
        return self.status == 'CONFIRMADA' and self.data <= date.today()