from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from usuarios.models import PerfilTutorado
from .forms import MaterialForm
from .models import Material


@login_required
def lista_materiais(request):
    """Lista os materiais relevantes para o usuário logado."""
    if request.user.tipo == 'TUTORADO':
        materiais = Material.objects.filter(tutorado=request.user)
    elif request.user.tipo == 'TUTOR':
        # Pega os IDs dos tutorados deste tutor
        tutorados_ids = PerfilTutorado.objects.filter(tutor=request.user).values_list('usuario_id', flat=True)
        # Mostra os materiais associados a esses tutorados
        materiais = Material.objects.filter(tutorado_id__in=tutorados_ids)
    else:
        materiais = Material.objects.all()

    return render(request, 'lista_materiais.html', {'materiais': materiais})


@login_required
def enviar_material(request):
    """Processa o upload de um arquivo ou cadastro de um link."""
    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            material = form.save(commit=False)
            material.enviado_por = request.user

            # Se for tutorado, preenche a FK oculta automaticamente
            if request.user.tipo == 'TUTORADO':
                material.tutorado = request.user

            material.save()
            messages.success(request, 'Material adicionado com sucesso!')
            return redirect('materiais:lista_materiais')
    else:
        form = MaterialForm(user=request.user)

    return render(request, 'enviar_material.html', {'form': form})


@login_required
def deletar_material(request, pk):
    """Exclui um material (se o usuário tiver permissão)."""
    material = get_object_or_404(Material, pk=pk)

    # Pode deletar se foi ele quem enviou
    pode_deletar = (request.user == material.enviado_por or request.user.tipo == 'ADMIN')

    # Tutor também pode deletar materiais enviados pelo tutorado (se ele for o tutor daquele aluno)
    if not pode_deletar and request.user.tipo == 'TUTOR':
        if PerfilTutorado.objects.filter(usuario=material.tutorado, tutor=request.user).exists():
            pode_deletar = True

    if request.method == 'POST' and pode_deletar:
        material.delete()
        messages.success(request, 'Material excluído com sucesso.')
    elif not pode_deletar:
        messages.error(request, 'Você não tem permissão para excluir este material.')

    return redirect('materiais:lista_materiais')
