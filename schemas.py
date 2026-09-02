# Arquivo: schemas.py
from pydantic import BaseModel
from typing import Optional

# --- Modelos Pydantic para Carro ---
class CarroBase(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    price: Optional[float] = None
    
    # --- MOTOR ATUALIZADO (CC-Only) ---
    engine_cc: Optional[int] = None # O número (ex: 3990)
    engine_size_display: Optional[str] = None # O texto (ex: "3990 cc")
    # -------------------------
    
    horsepower: Optional[int] = None
    torque: Optional[str] = None
    fuel_type: Optional[str] = None
    seating_capacity: Optional[int] = None

class CarroRead(CarroBase):
    id: int
    class Config:
        from_attributes = True

# --- Modelos Pydantic para Autenticação (Sem alterações) ---
class Token(BaseModel):
    access_token: str
    token_type: str
class TokenData(BaseModel):
    username: Optional[str] = None
class LoginRequest(BaseModel):
    username: str
    password: str