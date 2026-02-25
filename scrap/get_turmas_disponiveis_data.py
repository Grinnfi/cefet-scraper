import requests
import json
import os
from bs4 import BeautifulSoup
from scrap.get_cursos_disponiveis_id import get_cursos_disponiveis_id
from scrap.get_turma_data import get_turma_data

SAVE_PATH = "data/turmas_disponiveis_data.json"

def get_turmas_disponiveis_data(session: requests.Session, matricula: str) -> dict[str:dict[str:str]]:
    """
    Extrai os dados das turmas disponíveis para matricula.
    Retorna um dicionário com o id da turma e seus respectivos dados.
    """
    try:
        cursos_disponiveis_id = get_cursos_disponiveis_id(session=session, matricula=matricula)
    except Exception as error:
        print(error)
        cursos_disponiveis_path = "data/cursos_disponiveis_id.json"
        if os.path.exists(cursos_disponiveis_path) and input(f"Usar ultimos ids de cursos salvos em {cursos_disponiveis_path}? y\\n \n").lower() == "y":
            with open(cursos_disponiveis_path, "r") as f:
                cursos_disponiveis_id = json.load(f)
        else:
            return
        
    turma_id_data = {}

    for curso_id in cursos_disponiveis_id:
        ofertas_url = f"https://alunos.cefet-rj.br/aluno/ajax/aluno/matricula/oferta.action?matricula={matricula}&cursoDisc={curso_id}&exigeConsistencia=false&agruparPor=periodo"
        ofertas_page = session.get(ofertas_url, allow_redirects=False)

        ofertas_soup = BeautifulSoup(ofertas_page.text, 'html.parser')

        for periodo_soup in ofertas_soup.find_all(tipoinformacao="periodo"):
            periodo = periodo_soup.find("a").get_text()[-1]

            for disciplina_soup in periodo_soup.find_all(tipoinformacao="disciplina"):
                disciplina_content = disciplina_soup.find('li')
                disciplina_nome = disciplina_content.get('nomedisciplina')
                print(f"Checando dados de {disciplina_nome}")
                turma_id = disciplina_content.get('idturma')
                turma_data = get_turma_data(session= session, turma_id= turma_id)
                turma_data["Período"] = periodo
                turma_id_data[turma_id]= turma_data

    with open (SAVE_PATH,"w") as f:
        json.dump(turma_id_data, f, indent= 4)
    print(f"Dados das turmas salvos em {SAVE_PATH}")

    return turma_id_data

if __name__ == "__main__":
    from scrap.login import login
    user_data, session = login()
    get_turmas_disponiveis_data(session=session, matricula=user_data["matricula"])