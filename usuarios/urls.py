from django.urls import path
from .views import CustomLoginView, CustomLogoutView, painel_inicial

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('painel/', painel_inicial, name='painel_inicial'),
]
