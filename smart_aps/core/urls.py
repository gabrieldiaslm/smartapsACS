from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
# Importar tudo de views de uma vez só facilita
from core import views 
from core.views import CriancaViewSet, RegistroVacinaViewSet

# Configuração do Router da API
router = DefaultRouter()
router.register(r'criancas', CriancaViewSet, basename='crianca')
router.register(r'registros', RegistroVacinaViewSet, basename='registro')
router.register(r'vacinas-guia', views.VacinaViewSet, basename='vacinas-guia')

urlpatterns = [
    # Rota administrativa
    path('admin/', admin.site.urls),

    # Rotas do Site (HTML)
    path('', views.index, name='index'),
    path('criancas/', views.lista_criancas, name='lista_criancas'),
    path('crianca/nova/', views.cadastrar_crianca, name='cadastrar_crianca'),
    path('crianca/<int:crianca_id>/cartao/', views.cartao_vacina, name='cartao_vacina'),
    path('vacina/<int:registro_id>/editar/', views.editar_registro, name='editar_registro'),
    path('calendario-guia/', views.calendario_guia, name='calendario_guia'),
    path('censo/', views.censo_demografico, name='censo_demografico'),
    
    # Rotas de Gestão
    path('gestao/novo-acs/', views.cadastrar_acs, name='cadastrar_acs'),
    path('gestao/equipe/', views.lista_usuarios, name='lista_usuarios'),
    
    # Rota PWA Offline
    path('offline/', views.offline_view, name='offline'),
    
    # ROTA DA API (O endereço será: http://localhost:8000/api/criancas/)
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # NOVA ROTA: React vai chamar aqui para pegar os lotes da vacina X
    path('api/vacinas/<int:vacina_id>/lotes/', views.api_lotes_por_vacina, name='api_lotes_por_vacina'),
    path('api/', include(router.urls)),
    path('api/usuario/me/', views.usuario_atual, name='usuario_atual'),
    

]