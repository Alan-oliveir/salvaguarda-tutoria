# tutorias/urls.py

from django.urls import path

from . import views

app_name = 'tutorias'

urlpatterns = [
    # Tutorados
    path('', views.lista_tutorados, name='lista_tutorados'),
    path('vincular/', views.vincular_tutorado, name='vincular_tutorado'),
    path('<int:pk>/desvincular/', views.desvincular_tutorado, name='desvincular_tutorado'),
    path('<int:pk>/', views.detalhe_tutorado, name='detalhe_tutorado'),
    path('<int:pk>/editar/', views.editar_tutorado, name='editar_tutorado'),

    # Reuniões
    path('reunioes/', views.lista_reunioes, name='lista_reunioes'),
    path('reunioes/<int:pk>/', views.detalhe_reuniao, name='detalhe_reuniao'),
    path('reunioes/<int:pk>/editar/', views.editar_reuniao, name='editar_reuniao'),
    path('reunioes/<int:pk>/deletar/', views.deletar_reuniao, name='deletar_reuniao'),
]
