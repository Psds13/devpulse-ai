import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Garante que o .env seja lido antes de acessar as variáveis
load_dotenv()

# fallback for local development if postgres isn't running is sqlite
if os.getenv("USE_SQLITE", "true").lower() == "true":
    DATABASE_URL = "sqlite:///./devpulse.db"
else:
    DATABASE_URL = os.getenv("DATABASE_URL", "")

    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL não definida. Configure a variável de ambiente no Render.")

    # ⚠️ Fix necessário para o Render: ele gera URLs com "postgres://"
    # mas o SQLAlchemy 1.4+ exige "postgresql://"
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# connect_args apenas necessário para SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
