from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from tarefas.models import Tarefa
from tutorias.decorators import tutor_required
from tutorias.forms import FichaDiagnosticaForm, AtividadeExtraForm
from tutorias.models import Reuniao, FichaDiagnostica, AtividadeExtra, GradeEstudo, CheckpointSemanal
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

    # Atualiza os dados
    perfil.serie = request.POST.get('serie', perfil.serie)
    perfil.fez_enem = bool(request.POST.get('fez_enem'))
    perfil.trabalha = bool(request.POST.get('trabalha'))
    perfil.cursos_interesse = request.POST.get('cursos_interesse', '')
    perfil.universidade_pretendida = request.POST.get('universidade_pretendida', '')
    perfil.escola = request.POST.get('escola', '')
    perfil.turno_escolar = request.POST.get('turno_escolar', '')
    perfil.whatsapp = request.POST.get('whatsapp', '')
    perfil.carta_apresentacao = request.POST.get('carta_apresentacao', '').strip()
    perfil.objetivo_principal = request.POST.get('objetivo_principal', '')

    perfil.save()
    messages.success(request, 'Dados atualizados com sucesso!')
    return redirect('tutorias:detalhe_tutorado', pk=pk)


@tutor_required
def ficha_diagnostica(request, pk):
    perfil = get_object_or_404(PerfilTutorado, pk=pk, tutor=request.user)
    tutorado_user = perfil.usuario

    # Busca a ficha existente do aluno ou cria uma nova em branco
    ficha, created = FichaDiagnostica.objects.get_or_create(
        tutorado=tutorado_user,
        defaults={'tutor': request.user}
    )

    if request.method == 'POST':
        form = FichaDiagnosticaForm(request.POST, instance=ficha)
        if form.is_valid():
            f = form.save(commit=False)
            f.tutor = request.user  # Atualiza o autor da edição
            f.save()
            messages.success(request, 'Ficha diagnóstica salva com sucesso!')
            return redirect('tutorias:detalhe_tutorado', pk=pk)
    else:
        form = FichaDiagnosticaForm(instance=ficha)

    return render(request, 'ficha_diagnostica.html', {
        'form': form,
        'tutorado': perfil,
        'usuario': tutorado_user
    })


@tutor_required
def controle_horas(request):
    if request.method == 'POST':
        form = AtividadeExtraForm(request.POST, tutor=request.user)
        if form.is_valid():
            ativ = form.save(commit=False)
            ativ.tutor = request.user
            ativ.save()
            messages.success(request, 'Atividade extra registrada com sucesso!')
            return redirect('tutorias:controle_horas')
    else:
        form = AtividadeExtraForm(tutor=request.user)

    # 1. Busca todas as atividades para mapear os meses existentes
    todas_atividades = AtividadeExtra.objects.filter(tutor=request.user)
    todas_reunioes = Reuniao.objects.filter(tutor=request.user).exclude(duracao_minutos__isnull=True)

    meses_set = set()
    for a in todas_atividades:
        meses_set.add(a.data.strftime('%Y-%m'))
    for r in todas_reunioes:
        data_r = r.data.date() if hasattr(r.data, 'date') else r.data
        meses_set.add(data_r.strftime('%Y-%m'))

    meses_disponiveis = sorted(list(meses_set), reverse=True)
    NOME_MESES = {'01': 'Janeiro', '02': 'Fevereiro', '03': 'Março', '04': 'Abril', '05': 'Maio', '06': 'Junho',
                  '07': 'Julho', '08': 'Agosto', '09': 'Setembro', '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro'}

    opcoes_meses = [{'valor': m, 'rotulo': f"{NOME_MESES[m.split('-')[1]]} {m.split('-')[0]}"} for m in
                    meses_disponiveis]

    # 2. Aplica o filtro recebido pela URL (?mes=YYYY-MM)
    mes_filtro = request.GET.get('mes', '')
    atividades_filtradas = todas_atividades
    reunioes_filtradas = todas_reunioes

    if mes_filtro:
        try:
            ano, mes = mes_filtro.split('-')
            atividades_filtradas = atividades_filtradas.filter(data__year=ano, data__month=mes)
            reunioes_filtradas = reunioes_filtradas.filter(data__year=ano, data__month=mes)
        except ValueError:
            pass

    # 3. Monta o histórico
    historico = []
    total_minutos = 0

    for a in atividades_filtradas:
        historico.append({'data': a.data, 'aluno': a.tutorado.get_nome_completo() if a.tutorado else 'Geral',
                          'descricao': a.descricao, 'minutos': a.duracao_minutos, 'tipo': 'Atividade Extra'})
        total_minutos += a.duracao_minutos

    for r in reunioes_filtradas:
        data_r = r.data.date() if hasattr(r.data, 'date') else r.data
        historico.append({'data': data_r, 'aluno': r.tutorado.get_nome_completo() if r.tutorado else 'Geral',
                          'descricao': f"Reunião: {r.get_materia_display() if hasattr(r, 'get_materia_display') else 'Mentoria'}",
                          'minutos': r.duracao_minutos, 'tipo': 'Reunião'})
        total_minutos += r.duracao_minutos

    historico.sort(key=lambda x: x['data'], reverse=True)
    horas_formatadas = f"{total_minutos // 60}h {total_minutos % 60}m"

    # Geração de texto automático
    qtd_reunioes = reunioes_filtradas.count()
    nomes_alunos = list(set([r.tutorado.first_name for r in reunioes_filtradas if r.tutorado]))

    if nomes_alunos:
        nomes_str = ", ".join(nomes_alunos[:-1]) + " e " + nomes_alunos[-1] if len(nomes_alunos) > 1 else nomes_alunos[
            0]
        texto_relatorio = f"Neste ciclo, realizei {qtd_reunioes} reuniões de acompanhamento com {nomes_str}. "
    else:
        texto_relatorio = f"Neste ciclo, não realizei reuniões diretas. "

    if atividades_filtradas.exists():
        texto_relatorio += f"Também registrei {atividades_filtradas.count()} atividades extras focadas em pesquisa e planejamento. "

    texto_relatorio += f"A minha carga horária total deste período foi de {horas_formatadas}."

    return render(request, 'controle_horas.html', {
        'form': form,
        'historico': historico,
        'total_minutos': total_minutos,
        'horas_formatadas': horas_formatadas,
        'opcoes_meses': opcoes_meses,
        'mes_filtro': mes_filtro,
        'texto_relatorio': texto_relatorio
    })


@tutor_required
def relatorio_impresso(request):
    """Gera a página limpa com filtro dinâmico de mês."""
    atividades = AtividadeExtra.objects.filter(tutor=request.user)
    reunioes = Reuniao.objects.filter(tutor=request.user).exclude(duracao_minutos__isnull=True)

    mes_filtro = request.GET.get('mes', '')
    periodo_texto = "Histórico Completo"

    if mes_filtro:
        try:
            ano, mes = mes_filtro.split('-')
            atividades = atividades.filter(data__year=ano, data__month=mes)
            reunioes = reunioes.filter(data__year=ano, data__month=mes)
            NOME_MESES = {'01': 'Janeiro', '02': 'Fevereiro', '03': 'Março', '04': 'Abril', '05': 'Maio', '06': 'Junho',
                          '07': 'Julho', '08': 'Agosto', '09': 'Setembro', '10': 'Outubro', '11': 'Novembro',
                          '12': 'Dezembro'}
            periodo_texto = f"{NOME_MESES[mes]} de {ano}"
        except ValueError:
            pass

    historico = []
    total_minutos = 0

    for a in atividades:
        historico.append({'data': a.data, 'aluno': a.tutorado.get_nome_completo() if a.tutorado else 'Geral',
                          'descricao': a.descricao, 'minutos': a.duracao_minutos})
        total_minutos += a.duracao_minutos

    for r in reunioes:
        data_reuniao = r.data.date() if hasattr(r.data, 'date') else r.data
        historico.append({'data': data_reuniao, 'aluno': r.tutorado.get_nome_completo() if r.tutorado else 'Geral',
                          'descricao': "Reunião de tutoria", 'minutos': r.duracao_minutos})
        total_minutos += r.duracao_minutos

    historico.sort(key=lambda x: x['data'])
    horas_formatadas = f"{total_minutos // 60}h {total_minutos % 60}m"

    return render(request, 'relatorio_impresso.html', {
        'historico': historico,
        'horas_formatadas': horas_formatadas,
        'tutor': request.user,
        'periodo_texto': periodo_texto
    })


@tutor_required
def ficha_impresso(request, pk):
    perfil = get_object_or_404(PerfilTutorado, pk=pk, tutor=request.user)

    try:
        ficha = perfil.usuario.ficha_diagnostica
    except:
        messages.error(request, "Este aluno ainda não tem uma Ficha Diagnóstica preenchida.")
        return redirect('tutorias:detalhe_tutorado', pk=pk)

    # Busca o plano de ação (Tarefas de planejamento passadas por este tutor)
    plano_acao = Tarefa.objects.filter(
        tutorado=perfil.usuario,
        tutor=request.user,
        categoria='PLANEJAMENTO'
    ).order_by('-data_criacao')

    return render(request, 'ficha_impresso.html', {
        'tutorado': perfil,
        'ficha': ficha,
        'plano_acao': plano_acao
    })


@login_required
def cronograma_estudos_json(request):
    """
    Retorna a grade de estudos no formato de eventos recorrentes do FullCalendar.
    Funciona tanto para o aluno ver o seu próprio cronograma, como para o tutor ver o do aluno.
    """
    # Verifica se um tutor está a pedir para ver a grade de um tutorado específico
    tutorado_id = request.GET.get('tutorado_id')

    if tutorado_id and request.user.tipo == 'TUTOR':
        grade = GradeEstudo.objects.filter(tutorado_id=tutorado_id)
    else:
        # Caso contrário, mostra a grade do próprio utilizador logado (o aluno)
        grade = GradeEstudo.objects.filter(tutorado=request.user)

    eventos = []

    # Mapeamento de cores para as disciplinas para ficar visualmente incrível
    CORES_DISCIPLINAS = {
        'PORTUGUES': '#1a73e8', 'REDACAO': '#d93025', 'MATEMATICA': '#f29900',
        'FISICA': '#188038', 'QUIMICA': '#8e24aa', 'BIOLOGIA': '#009688',
        'HISTORIA': '#795548', 'GEOGRAFIA': '#e91e63', 'FILOSOFIA': '#607d8b',
        'SOCIOLOGIA': '#3f51b5', 'LINGUAS': '#00bcd4', 'REVISAO': '#333333'
    }

    for bloco in grade:
        cor = CORES_DISCIPLINAS.get(bloco.disciplina, '#7b2fbe')

        titulo = bloco.get_disciplina_display()
        if bloco.quinzenal:
            titulo += " (Quinzenal)"

        eventos.append({
            'title': titulo,
            'startTime': bloco.horario_inicio.strftime('%H:%M'),
            'endTime': bloco.horario_fim.strftime('%H:%M'),
            'daysOfWeek': [bloco.dia_semana],
            'backgroundColor': cor,
            'borderColor': cor,
            'textColor': '#ffffff',
            'extendedProps': {
                'id_bloco': bloco.id,
                'disciplina_cod': bloco.disciplina
            }
        })

    return JsonResponse(eventos, safe=False)


@tutor_required
def ver_cronograma_tutorado(request, pk):
    """Permite ao tutor visualizar a grade horária e os checkpoints de um tutorado específico."""
    perfil = get_object_or_404(PerfilTutorado, pk=pk, tutor=request.user)
    checkpoints = CheckpointSemanal.objects.filter(tutorado=perfil.usuario).order_by('-data_fim_semana')

    return render(request, 'ver_cronograma_tutorado.html', {
        'tutorado': perfil,
        'usuario': perfil.usuario,
        'checkpoints': checkpoints
    })
