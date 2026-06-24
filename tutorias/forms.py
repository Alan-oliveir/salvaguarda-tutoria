from django import forms

from .models import FichaDiagnostica


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
