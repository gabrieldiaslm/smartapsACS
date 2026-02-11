from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Crianca, Vacina, RegistroVacina, UsuarioACS, LoteVacina
from .forms import CriancaForm, RegistroVacinaForm, UsuarioACSForm
from datetime import date, timedelta
from django.db.models import Count, Q, F, Case, When, Value, BooleanField
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from django.core.paginator import Paginator
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
    # FILTRO DE IDADE (10 ANOS)
    hoje = date.today()
    try:
        data_corte = hoje.replace(year=hoje.year - 10)
    except ValueError:
        data_corte = hoje.replace(year=hoje.year - 10, day=28)
    
    qs = Crianca.objects.filter(data_nascimento__gt=data_corte)

    qs = qs.annotate(
        qtd_atrasos=Count('registros', filter=Q(registros__status='ATRASADA'))
    ).annotate(
        is_atrasado=Case(
            When(qtd_atrasos__gt=0, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        )
    )

    # BUSCA
    query = request.GET.get('busca')
    if query:
        qs = qs.filter(nome__icontains=query)

    # ORDENAÇÃO
    qs = qs.order_by('-criado_em')

    # PAGINAÇÃO
    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'lista_criancas.html', {'criancas': page_obj})


def censo_demografico(request):
    hoje = date.today()
    try:
        data_corte = hoje.replace(year=hoje.year - 10)
    except ValueError:
        data_corte = hoje.replace(year=hoje.year - 10, day=28)
    
    qs = Crianca.objects.filter(data_nascimento__gt=data_corte)

    qs = qs.annotate(
        qtd_pendencias_vencidas=Count(
            'registros', 
            filter=Q(registros__status='ATRASADA')
        )
    ).annotate(
        is_atrasado=Case(
            When(qtd_pendencias_vencidas__gt=0, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        )
    )

    busca = request.GET.get('busca')
    status_filtro = request.GET.get('status')
    sexo_filtro = request.GET.get('sexo')
    ordem_filtro = request.GET.get('ordem')

    if busca:
        qs = qs.filter(nome__icontains=busca)
    
    if sexo_filtro:
        qs = qs.filter(sexo=sexo_filtro)

    if status_filtro == 'ATRASADO':
        qs = qs.filter(is_atrasado=True)
    elif status_filtro == 'EM_DIA':
        qs = qs.filter(is_atrasado=False)

    if ordem_filtro == 'nome':
        qs = qs.order_by('nome')
    elif ordem_filtro == 'idade_cresc':
        qs = qs.order_by('data_nascimento') 
    else: 
        qs = qs.order_by('-data_nascimento')

    um_ano_atras = hoje - timedelta(days=365)
    
    qs_total = Crianca.objects.filter(data_nascimento__gt=data_corte)
    
    stats = qs_total.aggregate(
        total=Count('id'),
        meninos=Count('id', filter=Q(sexo='M')),
        meninas=Count('id', filter=Q(sexo='F')),
        bebes=Count('id', filter=Q(data_nascimento__gt=um_ano_atras))
    )

    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

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
def cadastrar_crianca(request):
    """Cadastrar Criança"""
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
    
    vacinas_vencidas = RegistroVacina.objects.filter(
        crianca=crianca,
        status='PENDENTE',
        vacina__idade_alvo_meses__lt=idade_meses # lt (less then)
    )
    
    if vacinas_vencidas.exists():
        vacinas_vencidas.update(status='ATRASADA')
        
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
            vacina_aplicada = form.save()
            
            # Verifica se foi informado o lote e se a vacina foi aplicada
            if vacina_aplicada.lote and vacina_aplicada.status == 'APLICADA':
                lote_estoque = LoteVacina.objects.filter(
                    vacina=vacina_aplicada.vacina, 
                    numero_lote=vacina_aplicada.lote
                ).first()
                
                if lote_estoque:
                    if lote_estoque.quantidade_disponivel > 0:
                        lote_estoque.quantidade_disponivel = F('quantidade_disponivel') - 1
                        lote_estoque.save()
                        
                        lote_estoque.refresh_from_db()
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
    vacinas = Vacina.objects.all().order_by('idade_alvo_meses', 'nome')
    return render(request, 'calendario_guia.html', {'vacinas': vacinas})



@never_cache
@login_required
def confirmar_aplicacao(request, registro_id):
    """Marca a vacina como aplicada e salva quem fez isso automaticamente"""
    registro = get_object_or_404(RegistroVacina, pk=registro_id)
    
    if request.method == 'POST':
        registro.status = 'APLICADA'
        
        data_form = request.POST.get('data_aplicacao')
        if data_form:
            registro.data_aplicacao = data_form
        else:
            registro.data_aplicacao = date.today()
            
        # Salva o usuário logado automaticamente
        registro.aplicado_por = request.user
        
        registro.save()
        messages.success(request, f'Vacina {registro.vacina.nome} registrada com sucesso!')
        return redirect('cartao_vacina', crianca_id=registro.crianca.id)

    return redirect('cartao_vacina', crianca_id=registro.crianca.id)

@never_cache
@user_passes_test(is_admin)
def lista_usuarios(request):
    """Admin visualiza lista de usuários"""
    usuarios = UsuarioACS.objects.filter(is_superuser=False).order_by('first_name')
    
    return render(request, 'lista_usuarios.html', {'usuarios': usuarios})

def offline_view(request):
    return render(request, 'offline.html')

# ------------------------------------------
#  ÁREA DA API 

class CriancaViewSet(viewsets.ModelViewSet):
    """
    API Power-Up para o Censo Demográfico
    """
    serializer_class = CriancaSerializer
    
    # Filtros do DRF (Django rest framework)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['nome', 'cns', 'nome_mae']
    filterset_fields = ['sexo', 'localidade']

    def get_queryset(self):
        hoje = date.today()
        try:
            data_corte = hoje.replace(year=hoje.year - 10)
        except ValueError:
            # Se for 29 de fev e 10 anos atrás não for bissexto, ajusta para dia 28
            data_corte = hoje.replace(year=hoje.year - 10, day=28)

        qs = Crianca.objects.filter(data_nascimento__gt=data_corte)

        qs = qs.annotate(
            qtd_atrasos=Count('registros', filter=Q(registros__status='ATRASADA'))
        )

        # Verificação de atrasos
        if self.request.query_params.get('atualizar') == 'true':
            lista_para_checar = qs.prefetch_related('registros__vacina')
            for c in lista_para_checar:
                c.verificar_atrasos()

        status_filter = self.request.query_params.get('status_filtro')
        if status_filter == 'ATRASADO':
            qs = qs.filter(qtd_atrasos__gt=0)
        elif status_filter == 'EM_DIA':
            qs = qs.filter(qtd_atrasos=0)

        ordem = self.request.query_params.get('ordem')
        if ordem == 'nome':
            qs = qs.order_by('nome')
        elif ordem == 'idade_cresc':
            qs = qs.order_by('data_nascimento')
        elif ordem == 'idade_dec':
            qs = qs.order_by('-data_nascimento')
        else:
            qs = qs.order_by('-id')

        return qs
    
    # censo no react
    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        qs_total = Crianca.objects.all()
        
        um_ano_atras = date.today() - timedelta(days=365)
        
        # O banco calcula tudo de uma vez
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
        registro_antigo = self.get_object()
        estava_aplicada = registro_antigo.status == 'APLICADA'
        
        print(f"DEBUG: Status Antigo: {registro_antigo.status}")

        # Salva as mudanças
        registro_novo = serializer.save()
        
        print(f"DEBUG: Status Novo: {registro_novo.status}")
        print(f"DEBUG: Lote Informado: '{registro_novo.lote}'")

        # Lógica de Baixa de Estoque
        # Só entra se: Virou APLICADA agora (não era antes) e Tem um lote preenchido
        if registro_novo.status == 'APLICADA' and not estava_aplicada and registro_novo.lote:
            print("DEBUG: Entrou na lógica de baixa de estoque...")
            
            # Tenta achar o lote
            lote_obj = LoteVacina.objects.filter(
                vacina=registro_novo.vacina, 
                numero_lote__iexact=registro_novo.lote # iexact ignora caixa alta/baixa
            ).first()
            
            if lote_obj:
                print(f"DEBUG: Lote encontrado! Qtd Atual: {lote_obj.quantidade_disponivel}")
                
                if lote_obj.quantidade_disponivel > 0:
                    lote_obj.quantidade_disponivel = F('quantidade_disponivel') - 1
                    lote_obj.save()
                    
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