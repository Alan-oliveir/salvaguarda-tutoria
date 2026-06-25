from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Tarefa

@receiver(post_save, sender=Tarefa)
def notificar_nova_tarefa(sender, instance, created, **kwargs):
    # O 'created' garante que o e-mail só será enviado quando a tarefa nascer (e não quando for editada/concluída)
    if created and instance.tutorado.email:
        assunto = f"Salvaguarda: Nova tarefa de {instance.tutor.first_name} para você!"
        mensagem = f"""Olá {instance.tutorado.first_name}!

O seu tutor(a) {instance.tutor.get_nome_completo()} acabou de adicionar uma nova tarefa para você no painel:

📌 Título: {instance.titulo}
📚 Categoria: {instance.get_categoria_display()}
📅 Prazo: {instance.data_limite.strftime('%d/%m/%Y') if instance.data_limite else 'Sem prazo fixo'}

Acesse a plataforma do Salvaguarda para conferir os detalhes e marcar como concluída!

Um abraço,
Equipe Salvaguarda"""

        try:
            send_mail(
                subject=assunto,
                message=mensagem,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[instance.tutorado.email],
                fail_silently=True # Impede que o sistema quebre se o e-mail não enviar
            )
        except Exception as e:
            pass # Ignora erros de envio silenciosamente