# tutorias/migrations/0001_initial.py
# Gerada automaticamente — rode: python manage.py makemigrations tutorias

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tutorado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('foto', models.ImageField(blank=True, null=True, upload_to='fotos_tutorados/')),
                ('estado', models.CharField(blank=True, max_length=50)),
                ('cidade', models.CharField(blank=True, max_length=50)),
                ('serie', models.CharField(choices=[('1EM', '1º Ano do Ensino Médio'), ('2EM', '2º Ano do Ensino Médio'), ('3EM', '3º Ano do Ensino Médio'), ('FORM', 'Já formado / Cursinho')], default='3EM', max_length=4)),
                ('idade', models.PositiveIntegerField(blank=True, null=True)),
                ('fez_enem', models.BooleanField(default=False)),
                ('cursos_interesse', models.TextField(blank=True)),
                ('whatsapp', models.CharField(blank=True, max_length=20)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('token', models.CharField(blank=True, max_length=16, unique=True)),
                ('criado_em', models.DateField(auto_now_add=True)),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tutorados', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Tutorado', 'verbose_name_plural': 'Tutorados', 'ordering': ['nome']},
        ),
        migrations.CreateModel(
            name='Reuniao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField()),
                ('horario', models.TimeField()),
                ('link', models.URLField(blank=True, help_text='Link do Google Meet, Zoom, etc.')),
                ('topicos', models.TextField(blank=True)),
                ('duracao_minutos', models.PositiveIntegerField(default=60)),
                ('observacoes', models.TextField(blank=True)),
                ('presenca', models.BooleanField(default=False)),
                ('materia', models.CharField(choices=[('MAT', 'Matemática'), ('POR', 'Português / Redação'), ('CIE', 'Ciências da Natureza'), ('HUM', 'Ciências Humanas'), ('LIN', 'Linguagens'), ('GER', 'Geral / Orientação')], default='GER', max_length=3)),
                ('tutorado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reunioes', to='tutorias.tutorado')),
            ],
            options={'verbose_name': 'Reunião', 'verbose_name_plural': 'Reuniões', 'ordering': ['-data', '-horario']},
        ),
    ]