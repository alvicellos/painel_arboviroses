import pandas as pd
import requests
import streamlit as st
from unidecode import unidecode

@st.cache_data(ttl=3600)
def carregar_dados_casos(fonte):
    
    #df_chik = pd.read_csv(r"data/resources_b300a634-1ab7-49fc-8592-4b45227822a8_casos-confirmados-de-chikungunya-em-2025.csv", sep=";", encoding='utf-8')
    df_chik = pd.read_csv(fonte, sep=";", encoding='utf-8')
    
    #df_chik['DT_OBITO_FORM'] = pd.to_timedelta(df_chik['DT_OBITO'], unit='D') + pd.Timestamp('1899-12-30') #transformação das colunas de data representadas por valores inteiros

    colunas_analise = [
        'NU_NOTIFIC', # placeholder para identificação de cada instância 
        'NU_ANO', 
        'DT_NASC',
        'CS_SEXO',
        'CS_ESCOL_N',
        'NM_BAIRRO',
        #'DT_OBITO_FORM', # retirar
        'HOSPITALIZ',
        'EVOLUCAO',
        'CLASSI_FIN'
        ]

    df_filtrado_colunas = df_chik[colunas_analise]
    
    # ----------------------------------------------------------------------
    # RETIRAR CASOS NOTIFICADOS, MAS DESCARTADOS NA CLASSIFICAÇÃO FINAL
    # ----------------------------------------------------------------------    
    df_confirmados = df_filtrado_colunas[df_filtrado_colunas['CLASSI_FIN'] != 5]
    
    # ----------------------------------------------------------------------
    # CONSIDERAR CASOS COM OCORRÊNCIA DE HOSPITALIZAÇÂO - AQUI TEMOS OS CASOS NÃO DESCARTADOS EM QUE HOUVE HOSPITALIZAÇÃO
    # ----------------------------------------------------------------------    
    df_hospitalizacoes = df_confirmados[df_filtrado_colunas['HOSPITALIZ'] == 2].reset_index(drop=True)   
    
    # ----------------------------------------------------------------------
    # OPERAÇÃO DIRETA PARA CONTAGEM DOS CASOS POR BAIRRO
    # ----------------------------------------------------------------------    
    df_bairros = df_confirmados['NM_BAIRRO'].value_counts().reset_index()
    df_bairros.columns = ['NM_BAIRRO', 'CONTAGEM']
    
    # ----------------------------------------------------------------------
    # PROCESSAMENTO AGREGADO
    # ----------------------------------------------------------------------
    
    df_agregado = (
        df_confirmados.groupby('NM_BAIRRO')
        .agg(
            TOTAL_CASOS=('NM_BAIRRO', 'size'),
            TOTAL_HOSPITALIZACOES=('HOSPITALIZ', lambda x: (x == 2).sum()),
            TOTAL_OBITOS=('EVOLUCAO', lambda x: (x == 2).sum()) # Óbito pelo agravo
        )
        .reset_index()
    )  
        
    return df_agregado, df_hospitalizacoes

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

# ----------------------------------------------------------------------
# NOTÍCIAS
# ----------------------------------------------------------------------

def carregar_noticias():
    df_noticias = pd.read_csv(r"./data/news.csv", encoding='utf-8')
    return df_noticias
