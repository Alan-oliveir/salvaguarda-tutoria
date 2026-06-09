# tutorias/admin.py

from django.contrib import admin
from .models import Tutorado, Reuniao


@admin.register(Tutorado)
class TutoradoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tutor', 'serie', 'cidade', 'estado', 'fez_enem', 'criado_em']
    list_filter = ['serie', 'fez_enem', 'criado_em']
    search_fields = ['nome', 'email', 'whatsapp']
    raw_id_fields = ['tutor']


@admin.register(Reuniao)
class ReuniaoAdmin(admin.ModelAdmin):
    list_display = ['tutorado', 'data', 'horario', 'materia', 'presenca', 'duracao_minutos']
    list_filter = ['materia', 'presenca', 'data']
    search_fields = ['tutorado__nome']