from django.contrib import admin

from .models import Material


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'tutorado', 'enviado_por', 'data_envio')
    list_filter = ('tipo', 'data_envio')
    search_fields = ('titulo', 'tutorado__first_name', 'enviado_por__first_name')
