from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.conf import settings

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

    class Meta:
        ordering = ['nome']
        # Cria "atalhos" para o banco de dados encontrar esses dados instantaneamente
        indexes = [
            models.Index(fields=['nome']),             # Usado na busca
            models.Index(fields=['data_nascimento']),  # Usado no Censo (cálculo de bebês)
            models.Index(fields=['sexo']),             # Usado no Censo (meninos/meninas)
            models.Index(fields=['cns']),              # Usado na busca
        ]

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
    
    @property
    def idade_formatada(self):
        """
        Converte meses em 'Anos' ou 'Anos e Meses'.
        Ex: 15 meses -> 1 Ano e 3 Meses
        Ex: 114 meses -> 9 Anos e 6 Meses
        """
        if self.idade_alvo_meses == 0:
            return "Ao Nascer"
        
        # Se for menos de 1 ano (ex: 2, 4, 9 meses), mantém meses
        if self.idade_alvo_meses < 12:
            return f"{self.idade_alvo_meses} Meses"
        
        # Calcula Anos e Meses restantes
        anos = self.idade_alvo_meses // 12
        meses_restantes = self.idade_alvo_meses % 12
        
        # Define singular ou plural para "Ano"
        texto_anos = "Ano" if anos == 1 else "Anos"
        
        # Lógica de Exibição
        if meses_restantes == 0:
            # Ex: 12, 24, 48 -> "1 Ano", "2 Anos"
            return f"{anos} {texto_anos}"
        else:
            # Ex: 15, 114 -> "1 Ano e 3 Meses", "9 Anos e 6 Meses"
            return f"{anos} {texto_anos} e {meses_restantes} Meses"

# 4. Cartão de Vacina (O Registro da Aplicação)
class RegistroVacina(models.Model):
    lote = models.CharField(max_length=50, blank=True, null=True) 
    observacao = models.TextField(blank=True, null=True)
    

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

    crianca = models.ForeignKey(Crianca, on_delete=models.CASCADE, related_name='registros') 
    
    vacina = models.ForeignKey(Vacina, on_delete=models.CASCADE)
    
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

    class Meta:
        indexes = [
            models.Index(fields=['status']), # Muito usado para contar atrasos
        ]
    
    # NOVO CAMPO:
    aplicado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Aponta para o seu UsuarioACS
        on_delete=models.SET_NULL, # Se o usuário for demitido/deletado, o registro fica mas sem nome
        null=True, 
        blank=True,
        related_name='vacinas_aplicadas'
    )

    # --- OPÇÕES DOS DROPDOWNS ---
    ESTRATEGIAS = [
        ('ROTINA', 'Rotina'),
        ('CAMPANHA', 'Campanha'),
        ('BLOQUEIO', 'Bloqueio'),
        ('ESPECIAL', 'Especial'),
    ]

    VIAS = [
        ('INTRAMUSCULAR', 'Intramuscular'),
        ('ORAL', 'Oral'),
        ('SUBCUTANEA', 'Subcutânea'),
        ('INTRADERMICA', 'Intradérmica'),
    ]

    LOCAIS = [
        ('VASTO_LATERAL_D', 'Vasto Lateral Direito (Coxa)'),
        ('VASTO_LATERAL_E', 'Vasto Lateral Esquerdo (Coxa)'),
        ('DELTOIDE_D', 'Deltoide Direito (Braço)'),
        ('DELTOIDE_E', 'Deltoide Esquerdo (Braço)'),
        ('GLUTEO_D', 'Glúteo Direito'),
        ('GLUTEO_E', 'Glúteo Esquerdo'),
        ('BOCA', 'Boca (Oral)'),
        ('OUTROS', 'Outros'),
    ]

    # --- CAMPOS ---
    # O parametro 'choices' é o que transforma o campo em Dropdown no Admin e no Form padrão
    status = models.CharField(max_length=20, default='PENDENTE') # Vamos tratar isso no form
    estrategia = models.CharField(max_length=20, choices=ESTRATEGIAS, default='ROTINA')
    via_administracao = models.CharField(max_length=20, choices=VIAS, default='INTRAMUSCULAR')
    local_aplicacao = models.CharField(max_length=20, choices=LOCAIS, blank=True, null=True)
    
    # Campos de texto livre (não são dropdown)
    lote = models.CharField(max_length=50, blank=True, null=True)
    fabricante = models.CharField(max_length=50, blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    
    # Profissional (Será dropdown dinâmico no form)
    profissional_aplicou = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.vacina.nome} - {self.crianca.nome}"