from django.urls import path

from .views import (
    CustomLoginView,
    CustomLogoutView,
    RegistroView,
    painel_inicial,
    perfil_usuario,
    redirect_after_login,
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView
)

app_name = 'usuarios'

urlpatterns = [
    path('', redirect_after_login, name='redirect_after_login'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('registro/', RegistroView.as_view(), name='registro'),
    path('painel/', painel_inicial, name='painel_inicial'),
    path('perfil/', perfil_usuario, name='perfil_usuario'),

    # Rotas de recuperação de senha:
    path('recuperar-senha/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('recuperar-senha/enviado/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('recuperar-senha/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('recuperar-senha/concluido/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
