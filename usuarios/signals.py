# usuarios/signals.py

from django.db.models.signals import post_save, user_logged_in
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from .models import CustomUser, PerfilTutor, PerfilTutorado


@receiver(post_save, sender=CustomUser)
def criar_perfil_especifico(sender, instance, created, **kwargs):
    """
    Cria perfil específico automaticamente quando um usuário é criado
    """
    if created:
        if instance.tipo == 'TUTOR':
            PerfilTutor.objects.get_or_create(usuario=instance)
        elif instance.tipo == 'TUTORADO':
            PerfilTutorado.objects.get_or_create(usuario=instance)


@receiver(post_save, sender=CustomUser)
def salvar_perfil_especifico(sender, instance, **kwargs):
    """
    Salva o perfil específico quando o usuário é salvo
    """
    if hasattr(instance, 'perfil_tutor'):
        instance.perfil_tutor.save()
    elif hasattr(instance, 'perfil_tutorado'):
        instance.perfil_tutorado.save()


@receiver(user_logged_in)
def atualizar_ultimo_acesso(sender, request, user, **kwargs):
    """
    Atualiza a data do último acesso quando o usuário faz login
    """
    if isinstance(user, CustomUser):
        user.atualizar_ultimo_acesso()