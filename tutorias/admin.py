# tutorias/admin.py

from django.contrib import admin
from .models import Tutorado, Reuniao

admin.site.register(Tutorado)
admin.site.register(Reuniao)
