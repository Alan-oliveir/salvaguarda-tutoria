from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from tutorias.decorators import tutor_required
from tutorias.forms import FichaDiagnosticaForm, AtividadeExtraForm
from tutorias.models import Reuniao, FichaDiagnostica, AtividadeExtra
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

    return render(request, 'controle_horas.html', {
        'form': form,
        'historico': historico,
        'total_minutos': total_minutos,
        'horas_formatadas': horas_formatadas,
        'opcoes_meses': opcoes_meses,
        'mes_filtro': mes_filtro
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
