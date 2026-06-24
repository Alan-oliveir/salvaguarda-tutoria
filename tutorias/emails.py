from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def _enviar_notificacao_base(destinatario, assunto, contexto):
    """Função interna auxiliar para renderizar e enviar o e-mail em HTML e texto puro."""
    # Renderiza o HTML passando o contexto com as variáveis
    html_message = render_to_string('email_notificacao.html', contexto)

    # Cria uma versão em texto puro caso o cliente de e-mail do usuário não suporte HTML
    plain_message = strip_tags(html_message)

    send_mail(
        subject=assunto,
        message=plain_message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[destinatario.email],
        html_message=html_message,
        fail_silently=True  # Evita travar a aplicação caso o Gmail falhe momentaneamente
    )


def notificar_agendamento(reuniao):
    """Identifica quem criou o agendamento e envia a notificação para a outra parte."""
    url_painel = "http://127.0.0.1:8000/usuarios/painel/"  # Futuramente substituído pelo domínio real

    # Caso 1: O tutorado agendou pelo calendário -> Notifica o Tutor
    if reuniao.agendado_por == 'TUTORADO':
        destinatario = reuniao.tutor
        nome_destinatario = reuniao.tutor.first_name or "Tutor"
        mensagem = f"O tutorado {reuniao.tutorado.get_nome_completo()} acabou de agendar uma nova reunião com você pelo calendário da plataforma."
        assunto = f"[Salvaguarda] Novo agendamento: {reuniao.tutorado.first_name}"

    # Caso 2: O tutor registrou manualmente -> Notifica o Tutorado
    else:
        destinatario = reuniao.tutorado
        nome_destinatario = reuniao.tutorado.first_name or "Estudante"
        mensagem = f"Seu tutor, {reuniao.tutor.get_nome_completo()}, registrou uma nova reunião com você no sistema."
        assunto = f"[Salvaguarda] Reunião agendada: {reuniao.get_materia_display()}"

    contexto = {
        'nome_destinatario': nome_destinatario,
        'mensagem_principal': mensagem,
        'reuniao': reuniao,
        'assunto': assunto,
        'url_painel': url_painel,
        'eh_cancelamento': False
    }

    _enviar_notificacao_base(destinatario, assunto, contexto)


def notificar_cancelamento(reuniao, usuario_cancelou):
    """Notifica a parte afetada sobre o cancelamento da reunião."""
    # Se o tutor cancelou -> Notifica o tutorado
    if usuario_cancelou.tipo == 'TUTOR':
        destinatario = reuniao.tutorado
        nome_destinatario = reuniao.tutorado.first_name or "Estudante"
        mensagem = f"Informamos que o tutor {reuniao.tutor.get_nome_completo()} precisou cancelar a reunião semanal que estava agendada."
        assunto = "[Salvaguarda] Reunião Cancelada pelo Tutor"

    # Se o tutorado cancelou -> Notifica o tutor
    else:
        destinatario = reuniao.tutor
        nome_destinatario = reuniao.tutor.first_name or "Tutor"
        mensagem = f"Informamos que o estudante {reuniao.tutorado.get_nome_completo()} cancelou a reunião que estava agendada."
        assunto = f"[Salvaguarda] Reunião Cancelada pelo Aluno: {reuniao.tutorado.first_name}"

    contexto = {
        'nome_destinatario': nome_destinatario,
        'mensagem_principal': mensagem,
        'reuniao': reuniao,
        'assunto': assunto,
        'eh_cancelamento': True
    }

    _enviar_notificacao_base(destinatario, assunto, contexto)

def notificar_link_chamada(reuniao):
    """Notifica o tutorado que o link da videochamada foi adicionado ou reenviado."""
    destinatario = reuniao.tutorado
    nome_destinatario = reuniao.tutorado.first_name or "Estudante"

    mensagem = (
        f"Seu tutor, {reuniao.tutor.get_nome_completo()}, disponibilizou o "
        f"link da videochamada para a reunião de {reuniao.get_materia_display()}."
    )
    assunto = f"[Salvaguarda] Link da Chamada: {reuniao.data.strftime('%d/%m/%Y')}"

    contexto = {
        'nome_destinatario': nome_destinatario,
        'mensagem_principal': mensagem,
        'reuniao': reuniao,
        'assunto': assunto,
        'url_painel': f"http://127.0.0.1:8000/tutorias/reunioes/{reuniao.pk}/",
        'eh_cancelamento': False
    }

    _enviar_notificacao_base(destinatario, assunto, contexto)
