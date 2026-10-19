import pandas as pd
import requests
import streamlit as st
from unidecode import unidecode
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"

# Colunas de interesse nos dados
fields = [
    "NU_NOTIFIC",
    "NU_ANO",
    "DT_NASC", 
    "CS_SEXO", 
    "CS_ESCOL_N",
    "NM_BAIRRO",
    "HOSPITALIZ",
    "EVOLUCAO",
    "CLASSI_FIN"
]

fields_2020_menos = [
    "nu_notificacao",
    "notificacao_ano",
    "dt_nascimento", 
    "tp_sexo", 
    "tp_escolaridade",
    "no_bairro_residencia",
    "st_ocorreu_hospitalizacao",
    "tp_evolucao_caso",
    "tp_classificacao_final"
]

def carregar_dados_api(colunas, colunas_2020_menos):    
    
    # Coletando os metadados dos recursos para definir as IDs dos datasets a importar
    metadados_chikg = requests.get("https://dados.recife.pe.gov.br/api/action/package_show?id=casos-de-dengue-zika-e-chikungunya")
    dict_response = metadados_chikg.json()
    results = dict_response['result']
    resources = results['resources']        
    
    ids_importar = [id['id'] for id in resources if "casos" in id['name'].lower() and "chikungunya" in id['name'].lower() and id['format'].lower().strip() == "csv"] # IDs para consultar (estão disponíveis dados de 2015 e 2025)
    nomes_importar = [name['name'] for name in resources if "casos" in name['name'].lower() and "chikungunya" in name['name'].lower()]
    nomes_2020_menos = [str(ano) for ano in range(2015, 2021)]             # primeiro ano da série histórica é 2015, até 2020 a nomenclatura das colunas foi diferente    
    
    dados_paginacao = []
    max_entradas_contrato = 500                                           # número máximo de registros enviados pelo site a cada request (testado)
        
    for id, nome in zip(ids_importar, nomes_importar):                     # iterar sobre as IDs dos dados + os nomes que descrevem o recurso  
        print(id, " - ", nome)
        url = "https://dados.recife.pe.gov.br/api/action/datastore_search"               
        
        for ano in nomes_2020_menos:                                       # controla a atribuição do nome das colunas (2020- apresenta outra nomenclatura)
            if ano in nome:                                
                colunas_params = colunas_2020_menos
                substituir_colunas = True                
                break             
            else:                
                colunas_params = colunas
                substituir_colunas = False
                
        num_dados_recebidos = max_entradas_contrato
        offset = 0
        total_recebidos = 0 
        while num_dados_recebidos >= max_entradas_contrato:
            params = {
                "resource_id": id,                
                "fields": colunas_params,
                "limit": max_entradas_contrato, # 500 entradas
                "offset": offset
            }        
            
            resposta = requests.get(url, params=params, timeout=30)
            resposta.raise_for_status()
            
            if substituir_colunas:                                               # Substituindo o nome das colunas para os dados 2020- e constrói o dicionario a partir do retorno do requests
                resposta_texto = resposta.text                
                for cols_2020_menos, cols in zip(colunas_2020_menos, colunas):                                
                    resposta_texto = resposta_texto.replace(cols_2020_menos, cols)                                                                        
                dados = json.loads(resposta_texto)                    
            else:        
                dados = resposta.json()                        
            
            registros = dados['result']["records"]                               # lista de dicionarios
            num_dados_recebidos = len(registros)
            total_recebidos += num_dados_recebidos                                            
            
            if offset == 0:
                print("Total disponível:", dados['result']["total"])            
            print("Registros recebidos:", num_dados_recebidos, "Total recebidos:", total_recebidos)  
            # print(f"Os dados estão em 'dados['result']['records']")            
            dados_paginacao += registros
            offset += max_entradas_contrato
        
        num_dados_recebidos = max_entradas_contrato
    
    # Construção do DataFrame
    df = pd.DataFrame(dados_paginacao)
    
    # Armazenando em texto             
    df.to_json(PROCESSED / "data_series.json")   
    print("Gravando registrons em json")         
    return df

@st.cache_data(ttl=3600)
def carregar_dados_fonte(arquivo_csv=None, json=True):         # fonte será json gravado ou arquivo fornecido pelo usuário
    
    ''' Precisa retornar só o DataFrame dos Dados'''
    nomes_2020_menos = [str(ano) for ano in range(2015, 2021)]
    if json:
        dados = pd.read_json(r"data\processed\data_series.json")  
    else:        
        dados = pd.read_csv(arquivo_csv, sep=";")
        for ano in nomes_2020_menos:
            if ano in arquivo_csv:                             # se o arquivo for de ano <= 2020, seleciona as colunas correspondentes e sai da função
                dados = dados.loc[:, fields_2020_menos]
                return dados
        dados = dados.loc[:, fields]
    return dados

@st.cache_data(ttl=3600)
def primeira_agregacao(df_api): # fonte será 'API' ou 'cache', se der erro na API, a função deve buscar no cache 
    
    '''
    Retorna um DataFrame - df_agregado - com as colunas:
    NM_BAIRRO - TOTAL_CASOS - TOTAL_HOSPITALIZACOES - TOTAL_OBITOS
    
    e um DataFrame - df_hospitalizacoes - filtrando apenas os casos em que ocorreu hospitalização
    '''
    # RETIRAR CASOS NOTIFICADOS, MAS DESCARTADOS NA CLASSIFICAÇÃO FINAL        
    df_casos_confirmados = df_api[df_api['CLASSI_FIN'] != 5]
    
    # CONSIDERAR CASOS COM OCORRÊNCIA DE HOSPITALIZAÇÂO - AQUI TEMOS OS CASOS NÃO DESCARTADOS EM QUE HOUVE HOSPITALIZAÇÃO    
    df_hospitalizacoes = df_casos_confirmados[df_casos_confirmados['HOSPITALIZ'] == 2].reset_index(drop=True)   

    # ----------------------------------------------------------------------
    # OPERAÇÃO DIRETA PARA CONTAGEM DOS CASOS POR BAIRRO
    # ----------------------------------------------------------------------    
    df_bairros = df_casos_confirmados['NM_BAIRRO'].value_counts().reset_index()
    df_bairros.columns = ['NM_BAIRRO', 'CONTAGEM']

    # PROCESSAMENTO AGREGADO   
    df_agregado = (
        df_casos_confirmados.groupby('NM_BAIRRO')
        .agg(
            TOTAL_CASOS=('NM_BAIRRO', 'size'),
            TOTAL_HOSPITALIZACOES=('HOSPITALIZ', lambda x: (x == 2).sum()),
            TOTAL_OBITOS=('EVOLUCAO', lambda x: (x == 2).sum()) # Óbito pelo agravo
        )
        .reset_index()
    )  

    return df_agregado, df_hospitalizacoes

def criar_analise(dataframe_casos, dataframe_populacao):
    
    dataframe_casos['BAIRRO_MERGE'] = dataframe_casos['NM_BAIRRO'].str.upper().apply(unidecode)
    dataframe_populacao['BAIRRO_MERGE'] = dataframe_populacao['NM_BAIRRO'].str.upper().apply(unidecode)
    df_completo = dataframe_casos.merge(
        dataframe_populacao[['BAIRRO_MERGE', 'POPULACAO']],
        on="BAIRRO_MERGE",
        how="left"
        )   
    
    # Cálculo da indicência por 100k habitantes
    df_completo["INCIDENCIA_100K"] = (
        df_completo["TOTAL_CASOS"] / df_completo["POPULACAO"]) * 100_000   
    
    # Cálculo do percentual de internações por casos
    df_completo['PERC_CASOS_HOSP'] = ((df_completo['TOTAL_HOSPITALIZACOES'] / df_completo['TOTAL_CASOS']) * 100 )
    df_completo['PERC_CASOS_HOSP'] = df_completo['PERC_CASOS_HOSP'].round(2)
    df_completo = df_completo.drop(columns=["BAIRRO_MERGE"])
        
    return df_completo

@st.cache_data(ttl=3600)
def carregar_dados_populacao():
    url = (
        "https://esigportal2.recife.pe.gov.br/arcgis/rest/services/"
        "Hosted/Bairros_Censo2022_final/FeatureServer/0/query"
    )

    params = {
        "where": "1=1",
        "outFields": "ebairrnomeof,sum_v0001",
        "returnGeometry": "false",
        "f": "json"
    }

    dados = requests.get(url, params=params).json()

    df_populacao = pd.DataFrame(
        [item["attributes"] for item in dados["features"]]
    )

    df_populacao = df_populacao.rename(columns={
        "ebairrnomeof": "NM_BAIRRO",
        "sum_v0001": "POPULACAO"
    })

    return df_populacao

# NOTÍCIAS
@st.cache_data(ttl=3600)
def carregar_noticias():    
    df_noticias = pd.read_csv(r"./data/processed/news.csv", encoding='utf-8')
    return df_noticias