from django.urls import path

from .views.disponibilidade import (
    disponibilidade, deletar_disponibilidade, calendario, slots_json
)
from .views.reunioes import (
    solicitar_reuniao, minhas_reunioes, lista_reunioes,
    detalhe_reuniao, editar_reuniao, cancelar_reuniao, realizar_reuniao
)
from .views.tutorados import (
    lista_tutorados, vincular_tutorado, desvincular_tutorado,
    detalhe_tutorado, editar_tutorado
)

app_name = 'tutorias'

urlpatterns = [
    # Tutorados
    path('', lista_tutorados, name='lista_tutorados'),
    path('vincular/', vincular_tutorado, name='vincular_tutorado'),
    path('<int:pk>/desvincular/', desvincular_tutorado, name='desvincular_tutorado'),
    path('<int:pk>/', detalhe_tutorado, name='detalhe_tutorado'),
    path('<int:pk>/editar/', editar_tutorado, name='editar_tutorado'),

    # Disponibilidade do tutor
    path('disponibilidade/', disponibilidade, name='disponibilidade'),
    path('disponibilidade/<int:pk>/deletar/', deletar_disponibilidade, name='deletar_disponibilidade'),

    # Calendário
    path('calendario/', calendario, name='calendario'),
    path('calendario/slots/', slots_json, name='slots_json'),
    path('calendario/agendar/', solicitar_reuniao, name='solicitar_reuniao'),

    # Reuniões — tutor
    path('reunioes/', lista_reunioes, name='lista_reunioes'),
    path('reunioes/<int:pk>/', detalhe_reuniao, name='detalhe_reuniao'),
    path('reunioes/<int:pk>/editar/', editar_reuniao, name='editar_reuniao'),

    # Reuniões — tutorado
    path('minhas-reunioes/', minhas_reunioes, name='minhas_reunioes'),

    # Ações compartilhadas
    path('reunioes/<int:pk>/cancelar/', cancelar_reuniao, name='cancelar_reuniao'),
    path('reunioes/<int:pk>/realizar/', realizar_reuniao, name='realizar_reuniao'),
]
