from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Crianca, Vacina, RegistroVacina, UsuarioACS, LoteVacina
from .forms import CriancaForm, RegistroVacinaForm, UsuarioACSForm
from datetime import date, timedelta
from django.db.models import Count, Q, F
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from django.core.paginator import Paginator
# Adicione estes imports do DRF no topo do arquivo
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import CriancaSerializer, RegistroVacinaSerializer, VacinaSerializer
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class VacinaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lista todas as vacinas ordenadas por idade para o Guia Vacinal
    """
    queryset = Vacina.objects.all().order_by('idade_alvo_meses', 'nome')
    serializer_class = VacinaSerializer
    pagination_class = None

def api_lotes_por_vacina(request, vacina_id):
    # ADICIONADO: 'quantidade_disponivel' é obrigatório para o React exibir a lista
    lotes = LoteVacina.objects.filter(vacina_id=vacina_id).values(
        'numero_lote', 
        'fabricante', 
        'quantidade_disponivel' 
    )
    return JsonResponse(list(lotes), safe=False)


def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
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
    
    if request.method == 'POST':
        form = RegistroVacinaForm(request.POST, instance=registro)
        
        if form.is_valid():
            # 1. Salva o registro da vacina na criança
            vacina_aplicada = form.save()
            
            # 2. BAIXA DE ESTOQUE AUTOMÁTICA
            # Verifica se foi informado um lote e se a vacina foi realmente aplicada
            if vacina_aplicada.lote and vacina_aplicada.status == 'APLICADA':
                
                # Busca o lote correspondente no banco de estoque
                lote_estoque = LoteVacina.objects.filter(
                    vacina=vacina_aplicada.vacina, 
                    numero_lote=vacina_aplicada.lote
                ).first()
                
                if lote_estoque:
                    if lote_estoque.quantidade_disponivel > 0:
                        # Usa F() para garantir subtração atômica e segura
                        lote_estoque.quantidade_disponivel = F('quantidade_disponivel') - 1
                        lote_estoque.save()
                        
                        # (Opcional) Verifica se o estoque zerou após essa aplicação
                        lote_estoque.refresh_from_db() # Recarrega para ver o valor real numérico
                        if lote_estoque.quantidade_disponivel <= 5:
                            messages.warning(request, f"Atenção: O estoque do Lote {lote_estoque.numero_lote} está baixo ({lote_estoque.quantidade_disponivel} un).")
                    else:
                        messages.error(request, f"Erro: O Lote {vacina_aplicada.lote} consta como zerado no sistema, mas o registro foi salvo.")
            
            messages.success(request, 'Vacina registrada e estoque atualizado com sucesso!')
            return redirect('cartao_vacina', crianca_id=registro.crianca.id)
    else:
        form = RegistroVacinaForm(
            instance=registro, 
            initial={'status': 'APLICADA'}
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

def censo_demografico(request):
    # === 0. OTIMIZAÇÃO DE LEITURA ===
    # O 'prefetch_related' carrega os dados filhos (registros) na memória
    # O 'select_related' carrega os dados pais (vacina) na memória
    todas_criancas = Crianca.objects.prefetch_related(
        'registros__vacina' # Traz os registros E os dados da vacina (idade alvo)
    ).all()

    # Agora o loop roda quase instantâneo porque os dados já estão na memória RAM do servidor
    for c in todas_criancas:
        c.verificar_atrasos()

    # === 1. ESTATÍSTICAS ===
    qs_base = Crianca.objects.all()
    um_ano_atras = date.today() - timedelta(days=365)
    
    estatisticas = qs_base.aggregate(
        total=Count('id'),
        meninos=Count('id', filter=Q(sexo='M')),
        meninas=Count('id', filter=Q(sexo='F')),
        bebes=Count('id', filter=Q(data_nascimento__gt=um_ano_atras))
    )

    # === 2. QUERYSET PRINCIPAL ===
    # ATENÇÃO AQUI: Usamos 'registros' pois é o related_name no Model
    lista_criancas = Crianca.objects.annotate(
        tem_atraso=Count('registros', filter=Q(registros__status='ATRASADA'))
    )

    # Captura dados da URL
    busca = request.GET.get('busca')
    status = request.GET.get('status')
    sexo = request.GET.get('sexo')
    ordem = request.GET.get('ordem')

    # --- LÓGICA DE FILTRAGEM ---
    if busca:
        print(f"Filtrando nome por: {busca}")
        lista_criancas = lista_criancas.filter(nome__icontains=busca)
    
    if status == 'atrasada':
        print("Filtrando por: ATRASADOS")
        # Pega quem tem contagem de atrasos > 0
        lista_criancas = lista_criancas.filter(tem_atraso__gt=0)
    elif status == 'em_dia':
        print("Filtrando por: EM DIA")
        # Pega quem tem contagem de atrasos == 0
        lista_criancas = lista_criancas.filter(tem_atraso=0)

    if sexo:
        print(f"Filtrando sexo por: {sexo}")
        lista_criancas = lista_criancas.filter(sexo=sexo)

    # --- ORDENAÇÃO ---
    if ordem == 'nome':
        lista_criancas = lista_criancas.order_by('nome')
    elif ordem == 'idade_cresc':
        lista_criancas = lista_criancas.order_by('-data_nascimento')
    elif ordem == 'idade_dec':
        lista_criancas = lista_criancas.order_by('data_nascimento')
    else:
        lista_criancas = lista_criancas.order_by('-data_nascimento')

    # Contexto final
    context = {
        'criancas': lista_criancas,
        'total': estatisticas['total'],
        'meninos': estatisticas['meninos'],
        'meninas': estatisticas['meninas'],
        'bebes': estatisticas['bebes'],
        'criancas_maiores': (estatisticas['total'] or 0) - (estatisticas['bebes'] or 0)
    }
    
    # === PAGINAÇÃO ===
    paginator = Paginator(lista_criancas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 5. CONTEXTO FINAL
    context = {
        'criancas': page_obj,
        'total': estatisticas['total'],
        'meninos': estatisticas['meninos'], 
        'meninas': estatisticas['meninas'],
        'bebes': estatisticas['bebes'],      
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
            
        # 3. Salva o usuário logado automaticamente
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

def offline_view(request):
    return render(request, 'offline.html')

# =========================================================
#  ÁREA DA API (Django REST Framework)
# =========================================================

class CriancaViewSet(viewsets.ModelViewSet):
    """
    API Power-Up para o Censo Demográfico
    """
    serializer_class = CriancaSerializer
    
    # Mantemos os filtros padrões do Django REST Framework
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['nome', 'cns', 'nome_mae']
    filterset_fields = ['sexo', 'localidade']

    def get_queryset(self):
        # 1. BASE INTELIGENTE:
        # Já pedimos ao banco para trazer a contagem de vacinas atrasadas de cada criança.
        # Isso cria um campo virtual 'qtd_atrasos' que usaremos para filtrar.
        qs = Crianca.objects.annotate(
            qtd_atrasos=Count('registros', filter=Q(registros__status='ATRASADA'))
        )

        # 2. LÓGICA DO ROBÔ (Mantida do seu código original)
        # Se o React pedir ?atualizar=true, verifica atrasos antes de devolver
        if self.request.query_params.get('atualizar') == 'true':
            lista_para_checar = qs.prefetch_related('registros__vacina')
            for c in lista_para_checar:
                c.verificar_atrasos()

        # 3. FILTRO DE STATUS (Vindo do Dropdown do Censo)
        status_filter = self.request.query_params.get('status_filtro')
        if status_filter == 'ATRASADO':
            qs = qs.filter(qtd_atrasos__gt=0) # Traz quem tem > 0 atrasos
        elif status_filter == 'EM_DIA':
            qs = qs.filter(qtd_atrasos=0)     # Traz quem tem 0 atrasos

        # 4. ORDENAÇÃO PERSONALIZADA
        ordem = self.request.query_params.get('ordem')
        if ordem == 'nome':
            qs = qs.order_by('nome')
        elif ordem == 'idade_cresc': # Do mais velho pro mais novo
            qs = qs.order_by('data_nascimento')
        elif ordem == 'idade_dec':   # Do mais novo pro mais velho (Padrão bebês)
            qs = qs.order_by('-data_nascimento')
        else:
            qs = qs.order_by('-id') # Padrãozão

        return qs

    # --- NOVIDADE: A ROTA DOS CARDS COLORIDOS ---
    # O React vai chamar: /api/criancas/estatisticas/
    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        # Pegamos a base completa (sem filtros de página)
        qs_total = Crianca.objects.all()
        
        um_ano_atras = date.today() - timedelta(days=365)
        
        # O banco calcula tudo de uma vez (super rápido)
        dados = qs_total.aggregate(
            total=Count('id'),
            meninos=Count('id', filter=Q(sexo='M')),
            meninas=Count('id', filter=Q(sexo='F')),
            bebes=Count('id', filter=Q(data_nascimento__gt=um_ano_atras))
        )
        
        return Response(dados)
    
class RegistroVacinaViewSet(viewsets.ModelViewSet):
    queryset = RegistroVacina.objects.all()
    serializer_class = RegistroVacinaSerializer
    http_method_names = ['get', 'patch', 'put', 'head', 'options']

    def perform_update(self, serializer):
        # 1. Pega o estado ANTES de salvar (Do Banco)
        registro_antigo = self.get_object()
        estava_aplicada = registro_antigo.status == 'APLICADA'
        
        print(f"DEBUG: Status Antigo: {registro_antigo.status}")

        # 2. Salva as mudanças
        registro_novo = serializer.save()
        
        print(f"DEBUG: Status Novo: {registro_novo.status}")
        print(f"DEBUG: Lote Informado: '{registro_novo.lote}'")

        # 3. Lógica de Baixa de Estoque
        # Só entra se:
        # - Virou APLICADA agora (não era antes)
        # - Tem um lote preenchido
        if registro_novo.status == 'APLICADA' and not estava_aplicada and registro_novo.lote:
            print("DEBUG: Entrou na lógica de baixa de estoque...")
            
            # Tenta achar o lote (ignorando maiúsculas/minúsculas para garantir)
            lote_obj = LoteVacina.objects.filter(
                vacina=registro_novo.vacina, 
                numero_lote__iexact=registro_novo.lote # iexact ignora caixa alta/baixa
            ).first()
            
            if lote_obj:
                print(f"DEBUG: Lote encontrado! Qtd Atual: {lote_obj.quantidade_disponivel}")
                
                if lote_obj.quantidade_disponivel > 0:
                    lote_obj.quantidade_disponivel = F('quantidade_disponivel') - 1
                    lote_obj.save()
                    
                    # Recarrega para confirmar
                    lote_obj.refresh_from_db()
                    print(f"SUCESSO: Estoque baixado para {lote_obj.quantidade_disponivel}")
                else:
                    print("AVISO: Estoque já estava zerado.")
            else:
                print(f"ERRO: Lote '{registro_novo.lote}' não encontrado no banco para a vacina {registro_novo.vacina}.")
        else:
            print("DEBUG: Não baixou estoque. Motivo: Ou já estava aplicada, ou não tem lote, ou status não é APLICADA.")

# Nav bar do React
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def usuario_atual(request):
    """Retorna os dados do usuário logado"""
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'full_name': user.get_full_name() or user.username # Se não tiver nome completo, usa o login
    })