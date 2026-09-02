# Arquivo: frontend_app.py
# --- VERSÃO FINAL (Layout Correto + CSS Bonito) ---

import streamlit as st
import requests
import pandas as pd
import json
import jwt # pip install pyjwt
from typing import Optional
import re # Para extrair o número do motor

# --- Configurações ---
API_BASE_URL = "http://127.0.0.1:8000"

# --- 1. DICIONÁRIO DE TRADUÇÃO DE COMBUSTÍVEL ---
FUEL_TRANSLATION_MAP = {
    "Todos os Tipos": None, "Gasolina": "Petrol", "Híbrido Plug-in": "plug in hyrbrid",
    "Elétrico": "Electric", "Diesel": "Diesel", "Híbrido": "Hybrid",
    "Flex": "Flex", "GNV": "CNG" 
}
REVERSE_FUEL_MAP = {v: k for k, v in FUEL_TRANSLATION_MAP.items() if v is not None}
FUEL_OPTIONS_PT = list(FUEL_TRANSLATION_MAP.keys()) # Lista de chaves PT

st.set_page_config(layout="wide", page_title="Busca de Veículos")

# --- Funções de Estado e Autenticação ---

def get_session_state():
    """Inicializa ou retorna o estado da sessão."""
    if 'token' not in st.session_state: st.session_state.token = None
    if 'username' not in st.session_state: st.session_state.username = None
    if 'is_logged_in' not in st.session_state: st.session_state.is_logged_in = False
    if 'db_cars' not in st.session_state: st.session_state.db_cars = []
    
    keys_to_init = {
        'make_filter_value': '', 'model_filter_value': '',
        'fuel_filter_value': "Todos os Tipos", 
        'seats_filter_value': None, 'min_price_filter_value': None, 
        'max_price_filter_value': None, 'min_hp_filter_value': None, 
        'max_hp_filter_value': None,
        'min_engine_filter_value': None, 'max_engine_filter_value': None,
        'editing_car_id': None 
    }
    for key, default_value in keys_to_init.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def login(username, password):
    try:
        response = requests.post(f"{API_BASE_URL}/login", data={"username": username, "password": password})
        if response.status_code == 200:
            token_data = response.json()
            st.session_state.token = token_data['access_token']
            st.session_state.username = username
            st.session_state.is_logged_in = True
            # st.success("Login bem-sucedido!") # Removido
        else:
            st.error("Erro de login. Verifique nome de usuário e senha.")
            st.session_state.token = None; st.session_state.is_logged_in = False
    except requests.exceptions.ConnectionError:
        st.error("Erro: Não foi possível conectar à API.")

def logout():
    st.session_state.token = None; st.session_state.username = None
    st.session_state.is_logged_in = False; st.session_state.db_cars = []
    get_session_state(); st.info("Deslogado com sucesso."); st.rerun()

# --- Funções da API para Carros ---
# (As funções fetch_cars, add_new_car, delete_car, update_existing_car
#  continuam aqui, sem alterações)

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.token}", "accept": "application/json"}

def fetch_cars(
    make_filter: Optional[str] = None, model_filter: Optional[str] = None,
    fuel_filter: Optional[str] = None, seats_filter: Optional[int] = 0,
    min_price: Optional[float] = 0.0, max_price: Optional[float] = 0.0,
    min_hp: Optional[int] = 0, max_hp: Optional[int] = 0,
    min_engine: Optional[int] = 0, max_engine: Optional[int] = 0
):
    if not st.session_state.is_logged_in: return
    params = {}
    if make_filter: params['make'] = make_filter
    if model_filter: params['model'] = model_filter
    if fuel_filter: params['fuel_type'] = fuel_filter
    if seats_filter and seats_filter > 0: params['seating_capacity'] = seats_filter
    if min_price and min_price > 0: params['min_price'] = min_price
    if max_price and max_price > 0: params['max_price'] = max_price
    if min_hp and min_hp > 0: params['min_horsepower'] = min_hp
    if max_hp and max_hp > 0: params['max_horsepower'] = max_hp
    if min_engine and min_engine > 0: params['min_engine_size'] = min_engine
    if max_engine and max_engine > 0: params['max_engine_size'] = max_engine

    try:
        response = requests.get(f"{API_BASE_URL}/cars", headers=get_headers(), params=params)
        if response.status_code == 200:
            st.session_state.db_cars = response.json()
            if 'fetched_once' in st.session_state:
                 st.toast(f"Total de {len(st.session_state.db_cars)} carros encontrados.", icon='🚗')
        elif response.status_code == 401:
            st.error("Sessão expirada. Por favor, faça login novamente.")
            st.session_state.is_logged_in = False
        else:
            st.error(f"Erro ao buscar dados. Status: {response.status_code}. Mensagem: {response.text}")
            st.session_state.db_cars = []
    except requests.exceptions.ConnectionError:
        st.error("Erro de Conexão: O backend (uvicorn) parece estar offline.")
        st.session_state.db_cars = []

def add_new_car(car_data: dict):
    if not st.session_state.is_logged_in:
        st.error("Você precisa estar logado para adicionar um carro."); return False
    try:
        response = requests.post(f"{API_BASE_URL}/cars", headers=get_headers(), json=car_data)
        if response.status_code == 201:
            st.success(f"Carro '{car_data['model']}' adicionado com sucesso!")
            get_session_state(); fetch_cars(); return True
        else:
            st.error(f"Erro ao adicionar carro. Status: {response.status_code}. Mensagem: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        st.error("Erro de Conexão: O backend (uvicorn) parece estar offline."); return False

def delete_car(car_id: int):
    if not st.session_state.is_logged_in:
        st.error("Você precisa estar logado para apagar um carro."); return False
    try:
        response = requests.delete(f"{API_BASE_URL}/cars/{car_id}", headers=get_headers())
        if response.status_code == 204:
            st.success(f"Carro (ID: {car_id}) apagado com sucesso!")
            get_session_state(); fetch_cars(); st.rerun()
        else:
            st.error(f"Erro ao apagar carro. Status: {response.status_code}. Mensagem: {response.text}")
    except requests.exceptions.ConnectionError:
        st.error("Erro de Conexão: O backend (uvicorn) parece estar offline.")

def update_existing_car(car_id: int, car_data: dict):
    if not st.session_state.is_logged_in:
        st.error("Você precisa estar logado para editar um carro."); return False
    try:
        response = requests.put(f"{API_BASE_URL}/cars/{car_id}", headers=get_headers(), json=car_data)
        if response.status_code == 200:
            st.success(f"Carro '{car_data['model']}' (ID: {car_id}) atualizado com sucesso!")
            st.session_state.editing_car_id = None
            get_session_state(); fetch_cars(); st.rerun()
        else:
            st.error(f"Erro ao atualizar carro. Status: {response.status_code}. Mensagem: {response.text}")
    except requests.exceptions.ConnectionError:
        st.error("Erro de Conexão: O backend (uvicorn) parece estar offline.")


# --- Interface de Usuário (Layout Principal) ---

def sidebar_status():
    with st.sidebar:
        st.header("Gerenciador de Veículos 🚗")
        if st.session_state.is_logged_in:
            st.success(f"Logado como: {st.session_state.username}")
            if st.button("Logout", key="sidebar_logout", type="primary"): logout()

# --- PÁGINA DE LOGIN ATUALIZADA ---
def login_page():
    """Página de login com novo design"""
    
    # CSS para o novo design
    login_css = """
    <style>
        /* Esconde o cabeçalho e menu do Streamlit */
        header, [data-testid="stSidebar"] {
            display: none;
        }

        /* Fundo da página com gradiente */
        [data-testid="stAppViewContainer"] > .main {
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        }
        
        /* O "Cartão" de Login */
        /* Target o form DENTRO da coluna central */
        [data-testid="stHorizontalBlock"] [data-testid="stForm"] {
            background-color: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 2.5rem 3rem;
            border-radius: 15px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            max-width: 450px;
            margin: 0 auto; /* Centraliza o form dentro da coluna */
        }
        
        /* Título "Acesso ao Sistema" */
        /* Target o h1 DENTRO da coluna central */
        [data-testid="stHorizontalBlock"] h1 {
            text-align: center;
            color: white;
            padding-bottom: 0.5rem;
            font-weight: 600;
        }
        
        /* Oculta o "---" (st.markdown) */
        [data-testid="stHorizontalBlock"] [data-testid="stForm"] hr { display: none; }

        /* Rótulos (Login / Senha) */
        [data-testid="stHorizontalBlock"] [data-testid="stForm"] label { color: #e0e0e0; font-weight: 500; }

        /* Botão "ENTRAR" */
        [data-testid="stHorizontalBlock"] [data-testid="stForm"] .stButton button {
            width: 100%;
            background-image: linear-gradient(to right, #6a11cb 0%, #2575fc 100%);
            color: white; border: none; border-radius: 8px; padding: 10px 0;
            font-weight: 600; font-size: 1rem; margin-top: 1rem;
        }
        [data-testid="stHorizontalBlock"] [data-testid="stForm"] .stButton button:hover {
            background-image: linear-gradient(to right, #5e0fc2 0%, #1e66e3 100%);
            color: #ffffff;
        }

        /* Inputs de texto (Fundo claro, texto digitado escuro) */
        [data-testid="stHorizontalBlock"] [data-testid="stForm"] .stTextInput input, 
        [data-testid="stHorizontalBlock"] [data-testid="stForm"] .stTextInput input:focus {
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background-color: #FFFFFF;
            color: black; 
            -webkit-text-fill-color: black; 
        }
        
        /* Cor dos placeholders (agora cinza claro) */
        ::placeholder {
            color: rgba(0, 0, 0, 0.4) !important; 
            opacity: 1;
        }
    </style>
    """
    
    st.markdown(login_css, unsafe_allow_html=True)
    
    # --- LÓGICA DE LAYOUT (st.columns) ---
    st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True) 
    col1, col2, col3 = st.columns([1, 1.2, 1]) 

    with col2: # Todo o conteúdo de login vai na coluna central
        st.title("Acesso ao Sistema")
        st.markdown("---") # Este <hr> será escondido pelo CSS
        
        with st.form("login_form"):
            username = st.text_input("Login", placeholder="Digite seu login")
            password = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            submitted = st.form_submit_button("ENTRAR")
            
            if submitted:
                login(username, password) # Usa diretamente o que foi digitado
                if st.session_state.is_logged_in: 
                    st.session_state.editing_car_id = None
                    st.rerun()

# --- Página Principal da Aplicação ---
def main_app():
    
    # --- CSS ATUALIZADO PARA A PÁGINA PRINCIPAL ---
    main_app_css = """
    <style>
        /* Fundo da página */
        [data-testid="stAppViewContainer"] > .main {
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        }
        
        /* Cor do texto principal (Rótulos, Títulos, etc) */
        .stApp, h1, h2, h3, label, [data-testid="stMarkdown"] {
            color: white !important;
        }
        [data-testid="stMarkdown"] p {
             color: #e0e0e0 !important; /* Cor do texto de info/ações */
        }
        [data-testid="stInfo"] { /* Mensagem "Nenhum carro..." */
             color: #e0e0e0;
             background-color: rgba(90, 128, 255, 0.1);
             border: 1px solid rgba(90, 128, 255, 0.2);
        }

        /* --- CORREÇÃO DO TEXTO DA SIDEBAR --- */
        /* Deixa o fundo da sidebar como está (padrão branco/claro) */
        
        /* Força o texto do header (h2) a ser PRETO */
        [data-testid="stSidebar"] h2 {
            color: black !important;
        }
        /* Força o texto dentro do "st.success" a ser PRETO */
        [data-testid="stSidebar"] [data-testid="stSuccess"] p { 
            color: black !important; 
        }
        /* --------------------------- */

        /* Estilo dos Expanders (Filtros, Adicionar, Editar) */
        [data-testid="stExpander"] {
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.37);
        }
        [data-testid="stExpander"] summary { /* O título do expander */
            color: #e0e0e0;
            font-size: 1.1rem;
            font-weight: 500;
        }
        [data-testid="stExpander"] summary:hover { color: white; }
        
        
        /* Inputs e Botões (Fundo claro, texto digitado escuro) */
        .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {
            background-color: #FFFFFF; /* Fundo branco */
            border: 1px solid rgba(0, 0, 0, 0.2); /* Borda escura */
            color: black; /* Texto sendo digitado */
            -webkit-text-fill-color: black;
            border-radius: 8px;
        }
        /* Cor do texto do placeholder (agora escuro) */
        ::placeholder {
            color: rgba(0, 0, 0, 0.4) !important;
        }
        .stSelectbox [data-baseweb="select"] > div {
             color: black; /* Texto do selectbox selecionado */
        }
        
        /* Botões */
        .stButton button {
            border: none;
            border-radius: 8px;
            padding: 10px 15px;
            font-weight: 600;
        }
        
        /* Botões Primários (VERMELHO) */
        .stButton button[kind="primary"] {
            background-image: linear-gradient(to right, #D32F2F 0%, #FF5252 100%) !important;
            color: white !important;
        }
        .stButton button[kind="primary"]:hover {
             background-image: linear-gradient(to right, #C62828 0%, #FF1744 100%) !important;
             color: white !important;
        }
        
        /* Botões Secundários (Cinza/Transparente) */
        .stButton button[kind="secondary"] {
             background: rgba(255, 255, 255, 0.1);
             border: 1px solid rgba(255, 255, 255, 0.2);
             color: white;
        }
        .stButton button[kind="secondary"]:hover {
             background: rgba(255, 255, 255, 0.2);
             color: white;
        }

        /* --- Tabela de Dados (Mantido o estilo escuro) --- */
        [data-testid="stDataFrame"] { background-color: transparent; }
        [data-testid="stDataFrame"] .col-header { /* Cabeçalho */
             background-color: rgba(255, 255, 255, 0.1);
             color: white; font-weight: 600;
        }
        [data-testid="stDataFrame"] .data-row { /* Células */
             color: #e0e0e0;
        }
        [data-testid="stDataFrame"] .data-row:hover {
             background-color: rgba(255, 255, 255, 0.1);
             color: white;
        }
        [data-testid="stDataFrame"] .data-row, 
        [data-testid="stDataFrame"] .col-header,
        [data-testid="stDataFrame"] .blank-overlay {
            border-bottom-color: rgba(255, 255, 255, 0.2);
            border-right-color: rgba(255, 255, 255, 0.2);
        }
        [data-testid="stDataFrame"] .data-row.row-selected {
             background-color: rgba(90, 128, 255, 0.3) !important;
             color: white;
        }
    </style>
    """
    st.markdown(main_app_css, unsafe_allow_html=True)
    
    st.title("Busca de Veículos 🔍"); st.markdown("---")

    # --- ÁREA DE FILTROS (AGORA DENTRO DE UM EXPANDER) ---
    with st.expander("Filtros de Busca", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            make_filter = st.text_input("Buscar por Marca", key="make_filter_value", placeholder="Ex: Honda, Tesla...")
        with col2:
            model_filter = st.text_input("Buscar por Modelo", key="model_filter_value", placeholder="Ex: Civic, Model 3...")

        col3, col4 = st.columns(2)
        with col3:
            min_price_filter = st.number_input("Preço Mínimo (R$)", min_value=0.0, format="%.2f", key='min_price_filter_value', placeholder="R$ 0,00")
        with col4:
            max_price_filter = st.number_input("Preço Máximo (R$)", min_value=0.0, format="%.2f", key='max_price_filter_value', placeholder="R$ 0,00")
        
        col5, col6 = st.columns(2)
        with col5:
            min_hp_filter = st.number_input("Potência Mínima (CV)", min_value=0, step=10, key='min_hp_filter_value', placeholder="CV 0")
        with col6:
            max_hp_filter = st.number_input("Potência Máxima (CV)", min_value=0, step=10, key='max_hp_filter_value', placeholder="CV 0")

        col7, col8 = st.columns(2)
        with col7:
            min_engine_filter = st.number_input("Motor Mínimo (cc)", min_value=0, step=100, key='min_engine_filter_value', placeholder="Ex: 2000")
        with col8:
            max_engine_filter = st.number_input("Motor Máximo (cc)", min_value=0, step=100, key='max_engine_filter_value', placeholder="Ex: 5000")

        col9, col10, col11 = st.columns(3)
        with col9:
            fuel_filter_display = st.selectbox("Tipo de Combustível", options=FUEL_OPTIONS_PT, key="fuel_filter_value")
        with col10:
            seats_filter = st.number_input("Nº de Assentos (Exato)", min_value=0, step=1, help="Deixe 0 para não filtrar", key='seats_filter_value', placeholder="0")
        with col11:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Buscar Carros", key="fetch_button", type="primary"):
                fuel_filter_to_send = FUEL_TRANSLATION_MAP[st.session_state.fuel_filter_value]
                fetch_cars(
                    make_filter=st.session_state.make_filter_value, 
                    model_filter=st.session_state.model_filter_value,
                    fuel_filter=fuel_filter_to_send, 
                    seats_filter=st.session_state.seats_filter_value,
                    min_price=st.session_state.min_price_filter_value, 
                    max_price=st.session_state.max_price_filter_value,
                    min_hp=st.session_state.min_hp_filter_value, 
                    max_hp=st.session_state.max_hp_filter_value,
                    min_engine=st.session_state.min_engine_filter_value,
                    max_engine=st.session_state.max_engine_filter_value
                )

    # --- SEÇÃO ADICIONAR CARRO ---
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True) # Espaçamento
    with st.expander("➕ Adicionar Novo Carro ao Inventário"):
        with st.form("add_car_form", clear_on_submit=True):
            st.subheader("Preencha os dados do novo veículo")
            c1, c2, c3 = st.columns(3)
            with c1:
                new_make = st.text_input("Marca", placeholder="Ex: FERRARI")
                new_model = st.text_input("Modelo", placeholder="Ex: SF90 STRADALE")
                new_price = st.number_input("Preço (R$)", min_value=0.0, format="%.2f", value=None, placeholder="R$ 0,00")
            with c2:
                new_engine_display = st.text_input("Motor (Texto Display)", placeholder="Ex: 3990 cc ou 95 kWh")
                new_hp = st.number_input("Potência (CV)", min_value=0, step=1, help="Ex: 963", value=None, placeholder="Ex: 963")
                new_torque = st.text_input("Torque (Nm)", placeholder="Ex: 800 Nm")
            with c3:
                new_fuel_display = st.selectbox("Tipo de Combustível", options=FUEL_OPTIONS_PT, key="add_fuel_type")
                new_seats = st.number_input("Nº de Assentos", min_value=1, step=1, format="%d", help="Ex: 2", value=None, placeholder="Ex: 2")
            
            submitted = st.form_submit_button("Salvar Carro", type="primary")

            if submitted:
                if not new_make or not new_model or not new_price or new_price == 0:
                    st.warning("Por favor, preencha pelo menos Marca, Modelo e Preço.")
                else:
                    new_engine_cc_num = None
                    if new_engine_display:
                        match = re.search(r'([\d\.]+)', new_engine_display)
                        if match:
                            try: new_engine_cc_num = int(float(match.group(1)))
                            except ValueError: pass 
                    
                    fuel_to_add = FUEL_TRANSLATION_MAP[new_fuel_display]
                    car_data = {
                        "make": new_make, "model": new_model, "price": new_price,
                        "engine_cc": new_engine_cc_num, 
                        "engine_size_display": new_engine_display, 
                        "horsepower": new_hp, "torque": new_torque if new_torque else None,
                        "fuel_type": fuel_to_add, "seating_capacity": new_seats
                    }
                    add_new_car(car_data)
    
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True) # Espaçamento
    
    if st.session_state.is_logged_in and not st.session_state.db_cars and 'fetched_once' not in st.session_state:
        fetch_cars()
        st.session_state.fetched_once = True 

    # --- ÁREA DE EXIBIÇÃO DE RESULTADOS ---
    st.subheader(f"Resultados Encontrados ({len(st.session_state.db_cars)} Carros)")
    
    if st.session_state.db_cars:
        df = pd.DataFrame(st.session_state.db_cars)
        
        if 'fuel_type' in df.columns:
            df['fuel_type'] = df['fuel_type'].map(REVERSE_FUEL_MAP).fillna(df['fuel_type'])
        
        df_display = df.rename(columns={
            'make': 'Marca', 'model': 'Modelo', 'price': 'Preço (R$)',
            'engine_size_display': 'Motor (cc)', 'horsepower': 'Potência (CV)',
            'torque': 'Torque (Nm)', 'fuel_type': 'Combustível',
            'seating_capacity': 'Nº de Assentos', 'id': 'ID'
        })
        
        cols_order_raw = ['ID', 'Marca', 'Modelo', 'Preço (R$)', 
                          'Potência (CV)', 'Motor (cc)', 'Combustível', 'Nº de Assentos', 'Torque (Nm)']
        cols_order = [col for col in cols_order_raw if col in df_display.columns]
        df_display = df_display[cols_order]
        
        if 'Preço (R$)' in df_display.columns:
            df_display['Preço (R$)'] = pd.to_numeric(df_display['Preço (R$)'], errors='coerce').fillna(0.0)
            df_display['Preço (R$)'] = df_display['Preço (R$)'].apply(lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        data_editor = st.dataframe(
            df_display, 
            use_container_width=True, 
            hide_index=True,
            on_select="rerun", 
            selection_mode="single-row"
        )
        
        # --- AÇÕES (EDITAR E APAGAR) ---
        if data_editor.selection.rows:
            st.markdown("---")
            selected_row_index = data_editor.selection.rows[0]
            selected_car = st.session_state.db_cars[selected_row_index]
            selected_car_id = selected_car['id']
            selected_car_model = selected_car['model']
            
            st.subheader(f"Ações para: {selected_car_model} (ID: {selected_car_id})")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                # Botão Editar (agora é 'secondary' para ser cinza)
                if st.button(f"✏️ Editar {selected_car_model}", type="secondary"):
                    st.session_state.editing_car_id = selected_car_id
                    st.rerun() 

            with col2:
                # Botão Apagar (é 'primary' para ser vermelho)
                if st.button(f"🗑️ Apagar {selected_car_model}", type="primary"):
                    st.session_state.editing_car_id = None
                    delete_car(selected_car_id)

        # --- FORMULÁRIO DE EDIÇÃO (USA EXPANDER) ---
        if st.session_state.editing_car_id:
            car = next((c for c in st.session_state.db_cars if c['id'] == st.session_state.editing_car_id), None)
            
            if car:
                with st.expander("✏️ Editando Carro...", expanded=True):
                    fuel_pt = REVERSE_FUEL_MAP.get(car['fuel_type'], "Todos os Tipos")
                    fuel_index = FUEL_OPTIONS_PT.index(fuel_pt) if fuel_pt in FUEL_OPTIONS_PT else 0

                    with st.form("edit_car_form"):
                        st.subheader(f"Alterando dados de: {car['make']} {car['model']}")
                        
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            edit_make = st.text_input("Marca", value=car['make'])
                            edit_model = st.text_input("Modelo", value=car['model'])
                            edit_price = st.number_input("Preço (R$)", min_value=0.0, format="%.2f", value=car['price'])
                        with c2:
                            edit_engine_display = st.text_input("Motor (Texto Display)", value=car.get('engine_size_display'))
                            edit_hp = st.number_input("Potência (CV)", min_value=0, step=1, help="Ex: 963", value=car.get('horsepower'))
                        with c3:
                            edit_torque = st.text_input("Torque (Nm)", value=car.get('torque'))
                            edit_fuel_display = st.selectbox("Tipo de Combustível", options=FUEL_OPTIONS_PT, index=fuel_index)
                            edit_seats = st.number_input("Nº de Assentos", min_value=1, step=1, format="%d", help="Ex: 2", value=car.get('seating_capacity'))
                        
                        col_submit, col_cancel = st.columns(2)
                        with col_submit:
                            # Botão Salvar (é 'primary' para ser vermelho)
                            if st.form_submit_button("Salvar Alterações", type="primary"):
                                edit_engine_cc_num = None
                                if edit_engine_display:
                                    match = re.search(r'([\d\.]+)', edit_engine_display)
                                    if match:
                                        try: edit_engine_cc_num = int(float(match.group(1)))
                                        except ValueError: pass 
                                
                                fuel_to_send = FUEL_TRANSLATION_MAP[edit_fuel_display]
                                car_data = {
                                    "make": edit_make, "model": edit_model, "price": edit_price,
                                    "engine_cc": edit_engine_cc_num, 
                                    "engine_size_display": edit_engine_display,
                                    "horsepower": edit_hp, "torque": edit_torque,
                                    "fuel_type": fuel_to_send, "seating_capacity": edit_seats
                                }
                                update_existing_car(car['id'], car_data)
                        
                        with col_cancel:
                            # Botão Cancelar (agora 'primary' para ser vermelho)
                            if st.form_submit_button("Cancelar Edição", type="primary"):
                                st.session_state.editing_car_id = None
                                st.rerun()

    else:
        st.info("Nenhum carro encontrado. Tente buscar novamente com outros filtros ou clique em 'Buscar Carros' sem filtros para carregar o inventário completo.")

# --- Execução Principal ATUALIZADA ---
if __name__ == "__main__":
    get_session_state()
    
    if st.session_state.is_logged_in:
        sidebar_status() # Só mostra a sidebar se estiver logado
        main_app()
    else:
        login_page() # Mostra a nova página de login