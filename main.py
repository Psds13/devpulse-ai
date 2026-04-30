from fastapi import FastAPI, Request, Form, Depends
from contextlib import asynccontextmanager
from database.config import engine, Base, get_db
from models.repository import Repository
from sqlalchemy.orm import Session
from api.routes import router
from scheduler.tasks import start_scheduler, scheduler
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import httpx

load_dotenv()

# =========================
# 🔁 LIFECYCLE
# =========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Criar tabelas no banco
        Base.metadata.create_all(bind=engine)

        # Iniciar scheduler
        start_scheduler()
        print("✅ Scheduler iniciado")

    except Exception as e:
        print(f"❌ Erro ao iniciar: {e}")

    yield

    try:
        scheduler.shutdown()
        print("🛑 Scheduler finalizado")
    except Exception as e:
        print(f"⚠️ Erro ao finalizar scheduler: {e}")


# =========================
# 🚀 APP
# =========================
app = FastAPI(
    title="DevPulse API",
    version="1.0.0",
    description="Monitor and analyze GitHub repositories using AI.",
    lifespan=lifespan
)

# =========================
# 🌍 CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# 🔗 API
# =========================
app.include_router(router, prefix="/api")

# =========================
# 📁 STATIC FILES
# =========================
os.makedirs("public", exist_ok=True)
app.mount("/static", StaticFiles(directory="public"), name="static")

# =========================
# 🧩 TEMPLATES
# =========================
templates = Jinja2Templates(directory="templates")

# =========================
# 🌐 ROTAS DO SITE
# =========================

# Página inicial (landing page)
@app.get("/", response_class=HTMLResponse)
def root():
    file_path = "public/index.html"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return HTMLResponse("<h1>DevPulse rodando 🚀</h1>")


# Dashboard principal
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    try:
        return templates.TemplateResponse(request=request, name="index.html", context={
            "request": request
        })
    except Exception as e:
        return HTMLResponse(f"<h1>Erro no dashboard</h1><p>{e}</p>")


# Página de repositórios
@app.get("/repos", response_class=HTMLResponse)
def repos_page(request: Request, db: Session = Depends(get_db)):
    try:
        db_repos = db.query(Repository).all()
        repos_list = [f"{repo.owner}/{repo.name}" if repo.owner and repo.name else repo.url for repo in db_repos]
        return templates.TemplateResponse(request=request, name="repos.html", context={
            "request": request,
            "repos": repos_list
        })
    except Exception as e:
        import traceback
        return HTMLResponse(
            f"<h1>Erro em /repos</h1><pre>{traceback.format_exc()}</pre>",
            status_code=500
        )


@app.post("/api/repos")
def add_repo(request: Request, repo_url: str = Form(...), db: Session = Depends(get_db)):
    owner = ""
    name = ""
    error_msg = None

    # Normaliza entrada: aceita "usuario/repo" ou URL completa
    clean_url = repo_url.strip()
    if "/" in clean_url and not clean_url.startswith("http"):
        parts = clean_url.split("/")
        if len(parts) == 2:
            owner, name = parts[0].strip(), parts[1].strip()
            clean_url = f"https://github.com/{owner}/{name}"
        else:
            error_msg = "Formato inválido. Use: usuario/repositorio"
    elif clean_url.startswith("https://github.com/"):
        parts = clean_url.replace("https://github.com/", "").split("/")
        if len(parts) >= 2:
            owner, name = parts[0], parts[1].replace(".git", "")
        else:
            error_msg = "URL do GitHub inválida."
    else:
        error_msg = "Formato inválido. Use: usuario/repositorio ou URL completa do GitHub."

    if not error_msg:
        # Verifica se o repositório realmente existe no GitHub
        github_token = os.getenv("GITHUB_TOKEN", "")
        headers = {"Accept": "application/vnd.github.v3+json"}
        if github_token:
            headers["Authorization"] = f"token {github_token}"

        try:
            response = httpx.get(
                f"https://api.github.com/repos/{owner}/{name}",
                headers=headers,
                timeout=8.0
            )
            if response.status_code == 404:
                error_msg = f"Repositório '{owner}/{name}' não encontrado no GitHub. Verifique o usuário e o nome."
            elif response.status_code == 403:
                error_msg = "Limite da API do GitHub atingido. Tente novamente em alguns minutos."
            elif response.status_code != 200:
                error_msg = f"Erro ao verificar repositório no GitHub (status {response.status_code})."
        except httpx.TimeoutException:
            error_msg = "Tempo de conexão esgotado ao verificar o GitHub. Tente novamente."
        except Exception as e:
            error_msg = f"Erro de rede ao verificar repositório: {str(e)}"

    if error_msg:
        # Reexibe a página de repos com a mensagem de erro
        db_repos = db.query(Repository).all()
        repos_list = [f"{r.owner}/{r.name}" if r.owner and r.name else r.url for r in db_repos]
        return templates.TemplateResponse(
            request=request, name="repos.html", context={
                "request": request,
                "repos": repos_list,
                "error": error_msg,
                "repo_input": repo_url
            }
        )

    # Salva no banco apenas se o repositório existe no GitHub e ainda não foi cadastrado
    existing = db.query(Repository).filter(Repository.url == clean_url).first()
    if not existing:
        new_repo = Repository(url=clean_url, owner=owner, name=name)
        db.add(new_repo)
        db.commit()

    return RedirectResponse(url="/repos", status_code=303)


# Página de relatório
@app.get("/report", response_class=HTMLResponse)
def report_page(request: Request):
    report_data = {
        "score": 85,
        "issues": [
            "Função muito longa",
            "Código duplicado"
        ]
    }

    try:
        return templates.TemplateResponse(request=request, name="report.html", context={
            "request": request,
            "report": report_data
        })
    except Exception as e:
        return HTMLResponse(f"<h1>Erro no report</h1><p>{e}</p>")