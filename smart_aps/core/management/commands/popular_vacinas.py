from django.core.management.base import BaseCommand
from core.models import Vacina, RegistroVacina

class Command(BaseCommand):
    help = 'Popula o banco de dados com o Calendário Nacional de Vacinação (PDF Oficial)'

    def handle(self, *args, **kwargs):
        self.stdout.write("Limpando vacinas antigas...")
        # CUIDADO: Isso apaga vacinas e registros anteriores para recriar limpo
        RegistroVacina.objects.all().delete()
        Vacina.objects.all().delete()

        lista_vacinas = [
            # === AO NASCER  ===
            {
                "nome": "BCG",
                "dose": "Dose Única",
                "idade_meses": 0,
                "doenca": "Formas graves da Tuberculose"
            },
            {
                "nome": "Hepatite B",
                "dose": "Dose ao Nascer",
                "idade_meses": 0,
                "doenca": "Hepatite B"
            },

            # === 2 MESES  ===
            {
                "nome": "Penta (DTP+Hib+HB)",
                "dose": "1ª Dose",
                "idade_meses": 2,
                "doenca": "Difteria, Tétano, Coqueluche, Hib, Hepatite B"
            },
            {
                "nome": "Poliomielite (VIP)",
                "dose": "1ª Dose",
                "idade_meses": 2,
                "doenca": "Poliomielite (Paralisia Infantil)"
            },
            {
                "nome": "Pneumocócica 10V",
                "dose": "1ª Dose",
                "idade_meses": 2,
                "doenca": "Pneumonias, Meningites, Otites"
            },
            {
                "nome": "Rotavírus Humano",
                "dose": "1ª Dose",
                "idade_meses": 2,
                "doenca": "Diarreia por Rotavírus"
            },

            # === 3 MESES  ===
            {
                "nome": "Meningocócica C",
                "dose": "1ª Dose",
                "idade_meses": 3,
                "doenca": "Meningite C"
            },

            # === 4 MESES  ===
            {
                "nome": "Penta (DTP+Hib+HB)",
                "dose": "2ª Dose",
                "idade_meses": 4,
                "doenca": "Difteria, Tétano, Coqueluche, Hib, Hepatite B"
            },
            {
                "nome": "Poliomielite (VIP)",
                "dose": "2ª Dose",
                "idade_meses": 4,
                "doenca": "Poliomielite (Paralisia Infantil)"
            },
            {
                "nome": "Pneumocócica 10V",
                "dose": "2ª Dose",
                "idade_meses": 4,
                "doenca": "Pneumonias, Meningites, Otites"
            },
            {
                "nome": "Rotavírus Humano",
                "dose": "2ª Dose",
                "idade_meses": 4,
                "doenca": "Diarreia por Rotavírus"
            },

            # === 5 MESES  ===
            {
                "nome": "Meningocócica C",
                "dose": "2ª Dose",
                "idade_meses": 5,
                "doenca": "Meningite C"
            },

            # === 6 MESES  ===
            {
                "nome": "Penta (DTP+Hib+HB)",
                "dose": "3ª Dose",
                "idade_meses": 6,
                "doenca": "Difteria, Tétano, Coqueluche, Hib, Hepatite B"
            },
            {
                "nome": "Poliomielite (VIP)",
                "dose": "3ª Dose",
                "idade_meses": 6,
                "doenca": "Poliomielite (Paralisia Infantil)"
            },
            
            # === 9 MESES  ===
            {
                "nome": "Febre Amarela",
                "dose": "Dose Inicial",
                "idade_meses": 9,
                "doenca": "Febre Amarela"
            },

            # === 12 MESES (1 ANO)  ===
            {
                "nome": "Tríplice Viral (SCR)",
                "dose": "1ª Dose",
                "idade_meses": 12,
                "doenca": "Sarampo, Caxumba, Rubéola"
            },
            {
                "nome": "Pneumocócica 10V",
                "dose": "Reforço",
                "idade_meses": 12,
                "doenca": "Pneumonias, Meningites, Otites"
            },
            {
                "nome": "Meningocócica ACWY",
                "dose": "Dose Única",
                "idade_meses": 12,
                "doenca": "Meningites A, C, W, Y"
            },

            # === 15 MESES [cite: 14, 16] ===
            {
                "nome": "Poliomielite (VOP/VIP)", # Geralmente VOP no reforço, mas seguindo tabela VIP
                "dose": "1º Reforço",
                "idade_meses": 15,
                "doenca": "Poliomielite"
            },
            {
                "nome": "DTP",
                "dose": "1º Reforço",
                "idade_meses": 15,
                "doenca": "Difteria, Tétano, Coqueluche"
            },
            {
                "nome": "Tetraviral (SCRV)",
                "dose": "Dose Única",
                "idade_meses": 15,
                "doenca": "Sarampo, Caxumba, Rubéola, Varicela"
            },
            {
                "nome": "Hepatite A",
                "dose": "Dose Única",
                "idade_meses": 15,
                "doenca": "Hepatite A"
            },

            # === 4 ANOS (48 MESES)  ===
            {
                "nome": "DTP",
                "dose": "2º Reforço",
                "idade_meses": 48,
                "doenca": "Difteria, Tétano, Coqueluche"
            },
            {
                "nome": "Poliomielite (VOP)", # Gotinha
                "dose": "2º Reforço",
                "idade_meses": 48,
                "doenca": "Poliomielite"
            },
            {
                "nome": "Febre Amarela",
                "dose": "Reforço",
                "idade_meses": 48,
                "doenca": "Febre Amarela"
            },
            {
                "nome": "Varicela",
                "dose": "Dose Única", # Atenuada
                "idade_meses": 48,
                "doenca": "Varicela (Catapora)"
            },
            
            # === 9 ANOS (108 MESES)  ===
            {
                "nome": "HPV",
                "dose": "1ª Dose",
                "idade_meses": 108,
                "doenca": "Papilomavírus Humano (Câncer)"
            },
             {
                "nome": "HPV",
                "dose": "2ª Dose", # Esquema varia, mas comum ser 6 meses depois
                "idade_meses": 114,
                "doenca": "Papilomavírus Humano (Câncer)"
            },
        ]

        for item in lista_vacinas:
            Vacina.objects.create(
                nome=item["nome"],
                dose_padrao=item["dose"],
                idade_alvo_meses=item["idade_meses"],
                descricao_doenca=item["doenca"]
            )

        self.stdout.write(self.style.SUCCESS(f'Sucesso! {len(lista_vacinas)} vacinas do calendário oficial cadastradas.'))