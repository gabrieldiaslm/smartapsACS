from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Crianca, Vacina, RegistroVacina, UsuarioACS
from .forms import CriancaForm, RegistroVacinaForm, UsuarioACSForm
from datetime import date, timedelta
from django.db.models import Count, Q
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


def cartao_vacina(request, crianca_id):
    crianca = get_object_or_404(Crianca, pk=crianca_id)
    
    # Cálculo da idade
    hoje = date.today()
    idade_meses = (hoje.year - crianca.data_nascimento.year) * 12 + (hoje.month - crianca.data_nascimento.month)
    
    # OTIMIZAÇÃO:
    # Em vez de trazer tudo e testar no Python, pedimos ao banco:
    # "Me dê apenas as vacinas PENDENTES cuja idade alvo já PASSOU (é menor que a idade da criança)"
    vacinas_vencidas = RegistroVacina.objects.filter(
        crianca=crianca,
        status='PENDENTE',
        vacina__idade_alvo_meses__lt=idade_meses # __lt significa "Less Than" (menor que)
    )
    
    # Se houver alguma nessa condição, atualizamos direto
    if vacinas_vencidas.exists():
        # O 'update' roda um comando SQL direto, sem carregar objetos na memória um por um
        vacinas_vencidas.update(status='ATRASADA')
        
    # === 2. BUSCA PARA EXIBIÇÃO (Já com dados atualizados) ===
    #    Ordenamos primeiro pela IDADE (cronológico) e depois pelo NOME
    registros = RegistroVacina.objects.filter(crianca=crianca)\
        .select_related('vacina')\
        .order_by('vacina__idade_alvo_meses', 'vacina__nome') # <--- MUDANÇA AQUI
    
    return render(request, 'cartao_vacina.html', {'crianca': crianca, 'registros': registros})

@never_cache
@login_required
def editar_registro(request, registro_id):
    registro = get_object_or_404(RegistroVacina, pk=registro_id)
    
    # Prepara o nome do usuário atual para usar como padrão
    nome_usuario_atual = f"{request.user.first_name} {request.user.last_name}".strip()
    if not nome_usuario_atual:
        nome_usuario_atual = request.user.username

    if request.method == 'POST':
        form = RegistroVacinaForm(request.POST, instance=registro)
        
        if form.is_valid():
            aplicacao = form.save(commit=False)
            
            # NÃO PRECISA MAIS DEFINIR 'profissional_aplicou' AQUI
            # O valor agora vem direto do formulário (dropdown)
            
            aplicacao.save()
            messages.success(request, 'Registro atualizado com sucesso!')
            return redirect('cartao_vacina', crianca_id=registro.crianca.id)
    else:
        # GET: Abre o form com valores iniciais
        form = RegistroVacinaForm(
            instance=registro, 
            initial={
                'status': 'APLICADA',
                # Aqui definimos que o usuário logado vem selecionado por padrão
                'profissional_aplicou': nome_usuario_atual 
            }
        )

    context = {
        'form': form,
        'registro': registro,
        'crianca': registro.crianca
    }
    return render(request, 'registro_form.html', context)

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
    """Card 4: Censo com Filtros e Ordenação"""
    
    # === 1. ESTATÍSTICAS GLOBAIS (Otimizadas) ===
    # Calculamos isso INDEPENDENTE dos filtros, para o gestor sempre ver o tamanho da unidade
    qs_base = Crianca.objects.all()
    um_ano_atras = date.today() - timedelta(days=365)
    
    estatisticas = qs_base.aggregate(
        total=Count('id'),
        meninos=Count('id', filter=Q(sexo='M')),
        meninas=Count('id', filter=Q(sexo='F')),
        bebes=Count('id', filter=Q(data_nascimento__gt=um_ano_atras))
    )

    # === 2. LISTA FILTRÁVEL ===
    # Começamos anotando os atrasos (necessário para filtrar por status)
    lista_criancas = Crianca.objects.annotate(
        tem_atraso=Count('registros', filter=Q(registros__status='ATRASADA'))
    )

    # --- A. Captura os parâmetros da URL ---
    busca = request.GET.get('busca')
    sexo = request.GET.get('sexo')
    status = request.GET.get('status')
    ordem = request.GET.get('ordem')

    # --- B. Aplica Filtros ---
    if busca:
        lista_criancas = lista_criancas.filter(nome__icontains=busca)
    
    if sexo:
        lista_criancas = lista_criancas.filter(sexo=sexo)
        
    if status == 'atrasada':
        lista_criancas = lista_criancas.filter(tem_atraso__gt=0)
    elif status == 'em_dia':
        lista_criancas = lista_criancas.filter(tem_atraso=0)

    # --- C. Aplica Ordenação ---
    if ordem == 'nome':
        lista_criancas = lista_criancas.order_by('nome')
    elif ordem == 'idade_cresc': # Do mais novo para o mais velho
        lista_criancas = lista_criancas.order_by('-data_nascimento')
    elif ordem == 'idade_dec':   # Do mais velho para o mais novo
        lista_criancas = lista_criancas.order_by('data_nascimento')
    else:
        # Padrão: Mais novos primeiro (Bebês no topo)
        lista_criancas = lista_criancas.order_by('-data_nascimento')

    context = {
        'criancas': lista_criancas,
        # Estatísticas globais mantidas
        'total': estatisticas['total'],
        'meninos': estatisticas['meninos'],
        'meninas': estatisticas['meninas'],
        'bebes': estatisticas['bebes'],
        'criancas_maiores': (estatisticas['total'] or 0) - (estatisticas['bebes'] or 0)
    }
    
    return render(request, 'censo_demografico.html', context)

@never_cache
@login_required
def confirmar_aplicacao(request, registro_id):
    """Marca a vacina como aplicada e salva quem fez isso automaticamente"""
    registro = get_object_or_404(RegistroVacina, pk=registro_id)
    
    if request.method == 'POST':
        # 1. Marca como Aplicada
        registro.status = 'APLICADA'
        
        # 2. Salva a data (pode vir do form ou ser hoje)
        data_form = request.POST.get('data_aplicacao')
        if data_form:
            registro.data_aplicacao = data_form
        else:
            registro.data_aplicacao = date.today()
            
        # 3. A MÁGICA: Salva o usuário logado automaticamente
        registro.aplicado_por = request.user
        
        registro.save()
        messages.success(request, f'Vacina {registro.vacina.nome} registrada com sucesso!')
        return redirect('cartao_vacina', crianca_id=registro.crianca.id)

    return redirect('cartao_vacina', crianca_id=registro.crianca.id)

@never_cache
@user_passes_test(is_admin)
def lista_usuarios(request):
    """Card 6: Admin visualiza lista de usuários"""
    # Exclui o próprio superuser da lista para evitar acidentes, ou mostra todos
    usuarios = UsuarioACS.objects.filter(is_superuser=False).order_by('first_name')
    
    return render(request, 'lista_usuarios.html', {'usuarios': usuarios})