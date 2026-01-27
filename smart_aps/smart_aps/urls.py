# smart_aps/urls.py (Principal)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')), # Aponta para o nosso app
    path('accounts/', include('django.contrib.auth.urls')), # Login/Logout padrão
]