import os
from scrap.login import login
from scrap.get_disciplinas_aprovadas import get_disciplinas_aprovadas
from scrap.get_turmas_matricula_data import get_turmas_matricula_data
from scrap.get_turmas_disponiveis_data import get_turmas_disponiveis_data
from transform.transform_data import run_transformation
from transform.generate_ics import generate_ics

def main():
    """
    Função principal que orquestra o fluxo completo de raspagem e transformação de dados.
    
    O fluxo consiste em:
    1. Realizar login no Portal do Aluno.
    2. Raspagem das disciplinas aprovadas (histórico).
    3. Raspagem das turmas em que o aluno está matriculado ou solicitou.
    4. Raspagem de todas as turmas disponíveis para o curso do aluno.
    5. Transformação e consolidação de todos os dados para o formato clean.
    """
    print("=== Iniciando CEFET Scraper ===")
    
    try:
        # 1. Login
        user_data, session = login()
        matricula = user_data["matricula"]
        
        # Garantir que a pasta data existe
        os.makedirs("data", exist_ok=True)
        
        # 2. Raspagem de Disciplinas Aprovadas
        print("\n[1/3] Raspando disciplinas aprovadas...")
        get_disciplinas_aprovadas(session=session, matricula=matricula)
        
        # 3. Raspagem de Turmas Matriculadas
        print("\n[2/3] Raspando turmas matriculadas/solicitadas...")
        turmas_matricula_data = get_turmas_matricula_data(session=session, matricula=matricula)
        
        # 4. Raspagem de Turmas Disponíveis
        print("\n[3/3] Raspando turmas disponíveis (isso pode demorar)...")
        get_turmas_disponiveis_data(session=session, matricula=matricula)
        
        print("\n=== Raspagem finalizada com sucesso! ===")

        # 5. Transformação de Dados
        print("\nIniciando transformação de dados...")
        run_transformation()

        # 6. Geração de ICS
        print("\nSalvando agenda...")
        generate_ics(turmas_data=turmas_matricula_data)
        
        
    except PermissionError:
        print("\nErro: Usuário ou senha inválidos no arquivo .env")
    except ValueError as e:
        print(f"\nErro de configuração: {e}")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")

if __name__ == "__main__":
    main()
