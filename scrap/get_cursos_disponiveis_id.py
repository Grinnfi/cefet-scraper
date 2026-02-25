import requests
from bs4 import BeautifulSoup
import json

# Só pode ser usado quando a seleção de matérias está aberta
def get_cursos_disponiveis_id (session: requests.Session, matricula: str) -> list[str]:
    """
    Retorna o id dos cursos com turmas disponíveis para a matrícula.
    Usa a página de matrícula (é disponível apenas quando a fase de matrícula está aberta).
    """
    print ("Checando cursos disponiveis.")
    matricula_url = "https://alunos.cefet-rj.br/aluno/aluno/matricula/oferta.action?matricula="+ matricula
    matricula_page = session.get(matricula_url, allow_redirects=False)
    matricula_soup = BeautifulSoup(matricula_page.text, "html.parser") 
    cursos_soup = matricula_soup.find(id ="cursos")

    if cursos_soup is None:
        raise Exception("Página de matrícula indisponível")
    curso_id_list = []
    for curso in cursos_soup.find_all("option"):
        id = curso.get("value")
        curso_id_list.append(id)

    with open ("data/cursos_disponiveis_id.json","w") as f:
        json.dump(curso_id_list, f)
    
    return curso_id_list

if __name__ == "__main__":
    from scrap.login import login
    from pprint import pprint
    user_data, session = login()
    curso_id_list = get_cursos_disponiveis_id(session=session, matricula=user_data["matricula"])
    pprint(curso_id_list)