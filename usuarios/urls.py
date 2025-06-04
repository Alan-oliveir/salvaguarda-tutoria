from django.urls import path
from .views import (
    CustomLoginView,
    CustomLogoutView,
    RegistroView,
    painel_inicial,
    perfil_usuario,
    redirect_after_login
)

app_name = 'usuarios'

urlpatterns = [
    path('', redirect_after_login, name='redirect_after_login'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('registro/', RegistroView.as_view(), name='registro'),
    path('painel/', painel_inicial, name='painel_inicial'),
    path('perfil/', perfil_usuario, name='perfil_usuario'),
]
