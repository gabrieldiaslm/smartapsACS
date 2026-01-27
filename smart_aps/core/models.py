from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

# 1. Usuário (ACS)
# Usaremos o sistema de auth padrão do Django, mas podemos estender se precisar de mais dados do ACS (como número da equipe).
class UsuarioACS(AbstractUser):
    # O AbstractUser já possui username, first_name, email e password.
    # Podemos adicionar campos específicos do ACS se necessário.
    cnes_unidade = models.CharField("CNES da Unidade", max_length=20, blank=True)

    class Meta:
        verbose_name = "Agente Comunitário de Saúde"
        verbose_name_plural = "Agentes Comunitários de Saúde"

# 2. Criança (Paciente)
class Crianca(models.Model):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
    ]

    nome = models.CharField(max_length=200)
    data_nascimento = models.DateField()
    cpf = models.CharField("CPF", max_length=14, unique=True) # Sugestão: usar lib django-localflavor-br depois
    cns = models.CharField("CNS", max_length=15, unique=True)
    localidade = models.CharField(max_length=100)
    nome_mae = models.CharField("Nome da Mãe", max_length=200)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    
    # Audit
    criado_em = models.DateTimeField(auto_now_add=True)
    cadastrado_por = models.ForeignKey(UsuarioACS, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.nome} ({self.data_nascimento})"

# 3. Definição da Vacina (Para o Calendário Vacinal)
class Vacina(models.Model):
    nome = models.CharField(max_length=100) # Ex: BCG, Pentavalente
    descricao_doenca = models.CharField("Previne que doença", max_length=200)
    idade_alvo_meses = models.IntegerField("Idade Alvo (meses)", help_text="0 para ao nascer")
    dose_padrao = models.CharField("Dose Padrão", max_length=50, default="Dose Única")
    
    class Meta:
        ordering = ['idade_alvo_meses', 'nome'] # Garante a ordem do calendário

    def __str__(self):
        meses = f"{self.idade_alvo_meses} meses" if self.idade_alvo_meses > 0 else "Ao nascer"
        return f"{self.nome} - {self.dose_padrao}"

# 4. Cartão de Vacina (O Registro da Aplicação)
class RegistroVacina(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Em Aberto'),
        ('ATRASADA', 'Atrasada'), # Isso pode ser calculado dinamicamente também
        ('APLICADA', 'Aplicada'),
    ]
    
    VIA_CHOICES = [
        ('INTRAMUSCULAR', 'Intramuscular'),
        ('SUBCUTANEA', 'Subcutânea'),
        ('ORAL', 'Oral'),
        ('INTRADERMICA', 'Intradérmica'),
    ]

    crianca = models.ForeignKey(Crianca, on_delete=models.CASCADE, related_name='vacinas')
    vacina = models.ForeignKey(Vacina, on_delete=models.PROTECT)
    
    # Detalhes da aplicação
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    dose = models.CharField(max_length=50) # Ex: 1ª Dose, Reforço
    lote = models.CharField(max_length=50, blank=True)
    fabricante = models.CharField(max_length=100, blank=True)
    observacoes = models.TextField(blank=True, null=True)
    profissional_aplicou = models.CharField(max_length=100, blank=True)
    data_aplicacao = models.DateField(blank=True, null=True)
    
    via_administracao = models.CharField(max_length=30, choices=VIA_CHOICES, blank=True)
    local_aplicacao = models.CharField(max_length=100, blank=True) # Ex: Deltoide direito
    estrategia = models.CharField(max_length=100, default="Rotina") # Rotina ou Campanha

    def __str__(self):
        return f"{self.vacina.nome} - {self.crianca.nome}"