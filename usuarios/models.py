# usuarios/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    TIPO_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('TUTOR', 'Tutor'),
        ('TUTORADO', 'Tutorado'),
    ]

    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)

    def is_admin(self):
        return self.tipo == 'ADMIN'

    def is_tutor(self):
        return self.tipo == 'TUTOR'

    def is_tutorado(self):
        return self.tipo == 'TUTORADO'
