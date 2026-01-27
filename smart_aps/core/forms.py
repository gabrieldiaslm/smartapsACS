# atencao_primaria/forms.py
from django import forms
from .models import Crianca, RegistroVacina, UsuarioACS
from django.contrib.auth.forms import UserCreationForm

class UsuarioACSForm(UserCreationForm):
    class Meta:
        model = UsuarioACS
        # Campos que o admin vai preencher
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

class RegistroVacinaForm(forms.ModelForm):
    class Meta:
        model = RegistroVacina
        fields = ['status', 'data_aplicacao', 'lote', 'fabricante', 'profissional_aplicou', 'observacoes']
        widgets = {
            'data_aplicacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'lote': forms.TextInput(attrs={'class': 'form-control'}),
            'fabricante': forms.TextInput(attrs={'class': 'form-control'}),
            'profissional_aplicou': forms.TextInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }