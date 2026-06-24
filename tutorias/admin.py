from django.contrib import admin

from .models import AtividadeExtra, FichaDiagnostica, Reuniao


@admin.register(Reuniao)
class ReuniaoAdmin(admin.ModelAdmin):
    list_display = ['tutorado', 'tutor', 'data', 'horario', 'materia', 'presenca']
    list_filter = ['materia', 'presenca', 'data']
    search_fields = ['tutorado__first_name', 'tutorado__last_name']


@admin.register(FichaDiagnostica)
class FichaDiagnosticaAdmin(admin.ModelAdmin):
    list_display = ('tutorado', 'tutor', 'data_atualizacao')
    search_fields = ('tutorado__first_name', 'tutor__first_name')
    raw_id_fields = ('tutorado', 'tutor')


@admin.register(AtividadeExtra)
class AtividadeExtraAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'tutor', 'tutorado', 'data', 'duracao_minutos')
    list_filter = ('data', 'tutor')
    search_fields = ('descricao', 'tutor__first_name')
