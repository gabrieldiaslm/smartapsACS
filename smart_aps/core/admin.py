from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UsuarioACS, Crianca, Vacina, RegistroVacina, LoteVacina

# 1. Registra o Usuário personalizado
admin.site.register(UsuarioACS, UserAdmin)

# 2. Registra a Criança
@admin.register(Crianca)
class CriancaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'data_nascimento', 'nome_mae', 'cns')
    search_fields = ('nome', 'cpf', 'cns')

# 3. Registra a Vacina (O Guia)
@admin.register(Vacina)
class VacinaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'dose_padrao', 'idade_alvo_meses')
    ordering = ('idade_alvo_meses', 'nome')

# 4. Registra o Histórico de Vacinação
@admin.register(RegistroVacina)
class RegistroVacinaAdmin(admin.ModelAdmin):
    list_display = ('crianca', 'vacina', 'status', 'data_aplicacao')
    list_filter = ('status', 'vacina')

@admin.register(LoteVacina)
class LoteVacinaAdmin(admin.ModelAdmin):
    # Colunas que aparecem na tabela
    list_display = ('vacina', 'numero_lote', 'fabricante', 'validade', 'quantidade_disponivel')
    
    # Campos que permitem busca (Lupa)
    search_fields = ('numero_lote', 'fabricante', 'vacina__nome')
    
    # Filtros laterais
    list_filter = ('fabricante', 'vacina')
    
    # Ordenação padrão (por vacina e depois validade)
    ordering = ('vacina', 'validade')