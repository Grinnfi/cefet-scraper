# CEFET Scraper

Ferramenta automatizada para extração e processamento de dados do Portal do Aluno do CEFET-RJ. Este projeto realiza a raspagem de turmas disponíveis, disciplinas cursadas e turmas matriculadas, consolidando tudo em um formato JSON pronto para visualização.

## 🚀 Funcionalidades

- **Raspagem Completa**: Obtém dados de disciplinas aprovadas, turmas matriculadas/solicitadas e oferta de turmas.
- **Transformação de Dados**: Limpa e organiza os dados em um formato padronizado.
- **Gestão de Requisitos**: Suporte para pré-requisitos e períodos das disciplinas.
- **Geração de ICS**: Geração de arquivo ICS para importação em calendários.

## 🛠️ Pré-requisitos

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (Recomendado para gerenciamento de dependências)

## 📦 Instalação e Configuração

1. Clone o repositório:
```bash
git clone https://github.com/Grinnfi/cefet-scraper.git
cd cefet_scraper
```

2. Crie e configure o arquivo `.env`:
```bash
cp .env.example .env
```
Edite o arquivo `.env` com sua matrícula e senha do Portal do Aluno.

> Sempre tome cuidado ao usar seus dados de login. As credenciais do `.env` são utilizadas apenas em `scrap/login.py`, repassando apenas os cookies (temporários) da sessão para as requisições.

3. Instale as dependências:

**Usando [uv](https://github.com/astral-sh/uv) (Recomendado):**
```bash
uv sync
```

**Usando pip:**
```bash
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
pip install -r requirements.txt
```


## 📖 Como Usar

### 1. Preparando os Requisitos
Como não encontrei uma forma consistente de obter os requisitos dos cursos, recomendamos o seguinte método:
1. Obtenha o PDF da grade curricular do seu curso.
2. Utilize uma LLM (como ChatGPT, Claude ou Gemini) com o seguinte prompt:
   > "Extraia as disciplinas deste PDF e gere um JSON no seguinte formato: `[{"disciplina": "NOME", "pre_requisitos": ["REQ1"], "periodo": "1"}]`. Salve o período de matérias optativas como "0"."
3. Salve o resultado em `curriculum/requisitos.json`.

### 2. Executando o Scraper
Basta executar o ponto de entrada principal:
```bash
python main.py
```
Isso irá:
1. Logar no portal.
2. Salvar os dados brutos em `data/` (ignorados pelo Git).
3. Transformar os dados brutos em `output/matricula_data.json`.
4. Gerar o arquivo `output/agenda.ics`.

## 🎨 Visualização

O arquivo `output/matricula_data.json` gerado por este scraper é compatível com o projeto de visualização web:

- **Repositório**: [Grinnfi/planejador-de-matricula](https://github.com/Grinnfi/planejador-de-matricula)
- **Página Web**: [Planejador de Matrícula](https://grinnfi.github.io/planejador-de-matricula)

## 📅 ICS - Arquivo de Agenda

O arquivo `output/agenda.ics` gerado por este scraper pode ser importado para o calendários como o Google Agenda, Outlook, etc.

---
*Este projeto não possui vínculo oficial com o CEFET-RJ.*
