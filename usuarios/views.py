from datetime import date
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView

from materiais.models import Material
from tarefas.models import Tarefa
from tutorias.models import Reuniao, AtividadeExtra
from .forms import CustomPasswordChangeForm
from .forms import CustomPasswordResetForm, CustomSetPasswordForm
from .forms import CustomUserCreationForm
from .models import CustomUser, PerfilTutorado


class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('usuarios:painel_inicial')

    def form_invalid(self, form):
        messages.error(self.request, 'Usuário ou senha incorretos.')
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('usuarios:login')
    http_method_names = ['post']

    def get(self, request, *args, **kwargs):
        return self.render_to_response({})

    def post(self, request, *args, **kwargs):
        messages.success(request, 'Logout realizado com sucesso!')
        return super().post(request, *args, **kwargs)


class RegistroView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'registro.html'
    success_url = reverse_lazy('usuarios:login')

    def form_valid(self, form):
        messages.success(self.request, 'Conta criada com sucesso! Faça login para continuar.')
        return super().form_valid(form)


@login_required
def painel_inicial(request):
    tipo = request.user.tipo.upper()
    context = {'tipo': tipo, 'user': request.user}
    User = get_user_model()

    if tipo == 'ADMIN':
        context['total_usuarios'] = User.objects.count()
        context['total_tutores'] = User.objects.filter(tipo='TUTOR').count()
        context['total_tutorados'] = User.objects.filter(tipo='TUTORADO').count()

    elif tipo == 'TUTOR':
        tutorados = PerfilTutorado.objects.filter(tutor=request.user)
        reunioes_futuras = Reuniao.objects.filter(
            tutor=request.user,
            data__gte=date.today()
        ).select_related('tutorado').order_by('data', 'horario')

        context.update({
            'meus_tutorados': tutorados.count(),
            'reunioes_pendentes': reunioes_futuras.count(),
            'proximas_reunioes': reunioes_futuras[:3],
        })

        context['total_materiais'] = Material.objects.filter(enviado_por=request.user).count()

    elif tipo == 'TUTORADO':
        # Tutorado vê suas próprias reuniões
        reunioes_futuras = Reuniao.objects.filter(
            tutorado=request.user,
            data__gte=date.today()
        ).select_related('tutor').order_by('data', 'horario')

        try:
            perfil = request.user.perfil_tutorado
            tem_tutor = perfil.tutor is not None
        except PerfilTutorado.DoesNotExist:
            perfil = None
            tem_tutor = False

        context.update({
            'proximas_reunioes': reunioes_futuras[:3],
            'reunioes_pendentes': reunioes_futuras.count(),
            'perfil': perfil,
            'tem_tutor': tem_tutor,
        })

        context['tarefas_pendentes'] = Tarefa.objects.filter(tutorado=request.user, status='PENDENTE').count()
        context['total_materiais'] = Material.objects.filter(tutorado=request.user).count()

    return render(request, 'painel_inicial.html', context)


@login_required
def perfil_usuario(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        # email com validação de unicidade já no model.save()
        novo_email = request.POST.get('email', '').strip()
        if novo_email and novo_email != user.email:
            try:
                user.email = novo_email
                user.save()
            except ValueError as e:
                messages.error(request, str(e))
                return redirect('usuarios:perfil_usuario')
        else:
            user.save(update_fields=['first_name', 'last_name'])
        messages.success(request, 'Perfil atualizado com sucesso!')
        return redirect('usuarios:perfil_usuario')

    return render(request, 'perfil.html', {'user': request.user})


@login_required
def relatorio_geral(request):
    """Nova view dedicada ao painel de relatórios do administrador."""
    if request.user.tipo != 'ADMIN':
        return redirect('usuarios:painel_inicial')

    User = get_user_model()

    # Métricas Globais
    total_usuarios = User.objects.count()
    total_tutores = User.objects.filter(tipo='TUTOR').count()
    total_tutorados = User.objects.filter(tipo='TUTORADO').count()

    # 1: Alunos Órfãos
    alunos_orfaos = PerfilTutorado.objects.filter(tutor__isnull=True).select_related('usuario')

    # 2: Tutores Inativos (15 dias sem registros)
    data_limite = timezone.now().date() - timedelta(days=15)
    tutores = User.objects.filter(tipo='TUTOR', is_active=True)
    tutores_inativos = []

    for tutor in tutores:
        tem_reuniao = Reuniao.objects.filter(tutor=tutor, data__gte=data_limite).exists()
        tem_atividade = AtividadeExtra.objects.filter(tutor=tutor, data__gte=data_limite).exists()

        if not tem_reuniao and not tem_atividade:
            qtd_alunos = PerfilTutorado.objects.filter(tutor=tutor).count()
            tutores_inativos.append({'user': tutor, 'qtd_alunos': qtd_alunos})

    return render(request, 'relatorio_geral.html', {
        'total_usuarios': total_usuarios,
        'total_tutores': total_tutores,
        'total_tutorados': total_tutorados,
        'alunos_orfaos': alunos_orfaos,
        'tutores_inativos': tutores_inativos,
    })


def redirect_after_login(request):
    if request.user.is_authenticated:
        return redirect('usuarios:painel_inicial')
    return redirect('usuarios:login')


class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset.html'
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('usuarios:password_reset_done')
    email_template_name = 'password_reset_email.html'


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('usuarios:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'


class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'alterar_senha.html'
    success_url = reverse_lazy('usuarios:perfil_usuario')

    def form_valid(self, form):
        messages.success(self.request, 'Sua senha foi alterada com sucesso!')
        return super().form_valid(form)
