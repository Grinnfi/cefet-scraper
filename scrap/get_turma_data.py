import requests
from bs4 import BeautifulSoup

def _parse_table_por_titulo(soup, titulo):
    """
    Faz o parse nas tabelas das turmas
    """
    container = soup.find("div", title=titulo)
    table = container.find("table")

    headers = [
        th.get_text(strip=True)
        for th in table.select("thead th")
    ]

    dados = []
    for row in table.select("tbody tr"):
        valores = [
            td.get_text(strip=True)
            for td in row.find_all("td")
        ]
        dados.append(dict(zip(headers, valores)))
    return dados

def get_turma_data(session: requests.Session, turma_id: str) -> dict[str:str]:
    """
    Checa a página da turma e retorna um dicionário.
    """
    """
    Exemplo:
    {'Ano': '2026',
    'Carga Horária Realizada': '72',
    'Curso': 'MAR - CURSO  DE BACHARELADO EM CIÊNCIA DA COMPUTAÇÃO',
    'Disciplina': 'ADMINISTRAÇÃO DE BANCO DE DADOS',
    'Docentes': [{'Nome do Docente': 'JORGE DE ABREU SOARES',
                'Papel do Docente': 'Colaborador'}],
    'Horários': [{'Aula': 'Teórica',
                'Data Fim Período': '02/07/2026',
                'Data Início Período': '23/02/2026',
                'Dia da Semana': '2 - Segunda-feira',
                'Hora Fim': '18:10',
                'Hora Início': '14:35'}],
    'Nome': '951522',
    'Total de Matrículas': '25',
    'Total de Solicitações': '0',
    'Vagas Ocupadas': '25',
    'Vagas Totais': '40'}
    """
    turma_url = "https://alunos.cefet-rj.br/aluno/aluno/turma.action?turma="+ turma_id
    turma_page = session.get(turma_url)
    turma_soup = BeautifulSoup(turma_page.text, 'html.parser')
    turma_data = {}

    container = turma_soup.find("div", title="Dados Gerais")

    # Vagas (tabela interna)
    for row in container.select(".tablevagas tr"):
        label = row.select_one(".label")
        value = row.find("strong")
        if label and value:
            turma_data[label.get_text(strip=True).replace(":", "")] = value.get_text(strip=True)

    # Campos de texto soltos
    labels = container.select("span.label")
    for lbl in labels:
        texto = lbl.get_text(strip=True).replace(":", "")
        parent = lbl.parent
        valor = parent.get_text(strip=True).replace(lbl.get_text(strip=True), "").strip()
        if valor and texto not in turma_data:
            turma_data[texto] = valor

    for table_name in ['Docentes', 'Horários', 'Espaço Físico']:
        try:
            turma_data[table_name] = _parse_table_por_titulo(turma_soup, table_name)
        except: # Tabela vazia
            turma_data[table_name] = None

    turma_data["Nome"] = turma_soup.find(class_="topopage").get_text().split("\xa0")[1]

    # Período = "1º Semestre"
    turma_data["Semestre"] = turma_data["Período"][0]
    del turma_data["Período"]

    return turma_data

if __name__ == "__main__":
    import sys
    from scrap.login import login
    from pprint import pprint

    if len(sys.argv) > 1:
        user_data, session = login()
        turma_dados = get_turma_data(session=session, turma_id=sys.argv[1])
        pprint(turma_dados)