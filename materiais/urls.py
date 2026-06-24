from django.urls import path

from . import views

app_name = 'materiais'

urlpatterns = [
    path('', views.lista_materiais, name='lista_materiais'),
    path('enviar/', views.enviar_material, name='enviar_material'),
    path('<int:pk>/deletar/', views.deletar_material, name='deletar_material'),
]
