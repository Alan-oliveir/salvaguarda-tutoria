from django import forms
from django.contrib.auth import get_user_model

from usuarios.models import PerfilTutorado
from .models import Tarefa

User = get_user_model()


class TarefaForm(forms.ModelForm):
    class Meta:
        model = Tarefa
        fields = ['tutorado', 'categoria', 'titulo', 'descricao', 'data_limite', 'link_externo']
        widgets = {
            'data_limite': forms.DateInput(attrs={'type': 'date'}),
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.tutor = kwargs.pop('tutor', None)
        super().__init__(*args, **kwargs)

        # Injeta as classes CSS do forms.css
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        self.fields['link_externo'].widget.attrs['placeholder'] = 'https://... (Opcional)'
        self.fields['titulo'].widget.attrs['placeholder'] = 'Ex: Fazer lista de redação do mês'

        # Filtra para mostrar APENAS os tutorados vinculados a este tutor
        if self.tutor:
            tutorados_ids = PerfilTutorado.objects.filter(tutor=self.tutor).values_list('usuario_id', flat=True)
            self.fields['tutorado'].queryset = User.objects.filter(id__in=tutorados_ids).order_by('first_name')
            self.fields['tutorado'].empty_label = "Selecione o tutorado..."
