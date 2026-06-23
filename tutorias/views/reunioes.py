from datetime import date, datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404

from tutorias.decorators import tutor_required, tutorado_required
from tutorias.models import Reuniao, DisponibilidadeRecorrente
from usuarios.models import PerfilTutorado


@tutorado_required
def solicitar_reuniao(request):
    if request.method != 'POST':
        return redirect('tutorias:calendario')

    try:
        perfil = request.user.perfil_tutorado
    except Exception:
        return redirect('usuarios:painel_inicial')

    tutor = perfil.tutor
    if not tutor:
        messages.error(request, 'Você não tem tutor vinculado.')
        return redirect('usuarios:painel_inicial')

    data_str = request.POST.get('data', '')
    horario_str = request.POST.get('horario', '')
    materia = request.POST.get('materia', 'GER')
    topicos = request.POST.get('topicos', '').strip()
    observacoes = request.POST.get('observacoes', '').strip()
    duracao = int(request.POST.get('duracao_minutos', 60) or 60)

    try:
        data = datetime.strptime(data_str, '%Y-%m-%d').date()
        horario = datetime.strptime(horario_str, '%H:%M').time()
    except ValueError:
        messages.error(request, 'Data ou horário inválidos.')
        return redirect('tutorias:calendario')

    dia_semana = data.weekday()
    hora_fim_reuniao = (datetime.combine(data, horario) + timedelta(minutes=duracao)).time()

    disponivel = DisponibilidadeRecorrente.objects.filter(
        tutor=tutor,
        dia_semana=dia_semana,
        hora_inicio__lte=horario,
        hora_fim__gte=hora_fim_reuniao,
        ativo=True,
    ).exists()

    if not disponivel:
        messages.error(request, 'O horário escolhido está fora da disponibilidade do tutor.')
        return redirect('tutorias:calendario')

    conflito = Reuniao.objects.filter(
        tutor=tutor,
        data=data,
        horario__gte=horario,
        horario__lt=hora_fim_reuniao,
    ).exclude(status='CANCELADA').exists()

    if conflito:
        messages.error(request, 'Já existe uma reunião neste horário. Escolha outro.')
        return redirect('tutorias:calendario')

    Reuniao.objects.create(
        tutor=tutor,
        tutorado=request.user,
        data=data,
        horario=horario,
        materia=materia,
        topicos=topicos,
        observacoes=observacoes,
        duracao_minutos=duracao,
        status='CONFIRMADA',
        agendado_por='TUTORADO',
    )

    messages.success(request, 'Reunião agendada com sucesso!')
    return redirect('tutorias:minhas_reunioes')


@tutorado_required
def minhas_reunioes(request):
    reunioes = Reuniao.objects.filter(
        tutorado=request.user
    ).select_related('tutor').order_by('-data', '-horario')

    return render(request, 'minhas_reunioes.html', {
        'reunioes': reunioes,
        'hoje': date.today(),
        'materias_choices': Reuniao.MATERIA_CHOICES,
    })


@tutor_required
def lista_reunioes(request):
    reunioes = Reuniao.objects.filter(
        tutor=request.user
    ).select_related('tutorado').order_by('-data', '-horario')

    filtro_tutorado = request.GET.get('tutorado', '')
    filtro_materia = request.GET.get('materia', '')
    filtro_status = request.GET.get('status', '')

    if filtro_tutorado:
        reunioes = reunioes.filter(tutorado_id=filtro_tutorado)
    if filtro_materia:
        reunioes = reunioes.filter(materia=filtro_materia)
    if filtro_status:
        reunioes = reunioes.filter(status=filtro_status)

    tutorados_vinculados = PerfilTutorado.objects.filter(
        tutor=request.user
    ).select_related('usuario')

    if request.method == 'POST':
        return _criar_reuniao_manual(request)

    return render(request, 'lista_reunioes.html', {
        'reunioes': reunioes,
        'tutorados': tutorados_vinculados,
        'materias_choices': Reuniao.MATERIA_CHOICES,
        'status_choices': Reuniao.STATUS_CHOICES,
        'filtro_tutorado': filtro_tutorado,
        'filtro_materia': filtro_materia,
        'filtro_status': filtro_status,
        'hoje': date.today(),
    })


def _criar_reuniao_manual(request):
    tutorado_id = request.POST.get('tutorado')
    data_str = request.POST.get('data', '')
    horario_str = request.POST.get('horario', '')

    perfil = get_object_or_404(PerfilTutorado, usuario_id=tutorado_id, tutor=request.user)

    try:
        data = datetime.strptime(data_str, '%Y-%m-%d').date()
        horario = datetime.strptime(horario_str, '%H:%M').time()
    except ValueError:
        messages.error(request, 'Data ou horário inválidos.')
        return redirect('tutorias:lista_reunioes')

    Reuniao.objects.create(
        tutor=request.user,
        tutorado=perfil.usuario,
        data=data,
        horario=horario,
        materia=request.POST.get('materia', 'GER'),
        link=request.POST.get('link', '').strip(),
        topicos=request.POST.get('topicos', '').strip(),
        duracao_minutos=int(request.POST.get('duracao_minutos', 60) or 60),
        observacoes=request.POST.get('observacoes', '').strip(),
        presenca=bool(request.POST.get('presenca')),
        status='CONFIRMADA',
        agendado_por='TUTOR',
    )
    messages.success(request, 'Reunião registrada com sucesso!')
    return redirect('tutorias:lista_reunioes')


@login_required
def detalhe_reuniao(request, pk):
    reuniao = get_object_or_404(
        Reuniao.objects.select_related('tutorado', 'tutor'), pk=pk
    )
    is_tutor = request.user.tipo == 'TUTOR' and reuniao.tutor == request.user
    is_tutorado = request.user.tipo == 'TUTORADO' and reuniao.tutorado == request.user
    if not (is_tutor or is_tutorado or request.user.tipo == 'ADMIN'):
        raise Http404()

    return render(request, 'detalhe_reuniao.html', {
        'reuniao': reuniao,
        'materias_choices': Reuniao.MATERIA_CHOICES,
        'is_tutor': is_tutor,
        'is_tutorado': is_tutorado,
        'hoje': date.today(),
    })


@tutor_required
def editar_reuniao(request, pk):
    reuniao = get_object_or_404(Reuniao, pk=pk, tutor=request.user)

    if request.method == 'GET':
        tutorados_vinculados = PerfilTutorado.objects.filter(
            tutor=request.user
        ).select_related('usuario')
        return render(request, 'editar_reuniao.html', {
            'reuniao': reuniao,
            'tutorados': tutorados_vinculados,
            'materias_choices': Reuniao.MATERIA_CHOICES,
        })

    try:
        reuniao.data = datetime.strptime(request.POST.get('data', ''), '%Y-%m-%d').date()
        reuniao.horario = datetime.strptime(request.POST.get('horario', ''), '%H:%M').time()
    except ValueError:
        messages.error(request, 'Data ou horário inválidos.')
        return redirect('tutorias:editar_reuniao', pk=pk)

    reuniao.materia = request.POST.get('materia', reuniao.materia)
    reuniao.link = request.POST.get('link', '').strip()
    reuniao.topicos = request.POST.get('topicos', '').strip()
    reuniao.duracao_minutos = int(request.POST.get('duracao_minutos', 60) or 60)
    reuniao.observacoes = request.POST.get('observacoes', '').strip()
    reuniao.presenca = bool(request.POST.get('presenca'))
    reuniao.save()

    messages.success(request, 'Reunião atualizada com sucesso!')
    return redirect('tutorias:detalhe_reuniao', pk=pk)


@login_required
def cancelar_reuniao(request, pk):
    reuniao = get_object_or_404(Reuniao, pk=pk)
    is_tutor = request.user.tipo == 'TUTOR' and reuniao.tutor == request.user
    is_tutorado = request.user.tipo == 'TUTORADO' and reuniao.tutorado == request.user

    if not (is_tutor or is_tutorado):
        raise Http404()

    if not reuniao.pode_cancelar:
        messages.error(request, 'Esta reunião não pode ser cancelada.')
    elif request.method == 'POST':
        reuniao.status = 'CANCELADA'
        reuniao.save(update_fields=['status'])
        messages.success(request, 'Reunião cancelada.')

    return redirect('tutorias:minhas_reunioes' if is_tutorado else 'tutorias:lista_reunioes')


@login_required
def realizar_reuniao(request, pk):
    reuniao = get_object_or_404(Reuniao, pk=pk)
    is_tutor = request.user.tipo == 'TUTOR' and reuniao.tutor == request.user
    is_tutorado = request.user.tipo == 'TUTORADO' and reuniao.tutorado == request.user

    if not (is_tutor or is_tutorado):
        raise Http404()

    if not reuniao.pode_realizar:
        messages.error(request, 'Esta reunião ainda não pode ser marcada como realizada.')
    elif request.method == 'POST':
        reuniao.status = 'REALIZADA'
        reuniao.presenca = bool(request.POST.get('presenca', True))
        reuniao.save(update_fields=['status', 'presenca'])
        messages.success(request, 'Reunião marcada como realizada!')

    return redirect('tutorias:minhas_reunioes' if is_tutorado else 'tutorias:lista_reunioes')
