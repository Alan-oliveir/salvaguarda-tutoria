# tutorias/models.py

from django.db import models
from django.conf import settings

class Tutorado(models.Model):
    tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tutorados'
    )
    nome = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='fotos_tutorados/', blank=True, null=True)
    estado = models.CharField(max_length=50)
    cidade = models.CharField(max_length=50)
    serie = models.CharField(max_length=50)
    idade = models.PositiveIntegerField()
    fez_enem = models.BooleanField(default=False)
    cursos_interesse = models.TextField()
    whatsapp = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.nome


class Reuniao(models.Model):
    tutorado = models.ForeignKey(
        Tutorado,
        on_delete=models.CASCADE,
        related_name='reunioes'
    )
    data = models.DateField()
    horario = models.TimeField()
    link = models.URLField(help_text="Link do Google Meet, Zoom, etc.")
    topicos = models.TextField()
    duracao_minutos = models.PositiveIntegerField()
    observacoes = models.TextField(blank=True)
    presenca = models.BooleanField(default=False)

    def __str__(self):
        return f"Reunião com {self.tutorado.nome} em {self.data}"
