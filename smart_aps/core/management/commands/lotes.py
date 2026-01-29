import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from core.models import Vacina, LoteVacina

class Command(BaseCommand):
    help = 'Popula o banco de dados com Vacinas e Lotes de Estoque (Sem criar pacientes)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Iniciando população de Vacinas e Lotes...'))

        # ==========================================
        # 1. POPULAR VACINAS (Calendário Oficial 2025/2026)
        # ==========================================
        self.stdout.write('1. Configurando Calendário Vacinal...')
        
        lista_vacinas = [
            # Ao Nascer
            {'nome': 'BCG', 'dose': 'Dose Única', 'meses': 0, 'desc': 'Tuberculose'},
            {'nome': 'Hepatite B', 'dose': 'Dose ao nascer', 'meses': 0, 'desc': 'Hepatite B'},

            # 2 Meses
            {'nome': 'Penta (DTP+Hib+HB)', 'dose': '1ª Dose', 'meses': 2, 'desc': 'Difteria, Tétano, Coqueluche, Hep B, Hib'},
            {'nome': 'Poliomielite (VIP)', 'dose': '1ª Dose', 'meses': 2, 'desc': 'Paralisia Infantil (Inativada)'},
            {'nome': 'Pneumocócica 10V', 'dose': '1ª Dose', 'meses': 2, 'desc': 'Pneumonia, Otite, Meningite'},
            {'nome': 'Rotavírus Humano', 'dose': '1ª Dose', 'meses': 2, 'desc': 'Diarreia por Rotavírus'},

            # 3 Meses
            {'nome': 'Meningocócica C', 'dose': '1ª Dose', 'meses': 3, 'desc': 'Meningite C'},

            # 4 Meses
            {'nome': 'Penta (DTP+Hib+HB)', 'dose': '2ª Dose', 'meses': 4, 'desc': ''},
            {'nome': 'Poliomielite (VIP)', 'dose': '2ª Dose', 'meses': 4, 'desc': ''},
            {'nome': 'Pneumocócica 10V', 'dose': '2ª Dose', 'meses': 4, 'desc': ''},
            {'nome': 'Rotavírus Humano', 'dose': '2ª Dose', 'meses': 4, 'desc': ''},

            # 5 Meses
            {'nome': 'Meningocócica C', 'dose': '2ª Dose', 'meses': 5, 'desc': ''},

            # 6 Meses
            {'nome': 'Penta (DTP+Hib+HB)', 'dose': '3ª Dose', 'meses': 6, 'desc': ''},
            {'nome': 'Poliomielite (VIP)', 'dose': '3ª Dose', 'meses': 6, 'desc': ''},
            {'nome': 'COVID-19 (Pfizer Baby)', 'dose': '1ª Dose', 'meses': 6, 'desc': 'Formas graves de COVID-19'},

            # 7 Meses
            {'nome': 'COVID-19 (Pfizer Baby)', 'dose': '2ª Dose', 'meses': 7, 'desc': ''},

            # 9 Meses
            {'nome': 'Febre Amarela', 'dose': '1ª Dose', 'meses': 9, 'desc': 'Febre Amarela'},
            {'nome': 'COVID-19 (Pfizer Baby)', 'dose': '3ª Dose', 'meses': 9, 'desc': ''},

            # 12 Meses (1 Ano)
            {'nome': 'Tríplice Viral (SCR)', 'dose': '1ª Dose', 'meses': 12, 'desc': 'Sarampo, Caxumba, Rubéola'},
            {'nome': 'Pneumocócica 10V', 'dose': 'Reforço', 'meses': 12, 'desc': ''},
            {'nome': 'Meningocócica ACWY', 'dose': 'Dose Única', 'meses': 12, 'desc': 'Meningite A, C, W, Y (Atualizado)'},

            # 15 Meses
            {'nome': 'DTP', 'dose': '1º Reforço', 'meses': 15, 'desc': 'Difteria, Tétano, Coqueluche'},
            {'nome': 'Poliomielite (VOP)', 'dose': '1º Reforço', 'meses': 15, 'desc': 'Paralisia Infantil (Gotinha)'},
            {'nome': 'Hepatite A', 'dose': 'Dose Única', 'meses': 15, 'desc': 'Hepatite A'},
            {'nome': 'Tetra Viral (SCRV)', 'dose': 'Dose Única', 'meses': 15, 'desc': 'Sarampo, Caxumba, Rubéola, Varicela'},

            # 4 Anos
            {'nome': 'DTP', 'dose': '2º Reforço', 'meses': 48, 'desc': ''},
            {'nome': 'Poliomielite (VOP)', 'dose': '2º Reforço', 'meses': 48, 'desc': ''},
            {'nome': 'Febre Amarela', 'dose': 'Reforço', 'meses': 48, 'desc': 'Reforço Obrigatório'},
            {'nome': 'Varicela', 'dose': '2ª Dose', 'meses': 48, 'desc': 'Catapora (se necessário)'},

            # 9 Anos
            {'nome': 'HPV4', 'dose': 'Dose Única', 'meses': 108, 'desc': 'Papilomavírus Humano (Meninos e Meninas)'},
        ]

        # Cria ou atualiza as vacinas
        for item in lista_vacinas:
            Vacina.objects.get_or_create(
                nome=item['nome'],
                dose_padrao=item['dose'],
                defaults={
                    'idade_alvo_meses': item['meses'],
                    'descricao_doenca': item['desc']
                }
            )

        # ==========================================
        # 2. POPULAR ESTOQUE (Lotes e Fabricantes)
        # ==========================================
        self.stdout.write('2. Gerando Estoque (Lotes e Fabricantes)...')
        
        # Limpa lotes antigos para evitar duplicidade ou lotes "órfãos"
        LoteVacina.objects.all().delete()
        
        # Lista de Fabricantes reais para dar veracidade ao teste
        fabricantes = [
            'Fiocruz/Bio-Manguinhos', 
            'Instituto Butantan', 
            'Pfizer', 
            'Sanofi Pasteur', 
            'GSK', 
            'Merck', 
            'AstraZeneca', 
            'Janssen'
        ]
        
        todas_vacinas = Vacina.objects.all()
        
        if not todas_vacinas.exists():
            self.stdout.write(self.style.ERROR('Erro: Nenhuma vacina encontrada. Algo deu errado no passo 1.'))
            return

        for v in todas_vacinas:
            # Seleciona aleatoriamente 2 fabricantes diferentes para esta vacina
            # Isso é CRUCIAL para testar o filtro "Fabricante <-> Lote" no front-end
            fabs_escolhidos = random.sample(fabricantes, 2)
            
            for fab in fabs_escolhidos:
                # Gera um lote estilo "FIO-1234"
                prefixo = fab[:3].upper().replace('/', '')
                numero = random.randint(1000, 9999)
                lote_num = f"{prefixo}-{numero}"
                
                LoteVacina.objects.create(
                    vacina=v,
                    numero_lote=lote_num,
                    fabricante=fab,
                    quantidade_disponivel=random.randint(50, 500), # Estoque inicial
                    validade=date.today() + timedelta(days=random.randint(180, 730)) # Validade entre 6 meses e 2 anos
                )

        self.stdout.write(self.style.SUCCESS(f'✅ SUCESSO! Vacinas configuradas e {LoteVacina.objects.count()} lotes de estoque criados.'))