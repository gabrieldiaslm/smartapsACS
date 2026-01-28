# atencao_primaria/forms.py
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
    # Criamos um campo de escolha explícito
    profissional_aplicou = forms.ChoiceField(
        label="Profissional que Aplicou",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = RegistroVacina
        # Adicione 'profissional_aplicou' na lista
        fields = ['status', 'data_aplicacao', 'lote', 'fabricante', 'profissional_aplicou', 'observacoes']
        
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'data_aplicacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'lote': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Lote 1234'}),
            'fabricante': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Fiocruz/Butantan'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'status': 'Situação / Status',
            'data_aplicacao': 'Data da Aplicação',
            'lote': 'Lote',
            'fabricante': 'Laboratório / Fabricante',
            'observacoes': 'Observações (Opcional)',
        }

    def __init__(self, *args, **kwargs):
        super(RegistroVacinaForm, self).__init__(*args, **kwargs)
        
        # 1. Data Padrão
        if not self.initial.get('data_aplicacao'):
            self.initial['data_aplicacao'] = date.today()

        # 2. POPULAR A LISTA DE PROFISSIONAIS (DINÂMICO)
        # Busca todos os usuários cadastrados
        usuarios = UsuarioACS.objects.all().order_by('first_name')
        
        lista_profissionais = []
        for u in usuarios:
            # Monta o nome: "Maria Silva" ou usa o username "maria.acs" se não tiver nome
            nome_completo = f"{u.first_name} {u.last_name}".strip()
            if not nome_completo:
                nome_completo = u.username
            
            # Tupla: (Valor_que_salva_no_banco, Texto_que_aparece_na_tela)
            lista_profissionais.append((nome_completo, nome_completo))
            
        self.fields['profissional_aplicou'].choices = lista_profissionais

        # 3. Campos Obrigatórios
        self.fields['data_aplicacao'].required = True
        self.fields['lote'].required = True
        self.fields['fabricante'].required = True
        self.fields['observacoes'].required = False