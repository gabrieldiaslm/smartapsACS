from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from datetime import date

# 1. Usuário (ACS)
class UsuarioACS(AbstractUser):
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
    cpf = models.CharField("CPF", max_length=14, unique=True, null=True, blank=True)
    cns = models.CharField("CNS", max_length=15, unique=True)
    localidade = models.CharField(max_length=100)
    nome_mae = models.CharField("Nome da Mãe", max_length=200)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    
    # Audit
    criado_em = models.DateTimeField(auto_now_add=True)
    cadastrado_por = models.ForeignKey(UsuarioACS, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['nome']
        indexes = [
            models.Index(fields=['nome']),
            models.Index(fields=['data_nascimento']),
            models.Index(fields=['sexo']),
            models.Index(fields=['cns']),
        ]

    @property
    def idade_em_meses(self):
        hoje = date.today()
        meses = (hoje.year - self.data_nascimento.year) * 12 + (hoje.month - self.data_nascimento.month)
        return meses

    def verificar_atrasos(self):
        hoje = date.today()
        idade_meses = (hoje.year - self.data_nascimento.year) * 12 + (hoje.month - self.data_nascimento.month)
        
        registros_pendentes = self.registros.filter(status='PENDENTE')
        
        for registro in registros_pendentes:
            if idade_meses > registro.vacina.idade_alvo_meses:
                registro.status = 'ATRASADA'
                registro.save()
    
    @property
    def status_geral(self):
        if self.registros.filter(status='ATRASADA').exists():
            return 'ATRASADO'
        return 'EM_DIA'
    
    @property
    def idade_formatada(self):
        total_meses = self.idade_em_meses
        if total_meses < 12:
            return f"{total_meses} meses"
        
        anos = total_meses // 12
        meses_restantes = total_meses % 12
        
        if meses_restantes == 0:
            return "1 ano" if anos == 1 else f"{anos} anos"
        
        msg_anos = "1 ano" if anos == 1 else f"{anos} anos"
        msg_meses = "1 mês" if meses_restantes == 1 else f"{meses_restantes} meses"
        
        return f"{msg_anos} e {msg_meses}"

    def __str__(self):
        return f"{self.nome} ({self.data_nascimento})"

# 3. Definição da Vacina
class Vacina(models.Model):
    nome = models.CharField(max_length=100)
    descricao_doenca = models.CharField("Previne que doença", max_length=200)
    idade_alvo_meses = models.IntegerField("Idade Alvo (meses)", help_text="0 para ao nascer")
    dose_padrao = models.CharField("Dose Padrão", max_length=50, default="Dose Única")
    
    class Meta:
        ordering = ['idade_alvo_meses', 'nome']

    def __str__(self):
        meses = f"{self.idade_alvo_meses} meses" if self.idade_alvo_meses > 0 else "Ao nascer"
        return f"{self.nome} - {self.dose_padrao}"
    
    @property
    def idade_formatada(self):
        if self.idade_alvo_meses == 0:
            return "Ao Nascer"
        if self.idade_alvo_meses < 12:
            return f"{self.idade_alvo_meses} Meses"
        
        anos = self.idade_alvo_meses // 12
        meses_restantes = self.idade_alvo_meses % 12
        texto_anos = "Ano" if anos == 1 else "Anos"
        
        if meses_restantes == 0:
            return f"{anos} {texto_anos}"
        else:
            return f"{anos} {texto_anos} e {meses_restantes} Meses"

# 4. Cartão de Vacina (O Registro da Aplicação)
class RegistroVacina(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Em Aberto'),
        ('ATRASADA', 'Atrasada'),
        ('APLICADA', 'Aplicada'),
    ]
    
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
        ('DELTOIDE_D', 'Deltoide Direito (Braço)'),
        ('DELTOIDE_E', 'Deltoide Esquerdo (Braço)'),
        ('VASTO_LATERAL_D', 'Vasto Lateral da Coxa D'),
        ('VASTO_LATERAL_E', 'Vasto Lateral da Coxa E'),
        ('GLUTEO_D', 'Glúteo (Dorso-Glúteo)'),
        ('BOCA', 'Boca (Oral)'),
        ('OUTROS', 'Outros'),
    ]

    # --- CAMPOS (Atualize os defaults para MAIÚSCULO) ---
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    
    estrategia = models.CharField(max_length=50, choices=ESTRATEGIAS, default='ROTINA')
    
    via_administracao = models.CharField(max_length=50, choices=VIAS, default='INTRAMUSCULAR')
    
    local_aplicacao = models.CharField(max_length=50, choices=LOCAIS, blank=True, null=True)

    # --- RELACIONAMENTOS ---
    crianca = models.ForeignKey(Crianca, on_delete=models.CASCADE, related_name='registros') 
    vacina = models.ForeignKey(Vacina, on_delete=models.CASCADE)
    aplicado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='vacinas_aplicadas'
    )

    # --- CAMPOS DE DADOS ---
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    dose = models.CharField(max_length=50, blank=True, null=True) # Ex: 1ª Dose
    data_aplicacao = models.DateField(blank=True, null=True)
    
    # Detalhes Clínicos
    estrategia = models.CharField(max_length=50, choices=ESTRATEGIAS, default='Rotina')
    via_administracao = models.CharField(max_length=50, choices=VIAS, default='Intramuscular')
    local_aplicacao = models.CharField(max_length=50, choices=LOCAIS, blank=True, null=True)
    
    # Rastreabilidade
    lote = models.CharField(max_length=50, blank=True, null=True)
    fabricante = models.CharField(max_length=100, blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    profissional_aplicou = models.CharField(max_length=100, blank=True, null=True) # Texto livre caso não seja o usuário logado

    class Meta:
        indexes = [
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.vacina.nome} - {self.crianca.nome}"

# 5. Lote de Vacina (Estoque/Disponível)
class LoteVacina(models.Model):
    vacina = models.ForeignKey(Vacina, on_delete=models.CASCADE, related_name='lotes')
    numero_lote = models.CharField(max_length=50)
    fabricante = models.CharField(max_length=100)
    quantidade_disponivel = models.IntegerField(default=0)
    validade = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.vacina.nome} - Lote: {self.numero_lote} ({self.fabricante})"

    class Meta:
        verbose_name = "Lote Disponível"
        verbose_name_plural = "Lotes Disponíveis"