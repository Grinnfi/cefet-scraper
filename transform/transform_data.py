import json
import unicodedata
import re
import os
from datetime import date

SAVE_PATH = "output/matricula_data.json"

DISCIPLINAS_APROVADAS_PATH = "data/disciplinas_aprovadas.json"
REQUISITOS_PATH = "curriculum/requisitos.json"
TURMAS_DISPONIVEIS_DATA_PATH = "data/turmas_disponiveis_data.json"
TURMAS_MATRICULA_DATA_PATH = "data/turmas_matricula_data.json"

DIAS_SEMANA = {
    "2": "SEG",
    "3": "TER",
    "4": "QUA",
    "5": "QUI",
    "6": "SEX",
    "7": "SAB",
    "1": "DOM"
}


def clean_str(text: str) -> str:
    """
    Remove múltiplos espaços, acentos, parênteses (e conteúdo após),
    e converte para caixa alta.
    """
    """
    Exemplo:
    Equações Diferenciais Parciais e Séries (EDPS) -> EQUACOES DIFERENCIAIS PARCIAIS E SERIES
    """
    # Remove conteúdo entre parênteses e o que vem depois
    text = text.split("(")[0]

    # Normaliza e remove acentos
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")

    # Remove múltiplos espaços e strip
    text = re.sub(r"\s+", " ", text).strip()

    return text.upper()


def transform_data(id, data, requisitos):
    """
    Trata as informações da turma para o formato esperado
    """

    code = clean_str(data["Disciplina"])
    name = clean_str(data["Nome"])
    degree = clean_str(data['Curso'])

    if "CURSO DE " in degree:
        degree = degree.split("CURSO DE ")[1]
    if "- " in degree:
        degree = degree.split("- ")[1]
        
    if data['Docentes']:
        professors = [docente['Nome do Docente'] for docente in data['Docentes']]
    else:
        professors = []

    if 'Período' in data:
        period = data['Período']
    elif code in requisitos and 'periodo' in requisitos[code]:
        period = requisitos[code]['periodo']
    else:
        period = ""

    if data['Carga Horária Realizada']:
        credits = int(data['Carga Horária Realizada'])//18
    else:
        credits = 0

    occupancy = {"total": data['Vagas Totais'], "occupied": data['Total de Matrículas'], "requested": data['Total de Solicitações']}
    
    slots = []
    if data['Horários']:
        for horario in data['Horários']:
            day = DIAS_SEMANA[horario['Dia da Semana'][0]]
            start = horario['Hora Início']
            end = horario['Hora Fim']
            slots.append({"day": day, "start": start, "end": end})
    if code in requisitos and 'pre_requisitos' in requisitos[code]:
        pre_requisits = requisitos[code]['pre_requisitos']
    else:
        pre_requisits = []

    course_dict = {
        "id": id,
        "code": code,
        "name": name,
        "degree": degree,
        "professors": professors,
        "period": period,
        "credits": credits,
        "occupancy": occupancy,
        "slots": slots,
        "pre_requisits": pre_requisits
    }
    return course_dict

def run_transformation():
    """
    Orquestra o fluxo de carregamento, limpeza e consolidação dos dados raspados.
    Este processo realiza as seguintes etapas:
    1. Carrega os dados brutos de disciplinas aprovadas, requisitos e turmas (disponíveis e matriculadas).
    2. Normaliza e limpa as strings de nomes de disciplinas e cursos.
    3. Cruza os dados das turmas com suas respectivas ementas e pré-requisitos.
    4. Identifica o status de matrícula do usuário (confirmada vs. solicitada).
    5. Adiciona metadados de versão e data de atualização.
    6. Exporta o resultado consolidado para o arquivo 'matricula_data_clean.json'.
    Raises:
        FileNotFoundError: Se algum dos arquivos de entrada obrigatórios não for encontrado.
        json.JSONDecodeError: Se houver erro na formatação dos arquivos JSON de origem.
    """
    if os.path.exists(DISCIPLINAS_APROVADAS_PATH):
        with open (DISCIPLINAS_APROVADAS_PATH, "r") as f:
            disciplinas_aprovadas = json.load(f)
    else:
        disciplinas_aprovadas = []

    if os.path.exists(REQUISITOS_PATH):
        with open (REQUISITOS_PATH, "r") as f:
            requisitos = json.load(f)
    else:
        requisitos = []

    if os.path.exists(TURMAS_DISPONIVEIS_DATA_PATH):
        with open (TURMAS_DISPONIVEIS_DATA_PATH, "r") as f:
            turmas_disponiveis_data = json.load(f)
    else:
        turmas_disponiveis_data = []

    if os.path.exists(TURMAS_MATRICULA_DATA_PATH):
        with open (TURMAS_MATRICULA_DATA_PATH, "r") as f:
            turmas_matricula_data = json.load(f)
    else:
        turmas_matricula_data = []

    # Limpando as entradas
    requisitos_clean = {}
    for disciplina in requisitos:
        disciplina_nome = clean_str(disciplina["disciplina"])
        pre_requisito_list = []
        for pre_requisito in disciplina['pre_requisitos']:
            pre_requisito_clean = clean_str(pre_requisito)
            pre_requisito_list.append(pre_requisito_clean)

        requisitos_clean[disciplina_nome] = {"pre_requisitos":pre_requisito_list, "periodo": disciplina["periodo"]}
    
    confirmed_course_ids = []
    planned_course_ids = []
    courses = []

    for id, data in turmas_disponiveis_data.items():
        courses.append(transform_data(id, data, requisitos_clean))

    for id, data in turmas_matricula_data.items():
        courses.append(transform_data(id, data, requisitos_clean))
        status = data["Matrícula"]
        if status == "Aceita/Matriculada":
            confirmed_course_ids.append(id)
        elif status == "Solicitada":
            planned_course_ids.append(id)

    # Metadados
    semester = f"{data['Ano']}.{data['Semestre']}"
    version = "1.0"
    last_update = date.today().isoformat()

    full_package = {
        "version": version,
        "metadata":{
            "semester": semester,
            "last_update": last_update,
        },
        "courses": courses,
        "user":{
            "confirmed_course_ids": confirmed_course_ids,
            "planned_course_ids": planned_course_ids,
            "completed_courses_codes": [clean_str(disciplina) for disciplina in disciplinas_aprovadas]
        }
    }

    with open(SAVE_PATH, "w") as f:
        json.dump(full_package, f, indent= 4)
    print("Dados salvos em ", SAVE_PATH)


if __name__ == "__main__":
    run_transformation()