import requests
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

def login() -> tuple[dict[str, str], requests.Session]:
    """
    Cria uma nova sessão autenticada utilizando as credenciais definidas no arquivo .env.

    Realiza o login no portal do aluno do CEFET-RJ, obtendo os cookies de autenticação
    e extraindo os dados básicos do usuário logado.

    Variáveis de ambiente necessárias:
        - user
        - password

    :return: Tupla contendo:
        - user_data: Dicionário com as chaves "nome" e "matricula"
        - session: Instância de requests.Session autenticada
    :rtype: tuple[dict[str, str], requests.Session]
    """
    print("Logando")
    
    load_dotenv()
    user = os.getenv('user')
    password = os.getenv('password')

    if not user or not password:
        raise ValueError("Salve usuario e senha no .env")

    session = requests.session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0",
        "Accept": "text/html",
        "Accept-Language": "pt-BR",
        "Referer": "https://cpa.cefet-rj.br/", # Evita Avaliação CPA 
    })

    # Pega o cookie de acesso - JSESSIONID
    main_page_url = "https://alunos.cefet-rj.br/aluno/"
    session.get(main_page_url)

    # Pega cookie de autentificação - JSESSIONIDSSO
    login_url = "https://alunos.cefet-rj.br/aluno/j_security_check"
    login_data = {"j_username": user, "j_password": password}
    login_response = session.post(login_url, data=login_data)

    if login_response.status_code == 403:
        raise PermissionError("Usuário ou senha inválidos")
    elif login_response.status_code != 200:
        raise RuntimeError(
            f"Erro HTTP no login: {login_response.status_code}"
        )

    login_soup = BeautifulSoup(login_response.text, 'html.parser')
    nome = login_soup.find(id = "menu").find('button').text
    matricula = login_soup.find(id='matricula')['value']

    print(f"Logado: {nome} | {matricula}")

    user_data = {"nome": nome, "matricula": matricula}

    return (user_data, session)