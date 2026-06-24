from django.contrib import admin

from .models import Tarefa


@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'tutorado', 'tutor', 'status', 'data_limite', 'esta_atrasada')
    list_filter = ('status', 'categoria', 'data_limite')
    search_fields = ('titulo', 'tutorado__first_name', 'tutor__first_name')
    readonly_fields = ('data_criacao', 'data_conclusao')
