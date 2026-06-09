# tutorias/views.py

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404

from .models import Tutorado, Reuniao
   

def tutor_required(view_func):
    """Decorator: exige login e que o usuário seja TUTOR ou ADMIN."""
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.tipo not in ('TUTOR', 'ADMIN'):
            messages.error(request, 'Acesso restrito a tutores.')
            return redirect('usuarios:painel_inicial')
        return view_func(request, *args, **kwargs)
    return wrapper


@tutor_required
def lista_tutorados(request):
    tutorados = Tutorado.objects.filter(tutor=request.user)
    series_choices = Tutorado.SERIE_CHOICES
    return render(request, 'tutorias/lista_tutorados.html', {
        'tutorados': tutorados,
        'series_choices': series_choices,
    })


@tutor_required
def cadastrar_tutorado(request):
    if request.method == 'GET':
        return render(request, 'tutorias/cadastrar.html', {
            'series_choices': Tutorado.SERIE_CHOICES,
        })

    nome = request.POST.get('nome', '').strip()
    if not nome:
        messages.error(request, 'O nome é obrigatório.')
        return redirect('tutorias:cadastrar_tutorado')

    foto = request.FILES.get('foto')

    Tutorado.objects.create(
        tutor=request.user,
        nome=nome,
        foto=foto,
        estado=request.POST.get('estado', ''),
        cidade=request.POST.get('cidade', ''),
        serie=request.POST.get('serie', '3EM'),
        idade=request.POST.get('idade') or None,
        fez_enem=bool(request.POST.get('fez_enem')),
        cursos_interesse=request.POST.get('cursos_interesse', ''),
        whatsapp=request.POST.get('whatsapp', ''),
        email=request.POST.get('email', ''),
    )

    messages.success(request, f'{nome} cadastrado(a) com sucesso!')
    return redirect('tutorias:lista_tutorados')


@tutor_required
def detalhe_tutorado(request, pk):
    tutorado = get_object_or_404(Tutorado, pk=pk)
    if tutorado.tutor != request.user and not request.user.tipo == 'ADMIN':
        raise Http404()

    reunioes = tutorado.reunioes.order_by('-data', '-horario')
    return render(request, 'tutorias/detalhe_tutorado.html', {
        'tutorado': tutorado,
        'reunioes': reunioes,
        'materias_choices': Reuniao.MATERIA_CHOICES,
    })


@tutor_required
def editar_tutorado(request, pk):
    tutorado = get_object_or_404(Tutorado, pk=pk)
    if tutorado.tutor != request.user:
        raise Http404()

    if request.method == 'GET':
        return render(request, 'tutorias/editar.html', {
            'tutorado': tutorado,
            'series_choices': Tutorado.SERIE_CHOICES,
        })

    tutorado.nome = request.POST.get('nome', tutorado.nome).strip()
    tutorado.estado = request.POST.get('estado', '')
    tutorado.cidade = request.POST.get('cidade', '')
    tutorado.serie = request.POST.get('serie', tutorado.serie)
    tutorado.idade = request.POST.get('idade') or None
    tutorado.fez_enem = bool(request.POST.get('fez_enem'))
    tutorado.cursos_interesse = request.POST.get('cursos_interesse', '')
    tutorado.whatsapp = request.POST.get('whatsapp', '')
    tutorado.email = request.POST.get('email', '')

    if request.FILES.get('foto'):
        tutorado.foto = request.FILES['foto']

    tutorado.save()
    messages.success(request, 'Dados atualizados com sucesso!')
    return redirect('tutorias:detalhe_tutorado', pk=pk)