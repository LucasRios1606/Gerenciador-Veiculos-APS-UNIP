# Arquivo: import_data.py
import pandas as pd
import re 
from sqlalchemy.orm import Session
from database import Base, SessionLocal, engine
from models import Carro, User
from auth import get_password_hash 

CSV_FILE_NAME = "Cars Datasets 2025.csv"

def create_db_and_tables():
    Base.metadata.drop_all(bind=engine) 
    Base.metadata.create_all(bind=engine)
    print("-> Tabelas recriadas e banco de dados limpo.")

def create_test_user(db: Session):
    """Cria um usuário de teste padrão."""
    
    # --- DADOS DE LOGIN ATUALIZADOS ---
    TEST_USERNAME = "@administrador"
    TEST_PASSWORD = "Adm@2025"
    # ----------------------------------
    
    hashed_password = get_password_hash(TEST_PASSWORD) 
    
    db_user = User(
        username=TEST_USERNAME, 
        hashed_password=hashed_password,
        full_name="Administrador" # Nome completo atualizado
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # (Não vamos imprimir a senha no log por segurança)
    print(f"-> Usuário de teste ('{TEST_USERNAME}') criado com sucesso.")

# --- Funções de Limpeza de Dados ---
def clean_price(value):
    if not isinstance(value, str): return None
    cleaned = re.sub(r'[$,\s]', '', value)
    try: return float(cleaned)
    except (ValueError, TypeError): return None

def clean_horsepower(value):
    if not isinstance(value, str): return None
    match = re.search(r'(\d+)', value)
    try: return int(match.group(1)) if match else None
    except (ValueError, TypeError): return None

def clean_seats(value):
    try: return int(value)
    except (ValueError, TypeError): return None

def get_engine_cc(value):
    if not isinstance(value, str):
        return None
    match = re.search(r'([\d\.]+)', value) 
    if not match:
        return None
    try:
        return int(float(match.group(1))) 
    except (ValueError, TypeError):
        return None

def import_cars_data(db: Session):
    """Lê o CSV, limpa os dados e insere os carros no DB."""
    try:
        df = pd.read_csv(CSV_FILE_NAME)
        df.columns = df.columns.str.lower().str.strip()
    except FileNotFoundError:
        print(f"ERRO: Arquivo CSV '{CSV_FILE_NAME}' não encontrado.")
        return

    print(f"--- Iniciando importação de dados do arquivo {CSV_FILE_NAME} ---")
    
    cars_to_insert = []
    
    for index, row in df.iterrows():
        price = clean_price(row.get('cars prices'))
        horsepower = clean_horsepower(row.get('horsepower'))
        seats = clean_seats(row.get('seats'))
        engine_display_text = row.get('cc/battery capacity')
        engine_cc_num = get_engine_cc(engine_display_text)

        if price is None:
            print(f"Aviso: Pulando linha {index} por preço inválido: {row.get('cars prices')}")
            continue

        carro = Carro(
            make=row.get('company names'),
            model=row.get('cars names'),
            price=price,
            engine_cc=engine_cc_num, 
            engine_size_display=engine_display_text, 
            horsepower=horsepower,                     
            torque=row.get('torque'),                  
            fuel_type=row.get('fuel types'),
            seating_capacity=seats                     
        )
        cars_to_insert.append(carro)

    try:
        db.bulk_save_objects(cars_to_insert)
        db.commit()
        print(f"-> {len(cars_to_insert)} carros importados com sucesso para a tabela 'carros'.")
    except Exception as e:
        db.rollback()
        print(f"ERRO ao salvar no banco: {e}")

# --- Execução Principal ---
if __name__ == "__main__":
    db = SessionLocal()
    try:
        create_db_and_tables() 
        create_test_user(db)
        import_cars_data(db)
        print("\n=== Importação e Configuração do DB concluídas com SUCESSO! ===")
    except Exception as e:
        db.rollback()
        print(f"\nERRO FATAL DURANTE A CONFIGURAÇÃO DO DB: {e}")
    finally:
        db.close()