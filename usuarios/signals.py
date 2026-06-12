# usuarios/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in

from .models import CustomUser, PerfilTutor, PerfilTutorado


@receiver(post_save, sender=CustomUser)
def criar_perfil_especifico(sender, instance, created, **kwargs):
    if created:
        if instance.tipo == 'TUTOR':
            PerfilTutor.objects.get_or_create(usuario=instance)
        elif instance.tipo == 'TUTORADO':
            PerfilTutorado.objects.get_or_create(usuario=instance)


@receiver(user_logged_in)
def atualizar_ultimo_acesso(sender, request, user, **kwargs):
    if isinstance(user, CustomUser):
        user.atualizar_ultimo_acesso()