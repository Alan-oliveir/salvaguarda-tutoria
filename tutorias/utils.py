from datetime import datetime, timedelta

from .models import Reuniao, DisponibilidadeRecorrente


def validar_horario_reuniao(tutor, data, horario, duracao_minutos, validar_disponibilidade=True,
                            reuniao_ignorada_id=None):
    """
    Verifica se um horário é válido para agendamento.
    Retorna uma tupla: (True, None) se válido, ou (False, 'Mensagem de erro') se inválido.
    """
    # 1. Evitar agendamentos no passado
    agora = datetime.now()
    if data < agora.date() or (data == agora.date() and horario < agora.time()):
        return False, "Não é possível agendar uma reunião no passado."

    hora_fim_nova = (datetime.combine(data, horario) + timedelta(minutes=duracao_minutos)).time()

    # 2. Verificar conflito de horário (sobreposição)
    reunioes_do_dia = Reuniao.objects.filter(
        tutor=tutor, data=data
    ).exclude(status='CANCELADA')

    # Se for uma edição, ignoramos a própria reunião que está sendo editada
    if reuniao_ignorada_id:
        reunioes_do_dia = reunioes_do_dia.exclude(pk=reuniao_ignorada_id)

    for r in reunioes_do_dia:
        r_fim = r.hora_fim()
        # Lógica de interseção: Nova começa antes da existente terminar, E nova termina depois da existente começar
        if horario < r_fim and hora_fim_nova > r.horario:
            return False, "O tutor já possui outra reunião agendada neste mesmo horário."

    # 3. Verificar disponibilidade do tutor
    if validar_disponibilidade:
        dia_semana = data.weekday()
        disponivel = DisponibilidadeRecorrente.objects.filter(
            tutor=tutor,
            dia_semana=dia_semana,
            hora_inicio__lte=horario,
            hora_fim__gte=hora_fim_nova,
            ativo=True
        ).exists()

        if not disponivel:
            return False, "O horário escolhido está fora da disponibilidade do tutor."

    return True, None
