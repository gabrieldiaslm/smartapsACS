from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Crianca, Vacina, RegistroVacina
from .forms import CriancaForm, RegistroVacinaForm, UsuarioACSForm
from datetime import date, timedelta
from django.db.models import Count
from django.contrib import messages # Para dar feedback visual
from django.views.decorators.cache import never_cache
def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin) # Só deixa passar se eh_admin for True
def cadastrar_acs(request):
    """Card 5: Admin cria novo ACS"""
    if request.method == 'POST':
        form = UsuarioACSForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Novo Agente cadastrado com sucesso!')
            return redirect('index')
    else:
        form = UsuarioACSForm()
    
    return render(request, 'cadastro_acs.html', {'form': form})

@never_cache
@login_required
def index(request):
    """Tela Inicial: Dashboard com Estatísticas"""
    
    # 1. Total Geral
    total_criancas = Crianca.objects.count()
    
    # 2. Por Sexo (Agrupamento)
    # Retorna algo como: {'M': 15, 'F': 12}
    sexo_stats = Crianca.objects.values('sexo').annotate(total=Count('sexo'))
    sexo_dict = {item['sexo']: item['total'] for item in sexo_stats}
    
    # 3. Por Idade (Bebês < 1 ano vs Crianças >= 1 ano)
    # Data de corte: Hoje menos 365 dias
    um_ano_atras = date.today() - timedelta(days=365)
    
    # Menores de 1 ano (Nascidos DEPOIS da data de corte)
    bebes = Crianca.objects.filter(data_nascimento__gt=um_ano_atras).count()
    
    # Maiores de 1 ano
    maiores = total_criancas - bebes

    context = {
        'total': total_criancas,
        'meninos': sexo_dict.get('M', 0),
        'meninas': sexo_dict.get('F', 0),
        'bebes': bebes,
        'criancas_maiores': maiores,
    }
    
    return render(request, 'index.html', context)

@never_cache
@login_required
def lista_criancas(request):
    """Antiga tela inicial: Lista e Busca"""
    query = request.GET.get('busca')
    if query:
        criancas = Crianca.objects.filter(nome__icontains=query)
    else:
        criancas = Crianca.objects.all().order_by('-criado_em')[:20]
    
    return render(request, 'lista_criancas.html', {'criancas': criancas})

@never_cache
@login_required
def cadastrar_crianca(request):
    """Cadastrar Criança"""
    if request.method == 'POST':
        form = CriancaForm(request.POST)
        if form.is_valid():
            nova_crianca = form.save(commit=False)
            nova_crianca.cadastrado_por = request.user
            nova_crianca.save()
            
            # MAGIA: Ao criar a criança, gera o cartão em branco baseado nas vacinas do sistema
            vacinas_sistema = Vacina.objects.all()
            for vacina in vacinas_sistema:
                RegistroVacina.objects.create(
                    crianca=nova_crianca,
                    vacina=vacina,
                    status='PENDENTE'
                )
            
            return redirect('index')
    else:
        form = CriancaForm()
    
    return render(request, 'crianca_form.html', {'form': form})

# core/views.py


@login_required
def cartao_vacina(request, crianca_id):
    crianca = get_object_or_404(Crianca, pk=crianca_id)
    
    # IMPORTANTE: A ordenação por 'vacina__nome' é OBRIGATÓRIA para o regroup funcionar
    registros = RegistroVacina.objects.filter(crianca=crianca)\
        .select_related('vacina')\
        .order_by('vacina__nome', 'vacina__idade_alvo_meses')
    
    return render(request, 'cartao_vacina.html', {'crianca': crianca, 'registros': registros})

@never_cache
@login_required
def editar_registro(request, registro_id):
    """Atualizar status da vacina (Aplicar)"""
    registro = get_object_or_404(RegistroVacina, pk=registro_id)
    
    if request.method == 'POST':
        form = RegistroVacinaForm(request.POST, instance=registro)
        if form.is_valid():
            form.save()
            return redirect('cartao_vacina', crianca_id=registro.crianca.id)
    else:
        form = RegistroVacinaForm(instance=registro)
        
    return render(request, 'registro_form.html', {'form': form, 'registro': registro})

@never_cache
@login_required
def calendario_guia(request):
    """Guia informativo de todas as vacinas por idade"""
    # Buscamos todas as vacinas ordenadas por idade e depois por nome
    vacinas = Vacina.objects.all().order_by('idade_alvo_meses', 'nome')
    return render(request, 'calendario_guia.html', {'vacinas': vacinas})

@never_cache
@login_required
def censo_demografico(request):
    """Card 4: Visão Planilha/Censo com estatísticas"""
    
    # 1. A Lista Base (Pode ter filtros no futuro)
    criancas = Crianca.objects.all().order_by('data_nascimento')

    # 2. Cálculos Estatísticos (Para o topo da planilha)
    total = criancas.count()
    
    # Conta por sexo
    por_sexo = criancas.values('sexo').annotate(qtd=Count('sexo'))
    meninos = next((item['qtd'] for item in por_sexo if item['sexo'] == 'M'), 0)
    meninas = next((item['qtd'] for item in por_sexo if item['sexo'] == 'F'), 0)

    # Conta bebês (< 1 ano)
    um_ano_atras = date.today() - timedelta(days=365)
    bebes = criancas.filter(data_nascimento__gt=um_ano_atras).count()
    
    context = {
        'criancas': criancas,
        'total': total,
        'meninos': meninos,
        'meninas': meninas,
        'bebes': bebes,
        'criancas_maiores': total - bebes
    }
    
    return render(request, 'censo_demografico.html', context)