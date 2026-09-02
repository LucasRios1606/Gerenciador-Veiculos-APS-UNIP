# Arquivo: models.py
from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.orm import relationship
from database import Base 

# --- Tabela Carro ---
class Carro(Base):
    __tablename__ = "carros"

    id = Column(Integer, primary_key=True, index=True)
    make = Column(String, index=True) 
    model = Column(String, index=True) 
    price = Column(Float) 
    
    # --- MOTOR ATUALIZADO (CC-Only) ---
    engine_cc = Column(Integer, index=True) # Ex: 3990 (para filtros)
    engine_size_display = Column(String) # Ex: "3990 cc" (para display)
    # -------------------------
    
    horsepower = Column(Integer, index=True) 
    torque = Column(String) 
    fuel_type = Column(String, index=True) 
    seating_capacity = Column(Integer, index=True) 
    
    def __repr__(self):
        return f"<Carro(id={self.id}, make='{self.make}', model='{self.model}')>"

# --- Tabela Usuário (Sem alterações) ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False) 
    disabled = Column(Boolean, default=False)
    full_name = Column(String, nullable=True)