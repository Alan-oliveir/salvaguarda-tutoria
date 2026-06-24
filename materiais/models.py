from django.conf import settings
from django.db import models


class Material(models.Model):
    TIPO_CHOICES = [
        ('ARQUIVO', 'Arquivo (PDF, Imagem, Documento)'),
        ('LINK', 'Link Externo'),
    ]

    # O "dono" do repositório onde o material vai ficar
    tutorado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='materiais_recebidos',
        limit_choices_to={'tipo': 'TUTORADO'},
        help_text="Estudante ao qual este material pertence"
    )

    # Quem fez o upload (pode ser o tutor ou o próprio tutorado)
    enviado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='materiais_enviados'
    )

    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, help_text="Opcional. Breve resumo do conteúdo.")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='LINK')

    # Preenchido APENAS se tipo == 'ARQUIVO' (Salva organizado por Ano/Mês)
    arquivo = models.FileField(upload_to='materiais/%Y/%m/', blank=True, null=True)

    # Preenchido APENAS se tipo == 'LINK'
    url = models.URLField(blank=True, null=True)

    data_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Material'
        verbose_name_plural = 'Materiais'
        ordering = ['-data_envio']

    def __str__(self):
        return f"{self.titulo} - {self.tutorado.first_name}"
