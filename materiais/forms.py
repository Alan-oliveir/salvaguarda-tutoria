from django import forms
from django.contrib.auth import get_user_model

from usuarios.models import PerfilTutorado
from .models import Material

User = get_user_model()


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['tipo', 'titulo', 'descricao', 'arquivo', 'url', 'tutorado']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        # Deixa o select de tipo e título mais amigáveis
        self.fields['titulo'].widget.attrs['placeholder'] = 'Ex: Lista de Equações do 2º Grau'
        self.fields['url'].widget.attrs['placeholder'] = 'https://...'

        if self.user:
            if self.user.tipo == 'TUTORADO':
                # Tutorado não precisa escolher o destinatário
                self.fields['tutorado'].widget = forms.HiddenInput()
                self.fields['tutorado'].required = False
            elif self.user.tipo == 'TUTOR':
                # Tutor só pode enviar materiais para os seus próprios tutorados
                tutorados_ids = PerfilTutorado.objects.filter(tutor=self.user).values_list('usuario_id', flat=True)
                self.fields['tutorado'].queryset = User.objects.filter(id__in=tutorados_ids).order_by('first_name')
                self.fields['tutorado'].empty_label = "Selecione o tutorado..."
