from django.urls import path

from . import views

app_name = 'tarefas'

urlpatterns = [
    path('', views.lista_tarefas, name='lista_tarefas'),
    path('criar/', views.criar_tarefa, name='criar_tarefa'),
    path('<int:pk>/editar/', views.editar_tarefa, name='editar_tarefa'),
    path('<int:pk>/deletar/', views.deletar_tarefa, name='deletar_tarefa'),
    path('<int:pk>/status/', views.alternar_status_tarefa, name='alternar_status'),
]
