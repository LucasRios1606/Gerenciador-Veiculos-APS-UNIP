from fastapi import FastAPI, Depends, HTTPException, status, Form
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm
from database import get_db, engine
from schemas import CarroBase, CarroRead, LoginRequest, Token
from models import Base, Carro, User
from auth import (
    get_current_active_user, 
    authenticate_user, 
    create_access_token, 
    create_initial_user
)

app = FastAPI(title="API Gerenciador de Veículos")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    create_initial_user()

@app.post("/login", response_model=Token, tags=["Auth"])
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nome de usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"username": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/cars", response_model=List[CarroRead], tags=["Cars"])
def get_cars(
    # Filtros de texto
    make: Optional[str] = None,
    model: Optional[str] = None,
    fuel_type: Optional[str] = None,
    
    # Filtros de faixa (range)
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_horsepower: Optional[int] = None,
    max_horsepower: Optional[int] = None,
    
    # --- MOTOR ATUALIZADO (CC-Only) ---
    # Os nomes dos parâmetros continuam os mesmos para o frontend
    min_engine_size: Optional[int] = None,
    max_engine_size: Optional[int] = None,
    # -------------------------
    
    seating_capacity: Optional[int] = None,
    
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    statement = select(Carro)

    # Filtros de texto
    if make: statement = statement.where(Carro.make.ilike(f"%{make}%")) 
    if model: statement = statement.where(Carro.model.ilike(f"%{model}%"))
    if fuel_type: statement = statement.where(Carro.fuel_type.ilike(f"%{fuel_type}%"))

    # Filtros de faixa
    if min_price and min_price > 0: statement = statement.where(Carro.price >= min_price)
    if max_price and max_price > 0: statement = statement.where(Carro.price <= max_price)
    if min_horsepower and min_horsepower > 0: statement = statement.where(Carro.horsepower >= min_horsepower)
    if max_horsepower and max_horsepower > 0: statement = statement.where(Carro.horsepower <= max_horsepower)
    
    # --- MOTOR ATUALIZADO (CC-Only) ---
    # A lógica de filtro agora aponta para a coluna 'engine_cc'
    if min_engine_size and min_engine_size > 0:
        statement = statement.where(Carro.engine_cc >= min_engine_size)
    if max_engine_size and max_engine_size > 0:
        statement = statement.where(Carro.engine_cc <= max_engine_size)
    # -------------------------

    if seating_capacity and seating_capacity > 0:
        statement = statement.where(Carro.seating_capacity == seating_capacity)

    statement = statement.order_by(Carro.id)
    
    results = db.execute(statement).scalars().all()
    return results

@app.post("/cars", response_model=CarroRead, status_code=status.HTTP_201_CREATED, tags=["Cars"])
def create_car(
    car: CarroBase, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    db_car = Carro(**car.model_dump())
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car

# Rotas PUT e DELETE (Sem alterações)
@app.put("/cars/{car_id}", response_model=CarroRead, tags=["Cars"])
def update_car(
    car_id: int, 
    car: CarroBase,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    db_car = db.get(Carro, car_id)
    if not db_car:
        raise HTTPException(status_code=404, detail="Carro não encontrado")
    car_data = car.model_dump(exclude_unset=True)
    for key, value in car_data.items():
        setattr(db_car, key, value)
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car

@app.delete("/cars/{car_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Cars"])
def delete_car(
    car_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    db_car = db.get(Carro, car_id)
    if not db_car:
        raise HTTPException(status_code=404, detail="Carro não encontrado")
    db.delete(db_car)
    db.commit()
    return