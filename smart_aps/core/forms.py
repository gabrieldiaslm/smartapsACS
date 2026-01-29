from django import forms
from .models import Crianca, RegistroVacina, UsuarioACS
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

# --- NOVO FORMULÁRIO ESPECÍFICO PARA APLICAÇÃO ---
class RegistroVacinaForm(forms.ModelForm):

    # Mantemos a correção do Status para garantir as opções
    status = forms.ChoiceField(
        label="Situação / Status",
        choices=[
            ('PENDENTE', 'Pendente'),
            ('APLICADA', 'Aplicada'),
            ('ATRASADA', 'Atrasada'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = RegistroVacina
        fields = [
            'status', 'estrategia', 'data_aplicacao', 'via_administracao', 
            'local_aplicacao', 'lote', 'fabricante', 'observacoes'
        ]
        
        widgets = {
            'estrategia': forms.Select(attrs={'class': 'form-select'}),
            'via_administracao': forms.Select(attrs={'class': 'form-select'}),
            'local_aplicacao': forms.Select(attrs={'class': 'form-select'}),
            'data_aplicacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'lote': forms.Select(attrs={'class': 'form-select', 'id': 'id_lote'}),
            'fabricante': forms.Select(attrs={'class': 'form-select', 'id': 'id_fabricante'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
        labels = {
            'estrategia': 'Estratégia',
            'via_administracao': 'Via de Administração',
            'local_aplicacao': 'Local de Aplicação',
            'data_aplicacao': 'Data da Aplicação',
            'lote': 'Lote',
            'fabricante': 'Laboratório / Fabricante',
            'observacoes': 'Observações (Opcional)',
        }

    def __init__(self, *args, **kwargs):
        super(RegistroVacinaForm, self).__init__(*args, **kwargs)
        
        # Data padrão: Hoje
        if not self.initial.get('data_aplicacao'):
            self.initial['data_aplicacao'] = date.today()

        # Obrigatórios
        self.fields['data_aplicacao'].required = True
        self.fields['lote'].required = True
        self.fields['fabricante'].required = True
        self.fields['estrategia'].required = True
        self.fields['via_administracao'].required = True
        self.fields['local_aplicacao'].required = True
        self.fields['observacoes'].required = False

        # Isso evita erro de validação do Django dizendo "Opção inválida"
        # pois o Select tecnicamente está vazio no Python, mas cheio no HTML
        self.fields['lote'].widget.choices = [] 
        self.fields['fabricante'].widget.choices = []
        
        # Truque: Se já tiver dados (edição), preenche as opções iniciais
        if self.instance.pk:
            self.fields['lote'].widget.choices = [(self.instance.lote, self.instance.lote)]
            self.fields['fabricante'].widget.choices = [(self.instance.fabricante, self.instance.fabricante)]