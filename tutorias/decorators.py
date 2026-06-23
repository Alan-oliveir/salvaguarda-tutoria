from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def tutor_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.tipo not in ('TUTOR', 'ADMIN'):
            messages.error(request, 'Acesso restrito a tutores.')
            return redirect('usuarios:painel_inicial')
        return view_func(request, *args, **kwargs)

    return wrapper


def tutorado_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.tipo != 'TUTORADO':
            messages.error(request, 'Acesso restrito a tutorados.')
            return redirect('usuarios:painel_inicial')
        return view_func(request, *args, **kwargs)

    return wrapper
