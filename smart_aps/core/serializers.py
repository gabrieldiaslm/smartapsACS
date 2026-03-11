from rest_framework import serializers
from .models import Crianca, RegistroVacina, Vacina

class RegistroVacinaSerializer(serializers.ModelSerializer):
    nome_vacina = serializers.CharField(source='vacina.nome', read_only=True)
    idade_alvo = serializers.IntegerField(source='vacina.idade_alvo_meses', read_only=True)
    dose = serializers.CharField(source='vacina.dose_padrao', read_only=True)
    vacina_id = serializers.IntegerField(source='vacina.id', read_only=True)

    class Meta:
        model = RegistroVacina
        fields = [
            'id', 
            'vacina_id', 
            'nome_vacina', 
            'idade_alvo', 
            'status', 
            'data_aplicacao', 
            'dose', 
            'lote', 
            'fabricante', 
            'observacoes',
            'estrategia',       
            'via_administracao', 
            'local_aplicacao' 
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

class CriancaListSerializer(serializers.ModelSerializer):
    """
    Serializador super leve usado APENAS para as listas (Censo e Controle).
    Ele ignora o histórico de vacinas para a página carregar instantaneamente.
    """
    class Meta:
        model = Crianca
        fields = [
            'id', 
            'nome', 
            'localidade', 
            'cns', 
            'nome_mae', 
            'sexo', 
            'idade_formatada', 
            'status_geral'
        ]

class VacinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacina
        fields = ['id', 'nome', 'descricao_doenca', 'idade_alvo_meses', 'dose_padrao']