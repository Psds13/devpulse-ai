from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from database.config import engine, Base
from api.routes import router
from scheduler.tasks import start_scheduler, scheduler
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import os

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
        return templates.TemplateResponse("index.html", {
            "request": request
        })
    except Exception as e:
        return HTMLResponse(f"<h1>Erro no dashboard</h1><p>{e}</p>")


# Página de repositórios
@app.get("/repos", response_class=HTMLResponse)
def repos_page(request: Request):
    repos_list = [
        "psds13/devpulse",
        "psds13/teste"
    ]

    try:
        return templates.TemplateResponse("repos.html", {
            "request": request,
            "repos": repos_list
        })
    except Exception as e:
        return HTMLResponse(f"<h1>Erro em repos</h1><p>{e}</p>")


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
        return templates.TemplateResponse("report.html", {
            "request": request,
            "report": report_data
        })
    except Exception as e:
        return HTMLResponse(f"<h1>Erro no report</h1><p>{e}</p>")