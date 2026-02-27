from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UsuarioACS, Crianca, Vacina, RegistroVacina, LoteVacina

# Registra o Usuário personalizado
admin.site.register(UsuarioACS, UserAdmin)

# Registra a Criança
@admin.register(Crianca)
class CriancaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'data_nascimento', 'nome_mae', 'cns')
    search_fields = ('nome', 'cpf', 'cns')

# Registra a Vacina (O Guia)
@admin.register(Vacina)
class VacinaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'dose_padrao', 'idade_alvo_meses')
    ordering = ('idade_alvo_meses', 'nome')

# Registra o Histórico de Vacinação
@admin.register(RegistroVacina)
class RegistroVacinaAdmin(admin.ModelAdmin):
    list_display = ('crianca', 'vacina', 'status', 'data_aplicacao')
    list_filter = ('status', 'vacina')

@admin.register(LoteVacina)
class LoteVacinaAdmin(admin.ModelAdmin):
    list_display = ('vacina', 'numero_lote', 'fabricante', 'quantidade_frascos', 'doses_por_frasco', 'quantidade_disponivel')
    
    # Faz com que o campo de total disponível não possa ser editado manualmente,
    # forçando o usuário a usar a lógica dos frascos x doses.
    readonly_fields = ('quantidade_disponivel',)