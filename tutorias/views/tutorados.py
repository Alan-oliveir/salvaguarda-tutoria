from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from tutorias.decorators import tutor_required
from tutorias.models import Reuniao
from usuarios.models import PerfilTutorado


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
