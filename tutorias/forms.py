from django import forms

from .models import FichaDiagnostica, AtividadeExtra


class FichaDiagnosticaForm(forms.ModelForm):
    class Meta:
        model = FichaDiagnostica
        exclude = ['tutorado', 'tutor']
        widgets = {
            'maiores_dificuldades': forms.Textarea(attrs={'rows': 3, 'class': 'form-control',
                                                          'placeholder': 'Descreva as principais barreiras notadas...'}),
            'pontos_positivos': forms.Textarea(
                attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Descreva as facilidades e qualidades...'}),
            'comentarios_extras': forms.Textarea(
                attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Demandas que fugiram das opções acima...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Transforma os campos de nível (Excelente a Nulo) em Radio Buttons
        for field_name, field in self.fields.items():
            if field_name.startswith(('info_', 'org_')):
                field.widget = forms.RadioSelect(choices=field.choices)


class AtividadeExtraForm(forms.ModelForm):
    class Meta:
        model = AtividadeExtra
        fields = ['data', 'tutorado', 'descricao', 'duracao_minutos']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'duracao_minutos': forms.NumberInput(attrs={'placeholder': 'Ex: 90 (para 1h30)'}),
            'descricao': forms.TextInput(attrs={'placeholder': 'Ex: Leitura do manual, preparação de cronograma...'}),
        }

    def __init__(self, *args, **kwargs):
        self.tutor = kwargs.pop('tutor', None)
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        self.fields['tutorado'].empty_label = "Geral (Não vinculado a um aluno específico)"
        self.fields['tutorado'].required = False

        # Filtra para mostrar APENAS os tutorados deste tutor logado
        if self.tutor:
            from usuarios.models import PerfilTutorado
            from django.contrib.auth import get_user_model
            User = get_user_model()
            tutorados_ids = PerfilTutorado.objects.filter(tutor=self.tutor).values_list('usuario_id', flat=True)
            self.fields['tutorado'].queryset = User.objects.filter(id__in=tutorados_ids).order_by('first_name')
