# Gerenciador de Veículos — APS UNIP

Projeto desenvolvido como **Atividade Prática Supervisionada (APS)** da **Universidade Paulista — UNIP**, no **8º semestre de Ciência da Computação**, durante o **segundo semestre de 2025 (2025.2)**, último semestre da faculdade.

O trabalho aplica conceitos de desenvolvimento de sistemas distribuídos por meio de uma API em Python com autenticação JWT, persistência em SQLite e uma interface web para consultar e gerenciar veículos a partir de dados do Kaggle.

## Contexto acadêmico

- **Instituição:** Universidade Paulista — UNIP.
- **Curso:** Ciência da Computação.
- **Semestre:** 8º semestre, último semestre do curso.
- **Período de desenvolvimento:** segundo semestre de 2025.
- **Tema do enunciado:** API segura e dados do Kaggle.
- **Enunciado original:** [PDF da APS — 2025.2](docs/enunciado-aps-unip-2025-2.pdf).
- **Apresentação indicada na documentação do grupo:** [vídeo no YouTube](https://www.youtube.com/watch?v=i-Hl-VM9_1k).

Este repositório registra o trabalho acadêmico original. Os arquivos Python e o CSV foram preservados sem alterações nesta publicação. O README, a lista de dependências e os arquivos de organização foram acrescentados para facilitar a consulta e a reprodução local. A publicação no GitHub é posterior ao desenvolvimento em 2025.

## Integrantes

- André Leonardo Marinzeck de Oliveira
- Arthur Martin Castilho
- Bruno Mendonça Sigismundo
- Lucas Rios de Souza Jordão
- Marcio Gabriel Maio

## Funcionalidades presentes no código

- Login com autenticação JWT e tokens com tempo de expiração.
- Consulta de veículos por marca, modelo, combustível e número de assentos.
- Filtros por faixa de preço, potência e cilindrada.
- Cadastro, edição e exclusão de veículos.
- Visualização dos resultados em tabela e seleção de um veículo para edição ou exclusão.
- Encerramento da sessão pela interface.
- Importação e tratamento dos dados do arquivo CSV.
- Documentação interativa da API disponibilizada pelo FastAPI.

O enunciado registra o que foi solicitado pela disciplina; não é uma declaração de que todos os itens foram implementados. A versão original utiliza GET, POST, PUT e DELETE; não possui rota PATCH nem paginação na API.

## Tecnologias

Python 3.11, FastAPI, Uvicorn, Streamlit, SQLAlchemy, SQLite, Pandas, Pydantic, PyJWT, Passlib/bcrypt e Requests.

## Como executar localmente

As instruções abaixo usam o terminal do VS Code no Windows e devem ser executadas na pasta deste repositório. As versões das dependências diretas foram registradas a partir do ambiente virtual encontrado com o projeto; não representam uma atualização das bibliotecas nem um arquivo de lock completo.

### 1. Preparar uma cópia para demonstração

```powershell
git clone https://github.com/LucasRios1606/Gerenciador-Veiculos-APS-UNIP.git
cd Gerenciador-Veiculos-APS-UNIP
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Os comandos usam diretamente o Python do ambiente virtual; não é necessário mudar a política de execução do PowerShell para ativá-lo.

### 2. Importar os veículos

**Atenção: `import_data.py` apaga e recria as tabelas de `cars_inventory.db`, incluindo veículos e usuários. Execute esta etapa somente em uma cópia nova para demonstração, sem dados que precisem ser preservados. Reexecutar o importador perde as alterações feitas no banco.**

O arquivo `Cars Datasets 2025.csv` deve permanecer na raiz, com esse nome.

```powershell
.\.venv\Scripts\python.exe import_data.py
```

### 3. Iniciar a API

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

A documentação interativa fica em [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### 4. Iniciar a interface

Em um segundo terminal, na mesma pasta:

```powershell
.\.venv\Scripts\python.exe -m streamlit run frontend_app.py --server.address 127.0.0.1 --server.port 8501
```

Acesse [http://127.0.0.1:8501](http://127.0.0.1:8501). A interface original utiliza a API em `127.0.0.1:8000`; mantenha os dois terminais abertos. Para encerrar, use `Ctrl+C` em cada um.

### Acesso de demonstração

O importador original cria a conta de teste `@administrador`, com senha `Adm@2025`. A inicialização da API também cria a conta `teste`, com senha `sua_senha_aqui`, quando ela ainda não existe.

Esses valores fazem parte do código acadêmico original. Não são credenciais para um serviço público e não devem ser usados em contas reais.

## Cuidados e limitações da versão original

- **Uso acadêmico e local:** existem credenciais de teste e uma chave JWT de exemplo fixas no código. Não exponha esta versão à internet nem a utilize com dados reais ou em produção.
- O banco de dados local, seus usuários e hashes de senhas não foram incluídos no repositório. O banco de demonstração é criado pelos comandos acima.
- O ambiente virtual, os caches e arquivos privados de configuração também foram excluídos da publicação.
- O dataset informa preços em dólares americanos. A interface original usa o rótulo `R$`, mas o importador não faz conversão de moeda; os valores não devem ser interpretados como preços em reais.
- Os arquivos Python passaram por verificação de sintaxe para a publicação. Isso não substitui testes funcionais de todas as telas e rotas.

## Dados e materiais de terceiros

O arquivo `Cars Datasets 2025.csv` foi mantido conforme a cópia utilizada no projeto. Sua fonte é [Cars Datasets (2025), de Abdul Malik, no Kaggle](https://www.kaggle.com/datasets/abdulmalik1518/cars-datasets-2025). A página informa licença Apache 2.0 e contém uma observação sobre uso educacional e de pesquisa. Consulte [os créditos e avisos dos materiais](docs/materiais-de-terceiros.md) antes de reutilizá-los.

O PDF do enunciado é material acadêmico da UNIP, incluído para contextualizar a atividade. O relatório do grupo com RAs e assinaturas não faz parte desta publicação. Não foi atribuída uma nova licença ao código do grupo nem ao material da universidade.
