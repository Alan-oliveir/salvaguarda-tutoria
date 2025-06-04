from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


class CustomLoginView(LoginView):
    template_name = 'usuarios/login.html'


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')


@login_required
def painel_inicial(request):
    tipo = request.user.tipo.upper()  # força tipo em maiúsculas
    return render(request, 'usuarios/painel_inicial.html', {'tipo': tipo})
