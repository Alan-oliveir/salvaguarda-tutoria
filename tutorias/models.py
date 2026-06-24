from django.conf import settings
from django.db import models

from django.utils import timezone


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
        ('CANCELADA', 'Cancelada'),
        ('REALIZADA', 'Realizada'),
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

    data = models.DateField()
    horario = models.TimeField()
    duracao_minutos = models.PositiveIntegerField(default=60)
    materia = models.CharField(max_length=3, choices=MATERIA_CHOICES, default='GER')
    link = models.URLField(blank=True)
    topicos = models.TextField(blank=True)
    observacoes = models.TextField(blank=True)
    presenca = models.BooleanField(default=False)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='CONFIRMADA')

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


class FichaDiagnostica(models.Model):
    NIVEL_CHOICES = [
        ('EXCELENTE', 'Excelente'),
        ('BOM', 'Bom'),
        ('RAZOAVEL', 'Razoável'),
        ('BAIXO', 'Baixo'),
        ('NULO', 'Nulo'),
    ]

    tutorado = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ficha_diagnostica',
        limit_choices_to={'tipo': 'TUTORADO'}
    )

    tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='fichas_preenchidas',
        limit_choices_to={'tipo': 'TUTOR'}
    )

    data_preenchimento = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    # 1. DEMANDAS INFORMACIONAIS
    info_salvaguarda = models.CharField("Funcionamento do Salvaguarda", max_length=15, choices=NIVEL_CHOICES,
                                        default='NULO')
    info_publica_privada = models.CharField("Diferença entre universidade pública e privada", max_length=15,
                                            choices=NIVEL_CHOICES, default='NULO')
    info_vestibulares = models.CharField("O que é vestibular e opções disponíveis", max_length=15,
                                         choices=NIVEL_CHOICES, default='NULO')
    info_enem_programas = models.CharField("ENEM, SISU, PROUNI e FIES", max_length=15, choices=NIVEL_CHOICES,
                                           default='NULO')
    info_nota_corte = models.CharField("Conceito de nota de corte", max_length=15, choices=NIVEL_CHOICES,
                                       default='NULO')
    info_universidades_regiao = models.CharField("Universidades da região e cursos", max_length=15,
                                                 choices=NIVEL_CHOICES, default='NULO')
    info_assistencia = models.CharField("Programas de assistência estudantil", max_length=15, choices=NIVEL_CHOICES,
                                        default='NULO')
    info_bolsas_privadas = models.CharField("Mecanismo de bolsas em privadas", max_length=15, choices=NIVEL_CHOICES,
                                            default='NULO')

    # 2. DEMANDAS ORGANIZACIONAIS
    org_rotina = models.CharField("Segue rotina e cronograma", max_length=15, choices=NIVEL_CHOICES, default='NULO')
    org_estuda_sozinho = models.CharField("Estuda sozinho e concilia tarefas", max_length=15, choices=NIVEL_CHOICES,
                                          default='NULO')
    org_estudo_ativo = models.CharField("Estudo ativo (Exercícios e Simulados)", max_length=15, choices=NIVEL_CHOICES,
                                        default='NULO')
    org_estudo_eficiente = models.CharField("Estuda de forma eficiente", max_length=15, choices=NIVEL_CHOICES,
                                            default='NULO')

    # 3. PERCEPÇÕES GERAIS
    maiores_dificuldades = models.TextField(blank=True, null=True, help_text="Principais barreiras notadas na reunião.")
    pontos_positivos = models.TextField(blank=True, null=True, help_text="Qualidades e facilidades do estudante.")
    comentarios_extras = models.TextField("Demais comentários", blank=True, null=True,
                                          help_text="Demandas extras ou observações livres.")

    class Meta:
        verbose_name = 'Ficha Diagnóstica'
        verbose_name_plural = 'Fichas Diagnósticas'

    def __str__(self):
        return f"Ficha Diagnóstica - {self.tutorado.first_name}"


class AtividadeExtra(models.Model):
    tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='atividades_extras',
        limit_choices_to={'tipo': 'TUTOR'}
    )

    # Opcional, pois o tutor pode registrar "Leitura do manual" que não é para um aluno específico
    tutorado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='atividades_recebidas',
        limit_choices_to={'tipo': 'TUTORADO'}
    )

    data = models.DateField("Data da Atividade", default=timezone.now)
    descricao = models.CharField("Breve Descrição", max_length=255,
                                 help_text="Ex: Pesquisa de cursos na UFRJ, Leitura do Manual, etc.")
    duracao_minutos = models.PositiveIntegerField("Carga Horária (em minutos)", help_text="Ex: 90 para 1h30.")

    data_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Atividade Extra'
        verbose_name_plural = 'Atividades Extras'
        ordering = ['-data', '-data_registro']

    def __str__(self):
        return f"{self.descricao} - {self.tutor.first_name} ({self.duracao_minutos} min)"
