# smart_aps/urls.py (Principal)
from django.contrib import admin
from django.urls import path, include
from core.views import api_lotes_por_vacina

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')), # Aponta para o nosso app
    path('accounts/', include('django.contrib.auth.urls')), # Login/Logout padrão
    path('api/lotes/<int:vacina_id>/', api_lotes_por_vacina, name='api_lotes'),
    path('', include('pwa.urls')), # <--- O PWA assume as rotas de manifesto automaticamente
]