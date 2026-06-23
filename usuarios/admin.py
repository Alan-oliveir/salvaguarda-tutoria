from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import CustomUser, PerfilTutor, PerfilTutorado


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    # Campos exibidos na lista
    list_display = [
        'username',
        'get_nome_completo',
        'email',
        'tipo_badge',
        'is_active',
        'date_joined',
        'data_ultimo_acesso'
    ]

    # Campos para filtrar
    list_filter = [
        'tipo',
        'is_active',
        'is_staff',
        'date_joined',
        'cidade',
        'estado'
    ]

    # Campos de busca
    search_fields = [
        'username',
        'first_name',
        'last_name',
        'email',
        'telefone'
    ]

    # Campos editáveis diretamente na lista
    list_editable = ['is_active']

    # Ordenação
    ordering = ['first_name', 'last_name']

    # Campos para edição
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Específicas', {
            'fields': (
                'tipo',
                'telefone',
                'data_nascimento',
                'foto_perfil'
            )
        }),
        ('Endereço', {
            'fields': (
                'endereco',
                'cidade',
                'estado'
            ),
            'classes': ('collapse',)
        }),
        ('Dados Educacionais (Tutorado)', {
            'fields': (
                'serie_escolar',
                'ja_fez_enem',
                'cursos_interesse'
            ),
            'classes': ('collapse',)
        }),
        ('Controle do Sistema', {
            'fields': (
                'data_ultimo_acesso',
                'ativo',
                'observacoes'
            ),
            'classes': ('collapse',)
        }),
    )

    # Campos para criação de usuário
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais', {
            'fields': (
                'first_name',
                'last_name',
                'email',
                'tipo'
            )
        }),
    )

    # Número de itens por página
    list_per_page = 25

    # Ações personalizadas
    actions = ['ativar_usuarios', 'desativar_usuarios']

    def get_nome_completo(self, obj):
        """Retorna o nome completo formatado"""
        return obj.get_nome_completo()

    get_nome_completo.short_description = 'Nome Completo'
    get_nome_completo.admin_order_field = 'first_name'

    def tipo_badge(self, obj):
        """Retorna o tipo com badge colorido"""
        colors = {
            'ADMIN': '#dc3545',  # Vermelho
            'TUTOR': '#28a745',  # Verde
            'TUTORADO': '#007bff'  # Azul
        }
        color = colors.get(obj.tipo, '#6c757d')
        icon = obj.get_tipo_display_icon()

        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">'
            '{} {}</span>',
            color, icon, obj.get_tipo_display()
        )

    tipo_badge.short_description = 'Tipo'
    tipo_badge.admin_order_field = 'tipo'

    def ativar_usuarios(self, request, queryset):
        """Ação para ativar usuários selecionados"""
        updated = queryset.update(is_active=True, ativo=True)
        self.message_user(
            request,
            f'{updated} usuário(s) foram ativados com sucesso.'
        )

    ativar_usuarios.short_description = "Ativar usuários selecionados"

    def desativar_usuarios(self, request, queryset):
        """Ação para desativar usuários selecionados"""
        updated = queryset.update(is_active=False, ativo=False)
        self.message_user(
            request,
            f'{updated} usuário(s) foram desativados com sucesso.'
        )

    desativar_usuarios.short_description = "Desativar usuários selecionados"

    def get_queryset(self, request):
        """Otimiza consultas no admin"""
        return super().get_queryset(request).select_related()


@admin.register(PerfilTutor)
class PerfilTutorAdmin(admin.ModelAdmin):
    list_display = [
        'usuario',
        'especialidade',
        'max_tutorados',
        'get_tutorados_count'
    ]

    list_filter = ['especialidade']
    search_fields = [
        'usuario__first_name',
        'usuario__last_name',
        'especialidade'
    ]

    raw_id_fields = ['usuario']

    fieldsets = (
        ('Informações do Tutor', {
            'fields': ('usuario', 'especialidade', 'experiencia')
        }),
        ('Disponibilidade', {
            'fields': ('disponibilidade', 'max_tutorados')
        }),
    )

    def get_tutorados_count(self, obj):
        """Retorna o número atual de tutorados"""
        # TODO: Implementar quando criar o modelo de relacionamento
        return 0

    get_tutorados_count.short_description = 'Tutorados Atuais'


@admin.register(PerfilTutorado)
class PerfilTutoradoAdmin(admin.ModelAdmin):
    list_display = [
        'usuario',
        'escola',
        'turno_escolar',
        'responsavel_nome'
    ]

    list_filter = ['turno_escolar']
    search_fields = [
        'usuario__first_name',
        'usuario__last_name',
        'escola',
        'responsavel_nome'
    ]

    raw_id_fields = ['usuario']

    fieldsets = (
        ('Informações do Tutorado', {
            'fields': ('usuario', 'escola', 'turno_escolar')
        }),
        ('Responsável', {
            'fields': ('responsavel_nome', 'responsavel_telefone')
        }),
        ('Objetivos', {
            'fields': ('objetivo_principal',)
        }),
    )


# Configurações adicionais do admin
admin.site.site_header = "Salvaguarda - Administração"
admin.site.site_title = "Salvaguarda Admin"
admin.site.index_title = "Painel de Administração"
