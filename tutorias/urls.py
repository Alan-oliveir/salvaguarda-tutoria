# tutorias/urls.py

from django.urls import path
from . import views

app_name = 'tutorias'

urlpatterns = [
    path('', views.lista_tutorados, name='lista_tutorados'),
    path('novo/', views.cadastrar_tutorado, name='cadastrar_tutorado'),
    path('<int:pk>/', views.detalhe_tutorado, name='detalhe_tutorado'),
    path('<int:pk>/editar/', views.editar_tutorado, name='editar_tutorado'),
]