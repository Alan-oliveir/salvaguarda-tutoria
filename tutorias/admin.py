# tutorias/admin.py

from django.contrib import admin

from .models import Reuniao


@admin.register(Reuniao)
class ReuniaoAdmin(admin.ModelAdmin):
    list_display = ['tutorado', 'tutor', 'data', 'horario', 'materia', 'presenca']
    list_filter = ['materia', 'presenca', 'data']
    search_fields = ['tutorado__first_name', 'tutorado__last_name']
