from datetime import date

from django.conf import settings
from django.db import models


class Tarefa(models.Model):
    CATEGORIA_CHOICES = [
        ('LISTA', 'Lista Mensal / Cronograma'),
        ('REDACAO', 'Redação'),
        ('SIMULADO', 'Simulado (TRIEduc)'),
        ('PLANEJAMENTO', 'Planejamento e Estratégia'),
        ('GENERICA', 'Tarefa Personalizada'),
    ]

    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('CONCLUIDA', 'Concluída'),
    ]

    tutorado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tarefas_recebidas',
        limit_choices_to={'tipo': 'TUTORADO'}
    )

    tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tarefas_criadas',
        limit_choices_to={'tipo': 'TUTOR'}
    )

    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, help_text="Instruções ou detalhes da tarefa.")
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='GENERICA')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDENTE')

    data_limite = models.DateField(blank=True, null=True, help_text="Opcional. Prazo final para conclusão.")

    link_externo = models.URLField(blank=True, null=True,
                                   help_text="Opcional. Link para o site do Salvaguarda ou material extra.")

    data_criacao = models.DateTimeField(auto_now_add=True)
    data_conclusao = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Tarefa'
        verbose_name_plural = 'Tarefas'
        ordering = ['status', 'data_limite', '-data_criacao']  # Pendentes primeiro, ordenado pelo prazo mais próximo

    def __str__(self):
        return f"{self.titulo} - {self.tutorado.first_name}"

    @property
    def esta_atrasada(self):
        """Retorna True se a tarefa estiver pendente e o prazo já tiver passado."""
        if self.status == 'PENDENTE' and self.data_limite:
            return date.today() > self.data_limite
        return False
