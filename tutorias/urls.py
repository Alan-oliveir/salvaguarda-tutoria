# tutorias/urls.py

from django.urls import path
from . import views

app_name = 'tutorias'

urlpatterns = [
    # Tutorados
    path('',                              views.lista_tutorados,      name='lista_tutorados'),
    path('vincular/',                     views.vincular_tutorado,    name='vincular_tutorado'),
    path('<int:pk>/desvincular/',         views.desvincular_tutorado, name='desvincular_tutorado'),
    path('<int:pk>/',                     views.detalhe_tutorado,     name='detalhe_tutorado'),
    path('<int:pk>/editar/',              views.editar_tutorado,      name='editar_tutorado'),

    # Disponibilidade do tutor
    path('disponibilidade/',              views.disponibilidade,           name='disponibilidade'),
    path('disponibilidade/<int:pk>/deletar/', views.deletar_disponibilidade, name='deletar_disponibilidade'),

    # Calendário (tutorado)
    path('calendario/',                   views.calendario,        name='calendario'),
    path('calendario/slots/',             views.slots_json,        name='slots_json'),
    path('calendario/agendar/',           views.solicitar_reuniao, name='solicitar_reuniao'),

    # Reuniões — tutor
    path('reunioes/',                     views.lista_reunioes,    name='lista_reunioes'),
    path('reunioes/<int:pk>/',            views.detalhe_reuniao,   name='detalhe_reuniao'),
    path('reunioes/<int:pk>/editar/',     views.editar_reuniao,    name='editar_reuniao'),

    # Reuniões — tutorado
    path('minhas-reunioes/',              views.minhas_reunioes,   name='minhas_reunioes'),

    # Ações compartilhadas
    path('reunioes/<int:pk>/cancelar/',   views.cancelar_reuniao,  name='cancelar_reuniao'),
    path('reunioes/<int:pk>/realizar/',   views.realizar_reuniao,  name='realizar_reuniao'),
]
