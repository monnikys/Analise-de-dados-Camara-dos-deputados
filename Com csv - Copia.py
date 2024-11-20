import requests
import pandas as pd
import matplotlib.pyplot as plt
import psycopg2
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

def web_scraping_deputados():
    """
    Realiza o web scraping dos dados dos deputados a partir da API da Câmara dos Deputados.

    Returns:
        DataFrame: Um DataFrame contendo os dados dos deputados, ou None se ocorrer um erro.
    """
    try:
        url = "https://dadosabertos.camara.leg.br/api/v2/deputados"
        response = requests.get(url)

        if response.status_code == 200:
            deputados_data = response.json()
            deputados = deputados_data['dados']
            df_deputados = pd.DataFrame(deputados)
            return df_deputados
        else:
            print(f"Erro ao acessar a API: {response.status_code}")
            return None
    except Exception as e:
        print(f"Ocorreu um erro durante o scraping: {e}")
        return None

def salvar_banco_de_dados(df, tabela):
    """
    Salva os dados de um DataFrame em uma tabela específica do banco de dados PostgreSQL.
    Args:
        df (DataFrame): Os dados a serem salvos.
        tabela (str): O nome da tabela onde os dados serão salvos.
    """
    engine = create_engine('postgresql+psycopg2://postgres:1234@localhost:5432/db_camara')

    # Salvar o DataFrame na tabela 'deputados'
    df.to_sql(tabela, engine, if_exists='append', index=False)
    print(f"Dados salvos no banco de dados 'db_camara' na tabela '{tabela}'.")

def visualizar_dados(df):
    """ Visualiza os dados dos deputados em um gráfico de barras.
    Args: df (DataFrame): DataFrame contendo os dados dos deputados. """

    # Número de deputados por partido
    partidos = df['siglaPartido'].value_counts()
    
    # Gráfico de barras
    partidos.plot(kind='bar')
    plt.title('Número de Deputados por Partido')
    plt.xlabel('Partido')
    plt.ylabel('Número de Deputados')
    plt.xticks(rotation=100)  # Rotaciona o eixo x
    plt.tight_layout()  # Ajusta o layout para que não haja sobreposição
    plt.show()

def visualizar_dados_banco():
    """ Visualiza as primeiras linhas dos dados dos deputados armazenados no banco de dados PostgreSQL. """
    # Conecta ao PostgreSQL
    engine = create_engine('postgresql+psycopg2://postgres:1234@localhost:5432/db_camara')
    
    # Exibe as primeiras linhas
    df = pd.read_sql('SELECT * FROM deputados', con=engine)
    print(df.head()) 

def criar_tabela_deputados():
    """
    Cria a tabela 'deputados' no banco de dados PostgreSQL se ela não existir.
    """
    conn = psycopg2.connect(
        dbname='db_camara',
        user='postgres',
        password='1234',
        host='localhost',
        port='5432'
    )
    cursor = conn.cursor()

    # Criar tabela de deputados se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deputados (
            id SERIAL PRIMARY KEY,
            uri VARCHAR(255),
            nome VARCHAR(255) NOT NULL,
            "siglaPartido" VARCHAR(50) NOT NULL,
            "uriPartido" VARCHAR(255),
            "siglaUf" VARCHAR(2) NOT NULL,
            "idLegislatura" INTEGER,
            "urlFoto" TEXT,
            "email" VARCHAR(255),
            "gabinete" VARCHAR(100)
        )
    ''')

    conn.commit()
    cursor.close()
    conn.close()

criar_tabela_deputados()


def criar_tabela_despesas():
    """
    Cria a tabela 'despesas' no banco de dados PostgreSQL se ela não existir.
    """
    conn = psycopg2.connect(
        dbname='db_camara',
        user='postgres',
        password='1234',
        host='localhost',
        port='5432'
    )
    cursor = conn.cursor()
    
    # Criar tabela de despesas se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS despesas (
            id SERIAL PRIMARY KEY,
            "txNomeParlamentar" VARCHAR(255),
            "cpf" VARCHAR(20),
            "ideCadastro" INTEGER,
            "nuCarteiraParlamentar" VARCHAR(30),
            "nuLegislatura" INTEGER,
            "sgUF" VARCHAR(5),
            "sgPartido" VARCHAR(20),
            "codLegislatura" INTEGER,
            "numSubCota" INTEGER,
            "txtDescricao" TEXT,
            "numEspecificacaoSubCota" INTEGER,
            "txtDescricaoEspecificacao" TEXT,
            "txtFornecedor" TEXT,
            "txtCNPJCPF" VARCHAR(30),
            "txtNumero" VARCHAR(255),
            "indTipoDocumento" VARCHAR(5),
            "datEmissao" DATE,  -- esta é a coluna correta
            "vlrDocumento" NUMERIC,
            "vlrGlosa" NUMERIC,
            "vlrLiquido" NUMERIC,
            "numMes" INTEGER,
            "numAno" INTEGER,
            "numParcela" INTEGER,
            "txtPassageiro" TEXT,
            "txtTrecho" TEXT,
            "numLote" INTEGER,
            "numRessarcimento" INTEGER,
            "datPagamentoRestituicao" DATE,
            "vlrRestituicao" NUMERIC,
            "nuDeputadoId" INTEGER,
            "ideDocumento" VARCHAR(255),
            "urlDocumento" TEXT,
            deputado_id INTEGER,
            CONSTRAINT fk_deputado
                FOREIGN KEY(deputado_id) 
                REFERENCES deputados(id)
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()

criar_tabela_despesas()

def carregar_despesas_de_csv(caminho_csv):
    """
    Carrega os dados de despesas a partir de um arquivo CSV.
    Args:
        caminho_csv (str): O caminho do arquivo CSV.
    Returns:
        DataFrame: Um DataFrame contendo os dados das despesas, ou None se ocorrer um erro.
    """
    try:
        # Especifica o delimitador correto e trata as aspas
        df = pd.read_csv(caminho_csv, sep=';', quotechar='"')
        return df
    except Exception as e:
        print(f"Ocorreu um erro ao carregar o CSV: {e}")
        return None

def visualizar_despesas_banco():
    """ Visualiza os dados de despesas de 2022 armazenados no banco de dados PostgreSQL. """
    conn = psycopg2.connect(
        dbname='db_camara',
        user='postgres',
        password='1234',
        host='localhost',
        port='5432'
    )
    cursor = conn.cursor()

    # Alterar a consulta para usar o nome correto da coluna
    cursor.execute('SELECT * FROM despesas WHERE EXTRACT(YEAR FROM "datEmissao") = 2022')
    resultados = cursor.fetchall()
    
    # Aqui você pode manipular os resultados conforme necessário
    for linha in resultados:
        print(linha)

    cursor.close()
    conn.close()

visualizar_despesas_banco()

def preparar_dados(df):
    """
    Prepara os dados para o treinamento dos modelos.
    
    Args:
        df (DataFrame): DataFrame com os dados de despesas.
    
    Returns:
        X (DataFrame): Variáveis independentes.
        y (Series): Variável dependente (gastos altos).
    """
    df['gasto_alto'] = df['vlrLiquido'].apply(lambda x: 1 if x > 10000 else 0)  # Define o limite de gasto alto
    X = df[['numMes', 'numAno', 'numSubCota', 'vlrDocumento', 'numParcela']]  # Selecione as variáveis relevantes
    y = df['gasto_alto']
    return X, y

def treinar_modelos(X, y):
    """
    Treina modelos de Regressão Logística e Random Forest.
    
    Args:
        X (DataFrame): Variáveis independentes.
        y (Series): Variável dependente.
    
    Returns:
        None
    """
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import classification_report, confusion_matrix

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    modelo_logistico = LogisticRegression(max_iter=1000)
    modelo_logistico.fit(X_train, y_train)

    modelo_rf = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo_rf.fit(X_train, y_train)

    pred_logistico = modelo_logistico.predict(X_test)
    pred_rf = modelo_rf.predict(X_test)

    print("Relatório de Classificação - Regressão Logística:")
    print(classification_report(y_test, pred_logistico))
    print("Matriz de Confusão - Regressão Logística:")
    print(confusion_matrix(y_test, pred_logistico))

    print("Relatório de Classificação - Random Forest:")
    print(classification_report(y_test, pred_rf))
    print("Matriz de Confusão - Random Forest:")
    print(confusion_matrix(y_test, pred_rf))

if __name__ == "__main__":
    criar_tabela_deputados()
    criar_tabela_despesas()
    
    df_deputados = web_scraping_deputados()
    
    if df_deputados is not None:
        salvar_banco_de_dados(df_deputados, 'deputados')
        visualizar_dados_banco()  # Verifica os dados dos deputados salvos no banco
        visualizar_dados(df_deputados)  # Visualiza os dados dos deputados da API

# Carregar as despesas do arquivo CSV
caminho_csv = r'C:\Users\monni\Desktop\AA\Ano-2022 4.csv'  
df_despesas = carregar_despesas_de_csv(caminho_csv)

if df_despesas is not None:
    print(df_despesas.head())  # Visualiza as primeiras linhas
    salvar_banco_de_dados(df_despesas, 'despesas')
    visualizar_despesas_banco()
    
    X, y = preparar_dados(df_despesas)  # Prepara os dados para análise
    treinar_modelos(X, y)  # Treina os modelos de machine learning
