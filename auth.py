# Arquivo: auth.py
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import jwt 
from jwt import PyJWTError

# Importa as dependências dos nossos outros arquivos
# ISSO É O CORRETO:
from models import User # O User VEM do models.py
from schemas import TokenData, LoginRequest, Token # O resto VEM do schemas.py
from database import get_db, SessionLocal # Do database.py

# --- Configurações de Segurança ---
SECRET_KEY = "sua-chave-secreta-aqui" # Mude isso em produção
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # Token expira após 30 minutos

# Contexto de senha para hashing (usa bcrypt por padrão)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema OAuth2 para obter o token Bearer do header
# "login" é o URL da rota de login (ex: @app.post("/login"))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") 

# --- Funções de Hashing ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha simples corresponde ao hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera o hash da senha."""
    return pwd_context.hash(password)

# --- Funções de Banco de Dados de Usuário ---

def get_user(db: Session, username: str) -> Optional[User]:
    """Busca um usuário pelo username no banco de dados."""
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, username: str, password: str, disabled: bool = False):
    """Cria um novo usuário no banco de dados."""
    hashed_password = get_password_hash(password)
    db_user = User(
        username=username, 
        hashed_password=hashed_password, 
        disabled=disabled
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    print(f"-> Usuário de teste ('{username}') criado com sucesso no DB.")
    return db_user

def create_initial_user():
    """
    Função chamada na inicialização da API (no main.py)
    para garantir que o usuário de teste exista.
    """
    # Cria uma sessão de DB local apenas para esta operação
    db = SessionLocal()
    try:
        # Verifica se o usuário 'teste' já existe
        user = get_user(db, "teste")
        if not user:
            # Se não existir, cria o usuário 'teste' com a senha 'sua_senha_aqui'
            # ATENÇÃO: Se você mudou a senha no frontend_app.py, mude aqui também.
            create_user(db=db, username="teste", password="sua_senha_aqui")
    finally:
        db.close()

# --- Funções de Lógica de Autenticação ---

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Verifica se o usuário existe e se a senha está correta.
    Retorna o objeto User se for válido, senão None.
    """
    user = get_user(db, username)
    if not user:
        return None # Usuário não existe
    if not verify_password(password, user.hashed_password):
        return None # Senha incorreta
    
    return user # Autenticado

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria um token JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Adiciona o campo "sub" (subject) que é padrão para o username
    to_encode.update({"exp": expire, "sub": data.get("username")})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Funções de Dependência (Para rotas FastAPI) ---

def decode_access_token(token: str) -> str:
    """Valida o token e retorna o username (sub)."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # "sub" (subject) é onde armazenamos o username
        username: str = payload.get("sub") 
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido (sem subject)")
        return username
    except PyJWTError:
        # Lança 401 se o token estiver expirado ou for inválido
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais de autenticação inválidas ou token expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
) -> User:
    """Dependência FastAPI: Valida o token e retorna o objeto User do DB."""
    username = decode_access_token(token)
    user = get_user(db, username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário do token não encontrado no DB.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependência FastAPI: Valida o token E verifica se o usuário está ativo."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Usuário inativo")
    return current_user