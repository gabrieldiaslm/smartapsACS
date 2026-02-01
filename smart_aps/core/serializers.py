from rest_framework import serializers
from .models import Crianca, RegistroVacina

class RegistroVacinaSerializer(serializers.ModelSerializer):
    nome_vacina = serializers.CharField(source='vacina.nome', read_only=True)
    idade_alvo = serializers.IntegerField(source='vacina.idade_alvo_meses', read_only=True)
    dose = serializers.CharField(source='vacina.dose_padrao', read_only=True)
    
    # --- ESTA LINHA É O SEGREDO ---
    # Sem isso, o React não sabe qual vacina buscar os lotes!
    vacina_id = serializers.IntegerField(source='vacina.id', read_only=True)

    class Meta:
        model = RegistroVacina
        fields = [
            'id', 
            'vacina_id', # <--- Verifique se adicionou aqui na lista!
            'nome_vacina', 
            'idade_alvo', 
            'status', 
            'data_aplicacao', 
            'dose', 
            'lote', 
            'fabricante', 
            'observacoes',
            'estrategia',       # Adicionado para bater com o novo Model
            'via_administracao', # Adicionado
            'local_aplicacao'    # Adicionado
        ]

class CriancaSerializer(serializers.ModelSerializer):
    idade_formatada = serializers.ReadOnlyField()
    status_geral = serializers.ReadOnlyField()
    registros = RegistroVacinaSerializer(many=True, read_only=True)

    class Meta:
        model = Crianca
        fields = [
            'id', 'nome', 'data_nascimento', 'sexo', 'cns', 
            'localidade', 'nome_mae', 'idade_formatada', 
            'status_geral', 'registros'
        ]