from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Count, Q, F, Case, When, Value, BooleanField
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Crianca, Vacina, RegistroVacina, UsuarioACS, LoteVacina
from .forms import CriancaForm, RegistroVacinaForm, UsuarioACSForm
from .serializers import CriancaSerializer, RegistroVacinaSerializer, VacinaSerializer

# --- FUNÇÕES AUXILIARES (HELPER FUNCTIONS) ---
def get_data_corte_10_anos():
    """Retorna a data de 10 anos atrás (regra de negócio centralizada)."""
    hoje = date.today()
    try:
        return hoje.replace(year=hoje.year - 10)
    except ValueError:
        return hoje.replace(year=hoje.year - 10, day=28)

def get_criancas_queryset(filtrar_idade=True):
    """
    Retorna o QuerySet base de Crianças já com a anotação 'is_atrasado'.
    Evita repetição de código no Censo, Lista e API.
    """
    qs = Crianca.objects.all()
    
    if filtrar_idade:
        data_corte = get_data_corte_10_anos()
        qs = qs.filter(data_nascimento__gt=data_corte)

    # Anotação otimizada para identificar atrasos
    return qs.annotate(
        qtd_pendencias=Count('registros', filter=Q(registros__status='ATRASADA'))
    ).annotate(
        is_atrasado=Case(
            When(qtd_pendencias__gt=0, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        )
    )

def baixar_estoque_lote(vacina, lote_nome):
    """Lógica centralizada para baixar estoque."""
    if not lote_nome: return
    
    lote_obj = LoteVacina.objects.filter(vacina=vacina, numero_lote__iexact=lote_nome).first()
    
    if lote_obj and lote_obj.quantidade_disponivel > 0:
        lote_obj.quantidade_disponivel = F('quantidade_disponivel') - 1
        lote_obj.save()
        return lote_obj # Retorna o objeto atualizado
    return None

def is_admin(user):
    return user.is_superuser

# --- VIEWSETS (API) ---

class VacinaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Vacina.objects.all().order_by('idade_alvo_meses', 'nome')
    serializer_class = VacinaSerializer
    pagination_class = None

class CriancaViewSet(viewsets.ModelViewSet):
    serializer_class = CriancaSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['nome', 'cns', 'nome_mae']
    filterset_fields = ['sexo', 'localidade']

    def get_queryset(self):
        # Usa a função auxiliar
        qs = get_criancas_queryset(filtrar_idade=True)

        if self.request.query_params.get('atualizar') == 'true':
            for c in qs.prefetch_related('registros__vacina'):
                c.verificar_atrasos()

        status_filter = self.request.query_params.get('status_filtro')
        if status_filter == 'ATRASADO':
            qs = qs.filter(is_atrasado=True)
        elif status_filter == 'EM_DIA':
            qs = qs.filter(is_atrasado=False)

        ordem = self.request.query_params.get('ordem')
        if ordem == 'nome': qs = qs.order_by('nome')
        elif ordem == 'idade_cresc': qs = qs.order_by('data_nascimento')
        elif ordem == 'idade_dec': qs = qs.order_by('-data_nascimento')
        else: qs = qs.order_by('-id')

        return qs
    
    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        um_ano_atras = date.today() - timedelta(days=365)
        # Agregação direta no banco
        dados = Crianca.objects.aggregate(
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
        registro_antigo = self.get_object()
        estava_aplicada = registro_antigo.status == 'APLICADA'
        registro_novo = serializer.save()

        if registro_novo.status == 'APLICADA' and not estava_aplicada:
            baixar_estoque_lote(registro_novo.vacina, registro_novo.lote)

# --- VIEWS (TEMPLATES) ---

@never_cache
@login_required
def index(request):
    """Dashboard Otimizado"""
    um_ano_atras = date.today() - timedelta(days=365)
    
    # Faz tudo em 1 consulta ao banco (Aggregate)
    stats = Crianca.objects.aggregate(
        total=Count('id'),
        meninos=Count('id', filter=Q(sexo='M')),
        meninas=Count('id', filter=Q(sexo='F')),
        bebes=Count('id', filter=Q(data_nascimento__gt=um_ano_atras))
    )
    
    context = {
        'total': stats['total'],
        'meninos': stats['meninos'],
        'meninas': stats['meninas'],
        'bebes': stats['bebes'],
        'criancas_maiores': stats['total'] - stats['bebes'],
    }
    return render(request, 'index.html', context)

@never_cache
@login_required
def lista_criancas(request):
    qs = get_criancas_queryset(filtrar_idade=True)
    
    query = request.GET.get('busca')
    if query:
        qs = qs.filter(nome__icontains=query)

    qs = qs.order_by('-criado_em')
    
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'lista_criancas.html', {'criancas': page_obj})

def censo_demografico(request):
    qs = get_criancas_queryset(filtrar_idade=True)

    busca = request.GET.get('busca')
    status_filtro = request.GET.get('status')
    sexo_filtro = request.GET.get('sexo')
    ordem_filtro = request.GET.get('ordem')

    if busca: qs = qs.filter(nome__icontains=busca)
    if sexo_filtro: qs = qs.filter(sexo=sexo_filtro)
    
    if status_filtro == 'ATRASADO': qs = qs.filter(is_atrasado=True)
    elif status_filtro == 'EM_DIA': qs = qs.filter(is_atrasado=False)

    if ordem_filtro == 'nome': qs = qs.order_by('nome')
    elif ordem_filtro == 'idade_cresc': qs = qs.order_by('data_nascimento')
    else: qs = qs.order_by('-data_nascimento')

    # Estatísticas
    um_ano_atras = date.today() - timedelta(days=365)
    data_corte = get_data_corte_10_anos()
    
    # Query separada para stats totais (independente dos filtros da tabela)
    stats = Crianca.objects.filter(data_nascimento__gt=data_corte).aggregate(
        total=Count('id'),
        meninos=Count('id', filter=Q(sexo='M')),
        meninas=Count('id', filter=Q(sexo='F')),
        bebes=Count('id', filter=Q(data_nascimento__gt=um_ano_atras))
    )

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'criancas': page_obj,
        'total': stats['total'],     
        'meninos': stats['meninos'],
        'meninas': stats['meninas'],
        'bebes': stats['bebes'],
    }
    return render(request, 'censo_demografico.html', context)

@never_cache
@login_required
def editar_registro(request, registro_id):
    registro = get_object_or_404(RegistroVacina, pk=registro_id)
    
    if request.method == 'POST':
        form = RegistroVacinaForm(request.POST, instance=registro)
        if form.is_valid():
            vacina_aplicada = form.save()
            
            # Lógica de estoque centralizada
            if vacina_aplicada.lote and vacina_aplicada.status == 'APLICADA':
                lote_atualizado = baixar_estoque_lote(vacina_aplicada.vacina, vacina_aplicada.lote)
                
                if lote_atualizado:
                    lote_atualizado.refresh_from_db()
                    if lote_atualizado.quantidade_disponivel <= 5:
                        messages.warning(request, f"Atenção: Estoque baixo ({lote_atualizado.quantidade_disponivel} un).")
                else:
                    messages.error(request, f"Erro ou estoque zerado para o lote {vacina_aplicada.lote}.")

            messages.success(request, 'Atualizado com sucesso!')
            return redirect('cartao_vacina', crianca_id=registro.crianca.id)
    else:
        form = RegistroVacinaForm(instance=registro, initial={'status': 'APLICADA'})

    return render(request, 'registro_form.html', {'form': form, 'registro': registro, 'crianca': registro.crianca})

# --- OUTRAS VIEWS SIMPLES ---

def api_lotes_por_vacina(request, vacina_id):
    lotes = LoteVacina.objects.filter(vacina_id=vacina_id).values('numero_lote', 'fabricante', 'quantidade_disponivel')
    return JsonResponse(list(lotes), safe=False)

@user_passes_test(is_admin)
def cadastrar_acs(request):
    if request.method == 'POST':
        form = UsuarioACSForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cadastrado com sucesso!')
            return redirect('index')
    else:
        form = UsuarioACSForm()
    return render(request, 'cadastro_acs.html', {'form': form})

@never_cache
@login_required
def cadastrar_crianca(request):
    if request.method == 'POST':
        form = CriancaForm(request.POST)
        if form.is_valid():
            nova_crianca = form.save(commit=False)
            nova_crianca.cadastrado_por = request.user
            nova_crianca.save()
            return redirect('cartao_vacina', nova_crianca.id)
    else:
        form = CriancaForm()
    return render(request, 'crianca_form.html', {'form': form})

def cartao_vacina(request, crianca_id):
    crianca = get_object_or_404(Crianca, pk=crianca_id)
    hoje = date.today()
    idade_meses = (hoje.year - crianca.data_nascimento.year) * 12 + (hoje.month - crianca.data_nascimento.month)
    
    # Atualiza atrasos em massa se necessário
    RegistroVacina.objects.filter(
        crianca=crianca, status='PENDENTE', vacina__idade_alvo_meses__lt=idade_meses
    ).update(status='ATRASADA')
        
    registros = RegistroVacina.objects.filter(crianca=crianca).select_related('vacina').order_by('vacina__idade_alvo_meses', 'vacina__nome')
    return render(request, 'cartao_vacina.html', {'crianca': crianca, 'registros': registros})

@never_cache
@login_required
def calendario_guia(request):
    vacinas = Vacina.objects.all().order_by('idade_alvo_meses', 'nome')
    return render(request, 'calendario_guia.html', {'vacinas': vacinas})

@never_cache
@login_required
def confirmar_aplicacao(request, registro_id):
    registro = get_object_or_404(RegistroVacina, pk=registro_id)
    if request.method == 'POST':
        registro.status = 'APLICADA'
        registro.data_aplicacao = request.POST.get('data_aplicacao') or date.today()
        registro.aplicado_por = request.user
        registro.save()
        messages.success(request, 'Vacina registrada!')
    return redirect('cartao_vacina', crianca_id=registro.crianca.id)

@never_cache
@user_passes_test(is_admin)
def lista_usuarios(request):
    usuarios = UsuarioACS.objects.filter(is_superuser=False).order_by('first_name')
    return render(request, 'lista_usuarios.html', {'usuarios': usuarios})

def offline_view(request):
    return render(request, 'offline.html')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def usuario_atual(request):
    user = request.user
    return Response({'id': user.id, 'username': user.username, 'full_name': user.get_full_name() or user.username})