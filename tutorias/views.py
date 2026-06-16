# tutorias/views.py

from datetime import date, datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from usuarios.models import PerfilTutorado, CustomUser
from .models import Reuniao, DisponibilidadeRecorrente


# Decorators

def tutor_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.tipo not in ('TUTOR', 'ADMIN'):
            messages.error(request, 'Acesso restrito a tutores.')
            return redirect('usuarios:painel_inicial')
        return view_func(request, *args, **kwargs)
    return wrapper


def tutorado_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.tipo != 'TUTORADO':
            messages.error(request, 'Acesso restrito a tutorados.')
            return redirect('usuarios:painel_inicial')
        return view_func(request, *args, **kwargs)
    return wrapper


# Tutorados

@tutor_required
def lista_tutorados(request):
    tutorados = PerfilTutorado.objects.filter(
        tutor=request.user
    ).select_related('usuario').order_by('usuario__first_name')
    return render(request, 'lista_tutorados.html', {
        'tutorados': tutorados,
        'series_choices': PerfilTutorado.SERIE_CHOICES,
    })


@tutor_required
def vincular_tutorado(request):
    if request.method == 'POST':
        perfil = get_object_or_404(PerfilTutorado, pk=request.POST.get('perfil_pk'))
        if perfil.tutor is not None and perfil.tutor != request.user:
            messages.error(request, 'Este tutorado já está vinculado a outro tutor.')
            return redirect('tutorias:vincular_tutorado')
        perfil.tutor = request.user
        perfil.save(update_fields=['tutor'])
        messages.success(request, f'{perfil.usuario.get_nome_completo()} vinculado(a) com sucesso!')
        return redirect('tutorias:lista_tutorados')

    disponiveis = PerfilTutorado.objects.filter(
        tutor__isnull=True
    ).select_related('usuario').order_by('usuario__first_name')
    return render(request, 'vincular_tutorado.html', {'disponiveis': disponiveis})


@tutor_required
def desvincular_tutorado(request, pk):
    perfil = get_object_or_404(PerfilTutorado, pk=pk, tutor=request.user)
    if request.method == 'POST':
        nome = perfil.usuario.get_nome_completo()
        perfil.tutor = None
        perfil.save(update_fields=['tutor'])
        messages.success(request, f'{nome} desvinculado(a).')
    return redirect('tutorias:lista_tutorados')


@tutor_required
def detalhe_tutorado(request, pk):
    perfil = get_object_or_404(
        PerfilTutorado.objects.select_related('usuario'), pk=pk, tutor=request.user
    )
    reunioes = Reuniao.objects.filter(
        tutorado=perfil.usuario
    ).order_by('-data', '-horario')
    return render(request, 'detalhe_tutorado.html', {
        'tutorado': perfil,
        'usuario': perfil.usuario,
        'reunioes': reunioes,
        'materias_choices': Reuniao.MATERIA_CHOICES,
    })


@tutor_required
def editar_tutorado(request, pk):
    perfil = get_object_or_404(PerfilTutorado, pk=pk, tutor=request.user)
    if request.method == 'GET':
        return render(request, 'editar_tutorado.html', {
            'tutorado': perfil,
            'usuario': perfil.usuario,
            'series_choices': PerfilTutorado.SERIE_CHOICES,
            'turno_choices': PerfilTutorado.TURNO_CHOICES,
        })
    perfil.serie                = request.POST.get('serie', perfil.serie)
    perfil.fez_enem             = bool(request.POST.get('fez_enem'))
    perfil.cursos_interesse     = request.POST.get('cursos_interesse', '')
    perfil.escola               = request.POST.get('escola', '')
    perfil.turno_escolar        = request.POST.get('turno_escolar', '')
    perfil.whatsapp             = request.POST.get('whatsapp', '')
    perfil.responsavel_nome     = request.POST.get('responsavel_nome', '')
    perfil.responsavel_telefone = request.POST.get('responsavel_telefone', '')
    perfil.objetivo_principal   = request.POST.get('objetivo_principal', '')
    perfil.save()
    messages.success(request, 'Dados atualizados com sucesso!')
    return redirect('tutorias:detalhe_tutorado', pk=pk)


# Disponibilidade do tutor

@tutor_required
def disponibilidade(request):
    """Tutor gerencia seus blocos semanais de disponibilidade."""
    blocos = DisponibilidadeRecorrente.objects.filter(tutor=request.user)

    if request.method == 'POST':
        dia_semana  = request.POST.get('dia_semana')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fim    = request.POST.get('hora_fim')

        if not (dia_semana and hora_inicio and hora_fim):
            messages.error(request, 'Preencha todos os campos.')
            return redirect('tutorias:disponibilidade')

        if hora_inicio >= hora_fim:
            messages.error(request, 'O horário de início deve ser antes do horário de fim.')
            return redirect('tutorias:disponibilidade')

        _, criado = DisponibilidadeRecorrente.objects.get_or_create(
            tutor=request.user,
            dia_semana=int(dia_semana),
            hora_inicio=hora_inicio,
            defaults={'hora_fim': hora_fim},
        )
        if criado:
            messages.success(request, 'Disponibilidade adicionada!')
        else:
            messages.warning(request, 'Já existe um bloco neste dia e horário de início.')
        return redirect('tutorias:disponibilidade')

    # Agrupar por dia da semana para exibição
    dias = {}
    for b in blocos:
        dias.setdefault(b.get_dia_semana_display(), []).append(b)

    return render(request, 'disponibilidade.html', {
        'blocos': blocos,
        'dias_agrupados': dias,
        'dias_choices': DisponibilidadeRecorrente.DIAS_SEMANA,
    })


@tutor_required
def deletar_disponibilidade(request, pk):
    bloco = get_object_or_404(DisponibilidadeRecorrente, pk=pk, tutor=request.user)
    if request.method == 'POST':
        bloco.delete()
        messages.success(request, 'Disponibilidade removida.')
    return redirect('tutorias:disponibilidade')


# Calendário do tutorado

@tutorado_required
def calendario(request):
    """Página do calendário para o tutorado agendar reuniões."""
    try:
        perfil = request.user.perfil_tutorado
    except Exception:
        messages.error(request, 'Perfil não encontrado.')
        return redirect('usuarios:painel_inicial')

    if not perfil.tutor:
        messages.warning(request, 'Você ainda não está vinculado a um tutor.')
        return redirect('usuarios:painel_inicial')

    return render(request, 'calendario.html', {
        'materias_choices': Reuniao.MATERIA_CHOICES,
        'tutor': perfil.tutor,
    })


@tutorado_required
def slots_json(request):
    """JSON para o FullCalendar: disponibilidades + reuniões agendadas."""
    try:
        perfil = request.user.perfil_tutorado
    except Exception:
        return JsonResponse([], safe=False)

    if not perfil.tutor:
        return JsonResponse([], safe=False)

    start_str = request.GET.get('start', '')
    end_str   = request.GET.get('end', '')

    try:
        start_date = datetime.fromisoformat(start_str[:10]).date()
        end_date   = datetime.fromisoformat(end_str[:10]).date()
    except (ValueError, TypeError):
        return JsonResponse([], safe=False)

    events = []

    # ── Blocos de disponibilidade do tutor (background) ──
    disponibilidades = DisponibilidadeRecorrente.objects.filter(
        tutor=perfil.tutor, ativo=True
    )

    current = start_date
    while current < end_date:
        dia_semana = current.weekday()
        for disp in disponibilidades:
            if disp.dia_semana == dia_semana:
                events.append({
                    'groupId': 'disponivel',
                    'title': 'Disponível',
                    'start': f'{current}T{disp.hora_inicio.strftime("%H:%M:%S")}',
                    'end':   f'{current}T{disp.hora_fim.strftime("%H:%M:%S")}',
                    'display': 'background',
                    'color': '#ede5f8',
                    'extendedProps': {'tipo': 'disponibilidade'},
                })
        current += timedelta(days=1)

    # ── Reuniões já agendadas do tutorado ──
    reunioes = Reuniao.objects.filter(
        tutorado=request.user,
        data__gte=start_date,
        data__lt=end_date,
    ).exclude(status='CANCELADA')

    STATUS_COLORS = {
        'CONFIRMADA': '#7b2fbe',
        'REALIZADA':  '#1a7a4a',
    }

    for r in reunioes:
        hora_fim = r.hora_fim()
        events.append({
            'id':    f'reuniao-{r.pk}',
            'title': r.get_materia_display(),
            'start': f'{r.data}T{r.horario.strftime("%H:%M:%S")}',
            'end':   f'{r.data}T{hora_fim.strftime("%H:%M:%S")}',
            'color': STATUS_COLORS.get(r.status, '#f5a623'),
            'extendedProps': {
                'tipo':   'reuniao',
                'status': r.status,
                'pk':     r.pk,
            },
        })

    return JsonResponse(events, safe=False)


@tutorado_required
def solicitar_reuniao(request):
    """Tutorado confirma agendamento de uma reunião."""
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

    data_str    = request.POST.get('data', '')
    horario_str = request.POST.get('horario', '')
    materia     = request.POST.get('materia', 'GER')
    topicos     = request.POST.get('topicos', '').strip()
    observacoes = request.POST.get('observacoes', '').strip()
    duracao     = int(request.POST.get('duracao_minutos', 60) or 60)

    try:
        data    = datetime.strptime(data_str, '%Y-%m-%d').date()
        horario = datetime.strptime(horario_str, '%H:%M').time()
    except ValueError:
        messages.error(request, 'Data ou horário inválidos.')
        return redirect('tutorias:calendario')

    # Validar que o horário está dentro de uma disponibilidade
    dia_semana      = data.weekday()
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

    # Validar que não há conflito com reunião existente
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
    """Lista de reuniões do tutorado."""
    reunioes = Reuniao.objects.filter(
        tutorado=request.user
    ).select_related('tutor').order_by('-data', '-horario')

    return render(request, 'minhas_reunioes.html', {
        'reunioes': reunioes,
        'hoje': date.today(),
        'materias_choices': Reuniao.MATERIA_CHOICES,
    })


# Reuniões — tutor

@tutor_required
def lista_reunioes(request):
    reunioes = Reuniao.objects.filter(
        tutor=request.user
    ).select_related('tutorado').order_by('-data', '-horario')

    filtro_tutorado = request.GET.get('tutorado', '')
    filtro_materia  = request.GET.get('materia', '')
    filtro_status   = request.GET.get('status', '')

    if filtro_tutorado:
        reunioes = reunioes.filter(tutorado_id=filtro_tutorado)
    if filtro_materia:
        reunioes = reunioes.filter(materia=filtro_materia)
    if filtro_status:
        reunioes = reunioes.filter(status=filtro_status)

    tutorados_vinculados = PerfilTutorado.objects.filter(
        tutor=request.user
    ).select_related('usuario')

    # POST = criação manual (tutor agenda diretamente)
    if request.method == 'POST':
        return _criar_reuniao_manual(request)

    return render(request, 'lista_reunioes.html', {
        'reunioes': reunioes,
        'tutorados': tutorados_vinculados,
        'materias_choices': Reuniao.MATERIA_CHOICES,
        'status_choices': Reuniao.STATUS_CHOICES,
        'filtro_tutorado': filtro_tutorado,
        'filtro_materia':  filtro_materia,
        'filtro_status':   filtro_status,
        'hoje': date.today(),
    })


def _criar_reuniao_manual(request):
    """Criação direta pelo tutor (sem passar pelo calendário do tutorado)."""
    tutorado_id = request.POST.get('tutorado')
    data_str    = request.POST.get('data', '')
    horario_str = request.POST.get('horario', '')

    perfil = get_object_or_404(PerfilTutorado, usuario_id=tutorado_id, tutor=request.user)

    try:
        data    = datetime.strptime(data_str, '%Y-%m-%d').date()
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
    # Tutor ou tutorado da reunião podem ver
    is_tutor    = request.user.tipo == 'TUTOR'    and reuniao.tutor == request.user
    is_tutorado = request.user.tipo == 'TUTORADO' and reuniao.tutorado == request.user
    if not (is_tutor or is_tutorado or request.user.tipo == 'ADMIN'):
        raise Http404()

    return render(request, 'detalhe_reuniao.html', {
        'reuniao':         reuniao,
        'materias_choices': Reuniao.MATERIA_CHOICES,
        'is_tutor':        is_tutor,
        'is_tutorado':     is_tutorado,
        'hoje':            date.today(),
    })


@tutor_required
def editar_reuniao(request, pk):
    reuniao = get_object_or_404(Reuniao, pk=pk, tutor=request.user)

    if request.method == 'GET':
        tutorados_vinculados = PerfilTutorado.objects.filter(
            tutor=request.user
        ).select_related('usuario')
        return render(request, 'editar_reuniao.html', {
            'reuniao':          reuniao,
            'tutorados':        tutorados_vinculados,
            'materias_choices': Reuniao.MATERIA_CHOICES,
        })

    try:
        reuniao.data    = datetime.strptime(request.POST.get('data', ''), '%Y-%m-%d').date()
        reuniao.horario = datetime.strptime(request.POST.get('horario', ''), '%H:%M').time()
    except ValueError:
        messages.error(request, 'Data ou horário inválidos.')
        return redirect('tutorias:editar_reuniao', pk=pk)

    reuniao.materia         = request.POST.get('materia', reuniao.materia)
    reuniao.link            = request.POST.get('link', '').strip()
    reuniao.topicos         = request.POST.get('topicos', '').strip()
    reuniao.duracao_minutos = int(request.POST.get('duracao_minutos', 60) or 60)
    reuniao.observacoes     = request.POST.get('observacoes', '').strip()
    reuniao.presenca        = bool(request.POST.get('presenca'))
    reuniao.save()

    messages.success(request, 'Reunião atualizada com sucesso!')
    return redirect('tutorias:detalhe_reuniao', pk=pk)


@login_required
def cancelar_reuniao(request, pk):
    """Cancela reunião — disponível para tutor e tutorado."""
    reuniao  = get_object_or_404(Reuniao, pk=pk)
    is_tutor    = request.user.tipo == 'TUTOR'    and reuniao.tutor == request.user
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
    """Marca reunião como realizada — disponível para tutor e tutorado."""
    reuniao  = get_object_or_404(Reuniao, pk=pk)
    is_tutor    = request.user.tipo == 'TUTOR'    and reuniao.tutor == request.user
    is_tutorado = request.user.tipo == 'TUTORADO' and reuniao.tutorado == request.user

    if not (is_tutor or is_tutorado):
        raise Http404()

    if not reuniao.pode_realizar:
        messages.error(request, 'Esta reunião ainda não pode ser marcada como realizada.')
    elif request.method == 'POST':
        reuniao.status  = 'REALIZADA'
        reuniao.presenca = bool(request.POST.get('presenca', True))
        reuniao.save(update_fields=['status', 'presenca'])
        messages.success(request, 'Reunião marcada como realizada!')

    return redirect('tutorias:minhas_reunioes' if is_tutorado else 'tutorias:lista_reunioes')
