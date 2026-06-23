from datetime import datetime, timedelta

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from tutorias.decorators import tutor_required, tutorado_required
from tutorias.models import DisponibilidadeRecorrente, Reuniao


@tutor_required
def disponibilidade(request):
    blocos = DisponibilidadeRecorrente.objects.filter(tutor=request.user)

    if request.method == 'POST':
        dia_semana = request.POST.get('dia_semana')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fim = request.POST.get('hora_fim')

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


@tutorado_required
def calendario(request):
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
    try:
        perfil = request.user.perfil_tutorado
    except Exception:
        return JsonResponse([], safe=False)

    if not perfil.tutor:
        return JsonResponse([], safe=False)

    start_str = request.GET.get('start', '')
    end_str = request.GET.get('end', '')

    try:
        start_date = datetime.fromisoformat(start_str[:10]).date()
        end_date = datetime.fromisoformat(end_str[:10]).date()
    except (ValueError, TypeError):
        return JsonResponse([], safe=False)

    events = []

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
                    'end': f'{current}T{disp.hora_fim.strftime("%H:%M:%S")}',
                    'display': 'background',
                    'color': '#ede5f8',
                    'extendedProps': {'tipo': 'disponibilidade'},
                })
        current += timedelta(days=1)

    reunioes = Reuniao.objects.filter(
        tutorado=request.user,
        data__gte=start_date,
        data__lt=end_date,
    ).exclude(status='CANCELADA')

    STATUS_COLORS = {
        'CONFIRMADA': '#7b2fbe',
        'REALIZADA': '#1a7a4a',
    }

    for r in reunioes:
        hora_fim = r.hora_fim()
        events.append({
            'id': f'reuniao-{r.pk}',
            'title': r.get_materia_display(),
            'start': f'{r.data}T{r.horario.strftime("%H:%M:%S")}',
            'end': f'{r.data}T{hora_fim.strftime("%H:%M:%S")}',
            'color': STATUS_COLORS.get(r.status, '#f5a623'),
            'extendedProps': {
                'tipo': 'reuniao',
                'status': r.status,
                'pk': r.pk,
            },
        })

    return JsonResponse(events, safe=False)
