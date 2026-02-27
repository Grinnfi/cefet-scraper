import os
import unicodedata
import json
from datetime import datetime, timedelta
from scrap.get_turmas_matricula_data import get_turmas_matricula_data

OUTPUT_PATH = "output/agenda.ics"
TURMAS_MATRICULA_DATA_PATH = "data/turmas_matricula_data.json"

def generate_ics(turmas_data = None):
    """
    Gera um arquivo .ics (iCalendar) a partir dos dados das turmas matriculadas.
    """
    if not turmas_data:
        with open(TURMAS_MATRICULA_DATA_PATH, "r") as f:
            turmas_data = json.load(f)
    
    # Mapeamento de dias (CEFET -> iCalendar)
    # 1: Domingo, 2: Segunda, ..., 7: Sábado
    day_map_ics = {
        "1": "SU", "2": "MO", "3": "TU", "4": "WE", "5": "TH", "6": "FR", "7": "SA"
    }
    
    # Mapeamento de dias (CEFET -> Python weekday())
    # Python: 0=Mon, 6=Sun
    day_map_py = {
        "1": 6, "2": 0, "3": 1, "4": 2, "5": 3, "6": 4, "7": 5
    }

    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//CEFET Scraper//PT",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH"
    ]

    def norm(text):
        """
        Normaliza a codificação de caracteres para que o arquivo .ics seja válido.
        """
        if not text:
            return ""
        return unicodedata.normalize("NFD", text)

    for turma_id, data in turmas_data.items():
        disciplina = norm(data.get("Disciplina"))
        turma_nome = norm(data.get("Nome", ""))
        horarios = data.get("Horários", [])
        espacos = data.get("Espaço Físico", [])
        docentes = data.get("Docentes", [])
        
        if not horarios:
            continue

        # Formata a localização (se houver)
        location = ""
        if espacos:
            espaco = espacos[0] # Usando o primeiro registro de espaço por simplicidade
            loc_parts = []
            if espaco.get("Nome do Prédio"): loc_parts.append(norm(espaco["Nome do Prédio"]))
            if espaco.get("Número da Sala"): loc_parts.append(norm(espaco["Número da Sala"]))
            if espaco.get("Espaço Físico"): loc_parts.append(norm(espaco["Espaço Físico"]))
            location = ", ".join(loc_parts)

        # Formata a descrição
        desc_parts = []
        if docentes:
            profs = [norm(d["Nome do Docente"]) for d in docentes if d.get("Nome do Docente")]
            desc_parts.append("Docentes: " + ", ".join(profs))
        description = "\\n".join(desc_parts)

        for h in horarios:
            dia_cefet = h['Dia da Semana'][0]
            dia_ics = day_map_ics.get(dia_cefet)
            target_weekday = day_map_py.get(dia_cefet)

            if not dia_ics or target_weekday is None:
                continue

            start_date_str = h.get('Data Início Período')
            end_date_str = h.get('Data Fim Período')
            
            if not start_date_str or not end_date_str:
                continue
                
            try:
                start_dt = datetime.strptime(start_date_str, "%d/%m/%Y")
                end_dt = datetime.strptime(end_date_str, "%d/%m/%Y")

                # Encontrar a primeira ocorrência do dia da semana a partir da data de início
                days_ahead = target_weekday - start_dt.weekday()
                if days_ahead < 0:
                    days_ahead += 7
                first_occurrence = start_dt + timedelta(days=days_ahead)

                h_start_str = h.get('Hora Início', '00:00')
                h_end_str = h.get('Hora Fim', '00:00')
                
                h_start = h_start_str.split(':')
                h_end = h_end_str.split(':')

                dt_start = first_occurrence.replace(hour=int(h_start[0]), minute=int(h_start[1]))
                dt_end = first_occurrence.replace(hour=int(h_end[0]), minute=int(h_end[1]))

                # UNTIL deve ser no formato UTC (terminando em Z) ou com data/hora completa
                # Definimos como o fim do dia final do período
                until_str = end_dt.strftime("%Y%m%dT235959Z")

                ics_lines.append("BEGIN:VEVENT")
                ics_lines.append(f"SUMMARY:{disciplina}")
                ics_lines.append(f"DTSTART:{dt_start.strftime('%Y%m%dT%H%M%S')}")
                ics_lines.append(f"DTEND:{dt_end.strftime('%Y%m%dT%H%M%S')}")
                ics_lines.append(f"RRULE:FREQ=WEEKLY;BYDAY={dia_ics};UNTIL={until_str}")
                if location:
                    ics_lines.append(f"LOCATION:{location}")
                ics_lines.append(f"DESCRIPTION:{description}")
                ics_lines.append(f"UID:{turma_id}-{dia_ics}-{dt_start.strftime('%H%M')}@cefet-scraper")
                ics_lines.append("END:VEVENT")
            except Exception as e:
                print(f"Erro ao processar horário para {disciplina}: {e}")

    ics_lines.append("END:VCALENDAR")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(ics_lines))
    
    print(f"Arquivo ICS gerado com sucesso em {OUTPUT_PATH}")

if __name__ == "__main__":
    from scrap.login import login
    
    user_data, session = login()
    turmas_data = get_turmas_matricula_data(session, user_data["matricula"])

    generate_ics(turmas_data)