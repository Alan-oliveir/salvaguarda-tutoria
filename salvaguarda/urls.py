"""
URL configuration for salvaguarda project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
                path('', RedirectView.as_view(url='/usuarios/', permanent=False)),
                path('admin/', admin.site.urls),
                path('usuarios/', include('usuarios.urls')),
                path('tutorados/', include('tutorias.urls')),
                path('materiais/', include('materiais.urls')),
                path('tarefas/', include('tarefas.urls')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
