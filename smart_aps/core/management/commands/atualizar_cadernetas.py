from django.core.management.base import BaseCommand
from core.models import Crianca, Vacina, RegistroVacina
from datetime import date

class Command(BaseCommand):
    help = 'Gera a caderneta de vacinação para crianças que ficaram sem registro'

    def handle(self, *args, **kwargs):
        criancas = Crianca.objects.all()
        vacinas = Vacina.objects.all()
        
        total_criadas = 0
        hoje = date.today()

        self.stdout.write(f"Encontradas {criancas.count()} crianças e {vacinas.count()} vacinas no sistema.")

        for crianca in criancas:
            # Calcula idade em meses para já marcar atrasos se necessário
            idade_meses = (hoje.year - crianca.data_nascimento.year) * 12 + (hoje.month - crianca.data_nascimento.month)

            for vacina in vacinas:
                # O get_or_create garante que não vamos duplicar se a criança já tiver essa vacina
                registro, created = RegistroVacina.objects.get_or_create(
                    crianca=crianca,
                    vacina=vacina,
                    defaults={'status': 'PENDENTE'}
                )

                if created:
                    # Se acabamos de criar, verifica se já está atrasada
                    if idade_meses > vacina.idade_alvo_meses:
                        registro.status = 'ATRASADA'
                        registro.save()
                    
                    total_criadas += 1

        self.stdout.write(self.style.SUCCESS(f'Concluído! {total_criadas} novos registros de vacina foram gerados para os pacientes antigos.'))