# tutorias/views.py

from datetime import date, datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from usuarios.models import PerfilTutorado
from .models import Reuniao


# Decorator

def tutor_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.tipo not in ('TUTOR', 'ADMIN'):
            messages.error(request, 'Acesso restrito a tutores.')
            return redirect('usuarios:painel_inicial')
        return view_func(request, *args, **kwargs)

    return wrapper


# Tutorados

@tutor_required
def lista_tutorados(request):
    """Lista os tutorados vinculados ao tutor logado."""
    tutorados = PerfilTutorado.objects.filter(
        tutor=request.user
    ).select_related('usuario').order_by('usuario__first_name')

    return render(request, 'lista_tutorados.html', {
        'tutorados': tutorados,
        'series_choices': PerfilTutorado.SERIE_CHOICES,
    })


@tutor_required
def vincular_tutorado(request):
    """
    Exibe tutorados registrados no app ainda sem tutor (ou já vinculados
    a este tutor) e permite ao tutor vinculá-los a si mesmo.
    """
    if request.method == 'POST':
        perfil_pk = request.POST.get('perfil_pk')
        perfil = get_object_or_404(PerfilTutorado, pk=perfil_pk)

        # Só vincula se ainda não tiver tutor
        if perfil.tutor is not None and perfil.tutor != request.user:
            messages.error(request, 'Este tutorado já está vinculado a outro tutor.')
            return redirect('tutorias:vincular_tutorado')

        perfil.tutor = request.user
        perfil.save(update_fields=['tutor'])
        messages.success(request, f'{perfil.usuario.get_nome_completo()} vinculado(a) com sucesso!')
        return redirect('tutorias:lista_tutorados')

    # GET — busca tutorados sem tutor
    disponiveis = PerfilTutorado.objects.filter(
        tutor__isnull=True
    ).select_related('usuario').order_by('usuario__first_name')

    return render(request, 'vincular_tutorado.html', {
        'disponiveis': disponiveis,
    })


@tutor_required
def desvincular_tutorado(request, pk):
    """Remove o vínculo entre tutor e tutorado."""
    perfil = get_object_or_404(PerfilTutorado, pk=pk, tutor=request.user)
    if request.method == 'POST':
        nome = perfil.usuario.get_nome_completo()
        perfil.tutor = None
        perfil.save(update_fields=['tutor'])
        messages.success(request, f'{nome} desvinculado(a).')
    return redirect('tutorias:lista_tutorados')


@tutor_required
def detalhe_tutorado(request, pk):
    """Detalhe de um tutorado vinculado ao tutor logado."""
    perfil = get_object_or_404(
        PerfilTutorado.objects.select_related('usuario'),
        pk=pk, tutor=request.user
    )
    reunioes = Reuniao.objects.filter(
        tutorado=perfil.usuario
    ).order_by('-data', '-horario')

    return render(request, 'detalhe_tutorado.html', {
        'tutorado': perfil,  # PerfilTutorado
        'usuario': perfil.usuario,  # CustomUser — para nome, foto, email, etc.
        'reunioes': reunioes,
        'materias_choices': Reuniao.MATERIA_CHOICES,
    })


@tutor_required
def editar_tutorado(request, pk):
    """Edita dados do PerfilTutorado (campos acadêmicos)."""
    perfil = get_object_or_404(PerfilTutorado, pk=pk, tutor=request.user)

    if request.method == 'GET':
        return render(request, 'editar_tutorado.html', {
            'tutorado': perfil,
            'usuario': perfil.usuario,
            'series_choices': PerfilTutorado.SERIE_CHOICES,
            'turno_choices': PerfilTutorado.TURNO_CHOICES,
        })

    # POST — atualiza apenas os campos do PerfilTutorado
    perfil.serie = request.POST.get('serie', perfil.serie)
    perfil.fez_enem = bool(request.POST.get('fez_enem'))
    perfil.cursos_interesse = request.POST.get('cursos_interesse', '')
    perfil.escola = request.POST.get('escola', '')
    perfil.turno_escolar = request.POST.get('turno_escolar', '')
    perfil.whatsapp = request.POST.get('whatsapp', '')
    perfil.responsavel_nome = request.POST.get('responsavel_nome', '')
    perfil.responsavel_telefone = request.POST.get('responsavel_telefone', '')
    perfil.objetivo_principal = request.POST.get('objetivo_principal', '')
    perfil.save()

    messages.success(request, 'Dados atualizados com sucesso!')
    return redirect('tutorias:detalhe_tutorado', pk=pk)


# Reuniões

@tutor_required
def lista_reunioes(request):
    reunioes = Reuniao.objects.filter(
        tutor=request.user
    ).select_related('tutorado').order_by('-data', '-horario')

    filtro_tutorado = request.GET.get('tutorado', '')
    filtro_materia = request.GET.get('materia', '')

    if filtro_tutorado:
        reunioes = reunioes.filter(tutorado_id=filtro_tutorado)
    if filtro_materia:
        reunioes = reunioes.filter(materia=filtro_materia)

    # Apenas tutorados vinculados ao tutor logado
    tutorados_vinculados = PerfilTutorado.objects.filter(
        tutor=request.user
    ).select_related('usuario')

    if request.method == 'POST':
        return _criar_reuniao(request)

    return render(request, 'lista_reunioes.html', {
        'reunioes': reunioes,
        'tutorados': tutorados_vinculados,
        'materias_choices': Reuniao.MATERIA_CHOICES,
        'filtro_tutorado': filtro_tutorado,
        'filtro_materia': filtro_materia,
        'hoje': date.today(),
    })


def _criar_reuniao(request):
    tutorado_id = request.POST.get('tutorado')
    data_str = request.POST.get('data', '')
    horario_str = request.POST.get('horario', '')

    # Valida que o tutorado pertence ao tutor
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
    )
    messages.success(request, 'Reunião registrada com sucesso!')
    return redirect('tutorias:lista_reunioes')


@tutor_required
def detalhe_reuniao(request, pk):
    reuniao = get_object_or_404(
        Reuniao.objects.select_related('tutorado', 'tutor'),
        pk=pk, tutor=request.user
    )
    return render(request, 'detalhe_reuniao.html', {
        'reuniao': reuniao,
        'materias_choices': Reuniao.MATERIA_CHOICES,
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


@tutor_required
def deletar_reuniao(request, pk):
    reuniao = get_object_or_404(Reuniao, pk=pk, tutor=request.user)
    if request.method == 'POST':
        reuniao.delete()
        messages.success(request, 'Reunião excluída.')
    return redirect('tutorias:lista_reunioes')
