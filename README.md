# DevPulse API

DevPulse é um sistema backend completo desenvolvido em Python (FastAPI) que monitora repositórios do GitHub automaticamente e analisa a qualidade do código através de relatórios, integrando heurísticas estáticas e feedback gerado por Inteligência Artificial.

## Principais Funcionalidades

- **Integração com GitHub**: Busca dados de repositórios, de commits e lê os arquivos alterados através da API nativa do GitHub.
- **Análise de Código**: Detecta suspeitas de violação de boas práticas, como envio de funções / arquivos enormes (large patches), detecção de loops muito aninhados e repetição de código.
- **Análise Assistida por IA**: Integra os diffs com LLMs (e possui simulação built-in) para adicionar sugestões personalizáveis às partes do código problemático.
- **Automação Escalonável:** Utiliza APScheduler assíncrono para garantir que novos commits e o repositório como um todo seja re-analisado de maneira recorrente a cada X minutos em background.
- **Geração de Relatórios**: Gera relatórios JSON contendo todos os dados, sugestões, scores de qualidade.

## Como Rodar

### 1. Requisitos
- Python 3.10+ instalado

### 2. Instalação e Configuração

Crie e ative um ambiente virtual:
```bash
python -m venv venv
# No Windows
venv\Scripts\activate
# No Linux/Mac:
# source venv/bin/activate
```

Instale as dependências requisitadas:
```bash
pip install -r requirements.txt
```

Crie um arquivo `.env` na raiz do projeto contendo as seguintes chaves (exemplo opcional):
```
DATABASE_URL=postgresql://user:password@localhost/devpulse
AI_API_KEY=your_api_key_here
GITHUB_TOKEN=your_github_token_here
```
> Obs: Por padrão (`USE_SQLITE=true`), o banco local em `sqlite` será usado caso as credenciais `postgresql` não funcionem na inicialização, ajudando o rápido desenvolvimento local, você pode alterar nas configs usando `environment variables`. Caso `AI_API_KEY` não for providenciada, a análise com a IA atuará de forma **simulada.**

### 3. Executando o Servidor 

Para inicializar a API:

```bash
uvicorn main:app --reload
```

O servidor começará a rodar em: `http://localhost:8000`.
Acesse o **Swagger UI Interativo** em: `http://localhost:8000/docs`.

### 4. Endpoints Principais
- `POST /api/repo`: Cadastra um novo repositório (ex. `{ "url": "https://github.com/fastapi/fastapi" }`).
- `GET /api/repo`: Lista todos os repositórios sendo vigiados.
- `POST /api/analyze`: Requere análises manuais forçadas sobre um `repository_id`.
- `GET /api/report/{id}`: Detalha a resposta estática + dicas da AI em formato unificado json.

## Estrutura do Código

- `main.py`: Entrypoint e base de eventos.
- `api/`: Definições das rotas HTTP, Controllers e Schemas.
- `services/`: Repositório da lógica de negócios, integrações, regras heurísticas, e comunicação com a IA.
- `models/`: Definições ORM (SQLAlchemy) das tabelas banco de relatórios.
- `scheduler/`: Tarefas periódicas mantidas pelo APScheduler.
- `database/`: Conectores.
- `utils/`: Loggers e utilitários da infraestrutura.
