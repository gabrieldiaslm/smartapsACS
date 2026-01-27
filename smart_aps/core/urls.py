# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('criancas/', views.lista_criancas, name='lista_criancas'), # Nova rota
    path('crianca/nova/', views.cadastrar_crianca, name='cadastrar_crianca'),
    path('crianca/<int:crianca_id>/cartao/', views.cartao_vacina, name='cartao_vacina'),
    path('vacina/<int:registro_id>/editar/', views.editar_registro, name='editar_registro'),
    path('calendario-guia/', views.calendario_guia, name='calendario_guia'),
    path('censo/', views.censo_demografico, name='censo_demografico'), # Card 4 (Relatório/Planilha)
    path('gestao/novo-acs/', views.cadastrar_acs, name='cadastrar_acs'),

]