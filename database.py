from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define o nome do arquivo do banco de dados SQLite
# Ele será criado na mesma pasta do seu projeto.
SQLALCHEMY_DATABASE_URL = "sqlite:///./cars_inventory.db"

# Cria o "motor" do SQLAlchemy
# connect_args={"check_same_thread": False} é necessário apenas para SQLite
# para permitir que o FastAPI o acesse.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Cria a classe de Sessão que usaremos para interagir com o DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria a classe Base da qual todos os seus modelos (tabelas)
# no models.py irão herdar.
Base = declarative_base()

# --- Função de Dependência (para o FastAPI) ---
# Isso é o que o FastAPI usará para obter uma sessão do banco de dados
# em cada requisição (rota) da API.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()