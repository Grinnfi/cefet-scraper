import requests
import json
from bs4 import BeautifulSoup
from scrap.get_turma_data import get_turma_data

SAVE_PATH = "data/turmas_matricula_data.json"

def get_turmas_matricula_data(session: requests.Session, matricula: str) -> dict[str:dict[str:str]]:
    """
    Extrai os dados das turmas matriculadas (Solicitada | Aceita/Matriculada) através do quadro de horários.
    Retorna um dicionário com o id da turma e seus respectivos dados.
    """
    quadro_horario_url = "https://alunos.cefet-rj.br/aluno/ajax/aluno/quadrohorario/quadrohorario.action?matricula="+ matricula
    quadro_horario_page = session.get(quadro_horario_url, allow_redirects=False)
    quadro_horario_soup = BeautifulSoup(quadro_horario_page.text, "html.parser") 

    turma_soup_list = quadro_horario_soup.find_all(class_="turmaqh")

    turma_id_data= {}
    for turma in turma_soup_list:
        turma_disciplina = turma.get_text(strip=True).split("T.")[0]
        turma_id = turma.find("a").get("href").split("turma=")[1]
        turma_matricula = turma.find("img").get("title")
        print(f"Checando dados de {turma_disciplina} | {turma_matricula}")
        turma_data = get_turma_data(session= session, turma_id=turma_id)
        turma_data["Matrícula"] = turma_matricula
        
        turma_id_data[turma_id] = turma_data

    with open (SAVE_PATH,"w") as f:
        json.dump(turma_id_data, f, indent= 4)
    print(f"Dados das turmas salvos em {SAVE_PATH}")

    return turma_id_data

if __name__ == "__main__":
    from login import login
    # from pprint import pprint
    user_data, session = login()
    turma_id_data = get_turmas_matricula_data(session=session, matricula=user_data["matricula"])
    # pprint(turma_id_data)