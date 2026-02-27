from django import forms
from .models import Crianca, LoteVacina, RegistroVacina, UsuarioACS
from django.contrib.auth.forms import UserCreationForm
from datetime import date

class UsuarioACSForm(UserCreationForm):
    class Meta:
        model = UsuarioACS
        fields = ['username', 'first_name', 'email', 'cnes_unidade']

class CriancaForm(forms.ModelForm):
    class Meta:
        model = Crianca
        fields = ['nome', 'data_nascimento', 'cpf', 'cns', 'localidade', 'nome_mae', 'sexo']
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'cns': forms.TextInput(attrs={'class': 'form-control'}),
            'localidade': forms.TextInput(attrs={'class': 'form-control'}),
            'nome_mae': forms.TextInput(attrs={'class': 'form-control'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
        }

# Form pra aplicação
class RegistroVacinaForm(forms.ModelForm):

    class Meta:
        model = RegistroVacina
        fields = [
            'status', 'eh_transcricao', 'estrategia', 'data_aplicacao', 
            'via_administracao', 'local_aplicacao', 
            'lote_vinculado', 'lote', 'fabricante', 'observacoes'
        ]
        
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            # Checkbox estilizado como "Switch" do Bootstrap (fica bem profissional)
            'eh_transcricao': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_eh_transcricao', 'role': 'switch'}),
            'estrategia': forms.Select(attrs={'class': 'form-select'}),
            'via_administracao': forms.Select(attrs={'class': 'form-select'}),
            'local_aplicacao': forms.Select(attrs={'class': 'form-select'}),
            'data_aplicacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            
            # Select inteligente que virá do banco de dados
            'lote_vinculado': forms.Select(attrs={'class': 'form-select', 'id': 'id_lote_vinculado'}),
            
            # Textos livres (usados apenas quando eh_transcricao for verdadeiro)
            'lote': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_lote_texto'}),
            'fabricante': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_fabricante_texto'}),
            
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

        labels = {
            'eh_transcricao': 'Registrar como Transcrição (Vacina de fora/anterior)',
            'lote_vinculado': 'Selecione o Lote do Estoque da UBS',
            'lote': 'Lote (Texto livre)',
            'fabricante': 'Fabricante (Texto livre)',
        }

    def __init__(self, *args, **kwargs):
        super(RegistroVacinaForm, self).__init__(*args, **kwargs)
        
        if not self.initial.get('data_aplicacao'):
            self.initial['data_aplicacao'] = date.today()

        self.fields['data_aplicacao'].required = True
        self.fields['estrategia'].required = True
        self.fields['via_administracao'].required = True
        self.fields['local_aplicacao'].required = True
        
        # Como o preenchimento depende do usuário (transcrição ou estoque),
        # não podemos forçar required no backend. Faremos isso via JavaScript.
        self.fields['lote_vinculado'].required = False
        self.fields['lote'].required = False
        self.fields['fabricante'].required = False

        # --- O PULO DO GATO ---
        # Filtra os lotes para mostrar SÓ os lotes dessa vacina que têm estoque!
        if self.instance and hasattr(self.instance, 'vacina') and self.instance.vacina:
            self.fields['lote_vinculado'].queryset = LoteVacina.objects.filter(
                vacina=self.instance.vacina, 
                quantidade_disponivel__gt=0
            )
            # Define o texto vazio padrão
            self.fields['lote_vinculado'].empty_label = "Selecione o Lote da Geladeira..."