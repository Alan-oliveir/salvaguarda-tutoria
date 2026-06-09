from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CustomUserCreationForm
from .models import CustomUser


class CustomLoginView(LoginView):
    template_name = 'usuarios/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('usuarios:painel_inicial')

    def form_invalid(self, form):
        messages.error(self.request, 'Usuário ou senha incorretos.')
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('usuarios:login')

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'Logout realizado com sucesso!')
        return super().dispatch(request, *args, **kwargs)


class RegistroView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'usuarios/registro.html'
    success_url = reverse_lazy('usuarios:login')

    def form_valid(self, form):
        messages.success(self.request, 'Conta criada com sucesso! Faça login para continuar.')
        return super().form_valid(form)


@login_required
def painel_inicial(request):
    from tutorias.models import Tutorado, Reuniao
    from datetime import date

    tipo = request.user.tipo.upper()
    context = {'tipo': tipo, 'user': request.user}

    if tipo == 'ADMIN':
        context.update({
            'total_usuarios': CustomUser.objects.count(),
            'total_tutores': CustomUser.objects.filter(tipo='TUTOR').count(),
            'total_tutorados': CustomUser.objects.filter(tipo='TUTORADO').count(),
        })

    elif tipo == 'TUTOR':
        tutorados = Tutorado.objects.filter(tutor=request.user)
        reunioes_futuras = Reuniao.objects.filter(
            tutorado__tutor=request.user,
            data__gte=date.today()
        ).order_by('data', 'horario')

        context.update({
            'meus_tutorados': tutorados.count(),
            'reunioes_pendentes': reunioes_futuras.count(),
            'proximas_reunioes': reunioes_futuras[:3],
        })

    elif tipo == 'TUTORADO':
        context.update({
            'tarefas_pendentes': 0,
            'proxima_reuniao': None,
            'materiais_novos': 0,
        })

    return render(request, 'usuarios/painel_inicial.html', context)


@login_required
def perfil_usuario(request):
    """View para visualizar e editar perfil do usuário"""
    if request.method == 'POST':
        # TODO: Implementar edição de perfil
        messages.success(request, 'Perfil atualizado com sucesso!')
        return redirect('perfil_usuario')

    return render(request, 'usuarios/perfil.html', {'user': request.user})


def redirect_after_login(request):
    """Redireciona usuário para painel apropriado após login"""
    if request.user.is_authenticated:
        return redirect('usuarios:painel_inicial')
    return redirect('usuarios:login')
