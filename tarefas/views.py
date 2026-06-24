from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .forms import TarefaForm
from .models import Tarefa


@login_required
def lista_tarefas(request):
    """Exibe as tarefas dependendo do tipo de usuário."""
    if request.user.tipo == 'TUTORADO':
        tarefas = Tarefa.objects.filter(tutorado=request.user)
    elif request.user.tipo == 'TUTOR':
        tarefas = Tarefa.objects.filter(tutor=request.user)
    else:
        tarefas = Tarefa.objects.all()  # Admin vê tudo

    # Separação visual básica para o template
    pendentes = tarefas.filter(status='PENDENTE')
    concluidas = tarefas.filter(status='CONCLUIDA')

    return render(request, 'lista_tarefas.html', {
        'pendentes': pendentes,
        'concluidas': concluidas,
        'total_pendentes': pendentes.count(),
    })


@login_required
def criar_tarefa(request):
    """Apenas tutores podem criar tarefas."""
    if request.user.tipo != 'TUTOR' and request.user.tipo != 'ADMIN':
        messages.error(request, 'Apenas tutores podem criar tarefas.')
        return redirect('tarefas:lista_tarefas')

    if request.method == 'POST':
        form = TarefaForm(request.POST, tutor=request.user)
        if form.is_valid():
            tarefa = form.save(commit=False)
            tarefa.tutor = request.user
            tarefa.save()
            messages.success(request, 'Tarefa atribuída com sucesso!')
            return redirect('tarefas:lista_tarefas')
    else:
        form = TarefaForm(tutor=request.user)

    return render(request, 'form_tarefa.html', {'form': form, 'acao': 'Nova Tarefa'})


@login_required
def editar_tarefa(request, pk):
    """Edita uma tarefa existente."""
    tarefa = get_object_or_404(Tarefa, pk=pk, tutor=request.user)

    if request.method == 'POST':
        form = TarefaForm(request.POST, instance=tarefa, tutor=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tarefa atualizada com sucesso!')
            return redirect('tarefas:lista_tarefas')
    else:
        form = TarefaForm(instance=tarefa, tutor=request.user)

    return render(request, 'form_tarefa.html', {'form': form, 'acao': 'Editar Tarefa', 'tarefa': tarefa})


@login_required
def deletar_tarefa(request, pk):
    tarefa = get_object_or_404(Tarefa, pk=pk, tutor=request.user)
    if request.method == 'POST':
        tarefa.delete()
        messages.success(request, 'Tarefa excluída.')
    return redirect('tarefas:lista_tarefas')


@login_required
def alternar_status_tarefa(request, pk):
    """Tutorado clica para concluir, ou desmarcar caso tenha clicado errado."""
    tarefa = get_object_or_404(Tarefa, pk=pk)

    # Apenas o tutorado dono da tarefa (ou o tutor dele) podem mexer no status
    if request.user != tarefa.tutorado and request.user != tarefa.tutor:
        messages.error(request, 'Permissão negada.')
        return redirect('tarefas:lista_tarefas')

    if request.method == 'POST':
        if tarefa.status == 'PENDENTE':
            tarefa.status = 'CONCLUIDA'
            tarefa.data_conclusao = timezone.now()
            messages.success(request, 'Parabéns! Tarefa marcada como concluída. 🎉')
        else:
            tarefa.status = 'PENDENTE'
            tarefa.data_conclusao = None
            messages.warning(request, 'Tarefa reaberta.')

        tarefa.save(update_fields=['status', 'data_conclusao'])

    return redirect('tarefas:lista_tarefas')
