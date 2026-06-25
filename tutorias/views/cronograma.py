from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from tutorias.models import GradeEstudo, CheckpointSemanal


@login_required
def cronograma(request):
    """Página principal onde o aluno visualiza e edita a sua rotina de estudos."""
    if request.user.tipo != 'TUTORADO':
        messages.error(request, "Acesso restrito a tutorados.")
        return redirect('usuarios:painel_inicial')

    if request.method == 'POST':
        # 1. Lógica do Checkpoint Semanal
        if 'checkpoint' in request.POST:
            status = request.POST.get('status')
            observacoes = request.POST.get('observacoes', '')
            hoje = timezone.now().date()
            dias_para_domingo = (hoje.weekday() + 1) % 7
            ultimo_domingo = hoje - timedelta(days=dias_para_domingo)

            CheckpointSemanal.objects.create(
                tutorado=request.user, data_fim_semana=ultimo_domingo,
                status=status, observacoes=observacoes
            )
            messages.success(request, "Checkpoint da semana registado com sucesso! Excelente trabalho!")
            return redirect('tutorias:cronograma')

        # 2. Lógica de Adicionar Bloco de Estudo
        elif 'adicionar_bloco' in request.POST:
            disciplina = request.POST.get('disciplina')
            dia_semana = request.POST.get('dia_semana')
            horario_inicio = request.POST.get('horario_inicio')
            horario_fim = request.POST.get('horario_fim')
            quinzenal = request.POST.get('quinzenal') == '1'

            GradeEstudo.objects.create(
                tutorado=request.user,
                disciplina=disciplina,
                dia_semana=dia_semana,
                horario_inicio=horario_inicio,
                horario_fim=horario_fim,
                quinzenal=quinzenal
            )
            messages.success(request, "Matéria adicionada ao seu cronograma!")
            return redirect('tutorias:cronograma')

    disciplinas_choices = GradeEstudo.DISCIPLINA_CHOICES
    return render(request, 'cronograma.html', {
        'disciplinas_choices': disciplinas_choices
    })


@login_required
def deletar_bloco_estudo(request, pk):
    """Remove um bloco de estudo do cronograma (apenas se pertencer ao aluno logado)."""
    if request.method == 'POST':
        bloco = get_object_or_404(GradeEstudo, pk=pk, tutorado=request.user)
        bloco.delete()
        messages.success(request, "Horário removido do cronograma.")
    return redirect('tutorias:cronograma')
