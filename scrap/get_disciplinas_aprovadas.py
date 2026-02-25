import requests
from bs4 import BeautifulSoup
import json

def get_disciplinas_aprovadas (session: requests.Session, matricula: str):
    """
    Extrai as disciplinas aprovadas do histórico escolar.
    """
    notas_page = session.get(f"https://alunos.cefet-rj.br/aluno/aluno/nota/nota.action?matricula={matricula}")
    notas_soup = BeautifulSoup(notas_page.text, 'html.parser')

    peridos = notas_soup.find_all("table", class_="table-turmas")

    aprovados = []

    for tabela in peridos:

        for linha in tabela.tbody.find_all("tr"):
            colunas = linha.find_all("td")
            
            disciplina = colunas[0].get_text(strip=True).split("  ")[0] # limpa texto depois dos espaços
            situacao = colunas[1].get_text(strip=True)

            if situacao == 'Aprovado' or situacao == 'Isento':
                aprovados.append(disciplina)
    
    with open("data/disciplinas_aprovadas.json", "w") as json_file:
        json.dump(aprovados, json_file, indent=4)
    print("Disciplinas Aprovadas salvas")

    return aprovados

if __name__ == "__main__":
    from scrap.login import login
    user_data, session = login()
    get_disciplinas_aprovadas(session=session, matricula=user_data["matricula"])