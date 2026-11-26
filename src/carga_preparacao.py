import pandas as pd
import requests
import streamlit as st
from unidecode import unidecode
import json
from pathlib import Path
#import time
from typing import Any

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"

# Colunas de interesse nos dados
fields = [
    "NU_NOTIFIC",
    "NU_ANO",
    "DT_NASC", 
    "CS_SEXO", 
    #"CS_ESCOL_N",
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
    #"tp_escolaridade",
    "no_bairro_residencia",
    "st_ocorreu_hospitalizacao",
    "tp_evolucao_caso",
    "tp_classificacao_final"
]

def download_dados_api(colunas, colunas_2020_menos, gravar=False):    
    
    # Coletando os metadados dos recursos para definir as IDs dos datasets a importar
    metadados_chikg = requests.get("https://dados.recife.pe.gov.br/api/action/package_show?id=casos-de-dengue-zika-e-chikungunya")
    dict_response = metadados_chikg.json()
    results = dict_response['result']
    resources = results['resources']        
    
    ids_importar = [id['id'] for id in resources if "casos" in id['name'].lower() and "chikungunya" in id['name'].lower() and id['format'].lower().strip() == "csv"] # IDs para consultar (estão disponíveis dados de 2015 e 2025)
    nomes_importar = [name['name'] for name in resources if "casos" in name['name'].lower() and "chikungunya" in name['name'].lower()]
    nomes_2020_menos = [str(ano) for ano in range(2015, 2021)]             # primeiro ano da série histórica é 2015, até 2020 a nomenclatura das colunas foi diferente    
    
    dados_paginacao = []
    max_entradas_contrato = 500                                            # número máximo de registros enviados pelo site a cada request (testado)
        
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

@st.cache_data(ttl=3600)
def carregar_dados_populacao(download=False):
    
    '''
    Baixa os dados de população de 2022 se a api estiver online, caso
    contrário lê os dados do cache JSON. Retorna a fonte utilizada.
    Com download=True, salva os dados em "data\processed\populacao_2022.json"
    '''
    
    try:
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

        dados = requests.get(url, params=params, timeout=10)
        dados.raise_for_status()
        dados = dados.json()
        
        df_populacao = pd.DataFrame(
            [item["attributes"] for item in dados["features"]]
        )
        
        fonte = "api"
        
        if download:
            df_populacao.to_json(PROCESSED / 'populacao_2022.json', orient='records')
    
    except:        
        df_populacao = pd.read_json(PROCESSED / 'populacao_2022.json')
        fonte = "cache"
    
            
    df_populacao = df_populacao.rename(columns={
            "ebairrnomeof": "NM_BAIRRO",
            "sum_v0001": "POPULACAO"
        })    
    
    return df_populacao, fonte

# def tratamento_api(df_api):
    
#     cod_hospitalizacao = {
#         1: "Sim",
#         2: "Não",
#         9: "Ignorado"
#     }
    
#     cod_class_fin = {
#         5 : "Descartado",
#         10: "Dengue",
#         11: "Dengue com sinais de alarme",
#         12: "Dengue grave",
#         13: "Chikungunya"
#     }
    
#     bairros_truncados = {
#         "ALTO JOSE DO PINH": "ALTO JOSE DO PINHO",
#         "BEERIBE": "BEBERIBE",
#         "BREJO": "BREJO DA GUABIRABA",
#         "BREJO DE GUABIRABA": "BREJO DA GUABIRABA",
#         "BEERIBE": "BEBERIBE",
#         "CACOTE": "CAÇOTE",
#         "CAMPO": "CAMPO GRANDE",                          # checar
#         "CASA": "CASA AMARELA",
#         "CATUEIRO": "CAJUEIRO",                           # checar
#         #"CATUEIRO": "CAJUEIRO,                           # checar
#         "CORREGO DO JENPAPO": "CORREGO DO JENIPAPO",
#         "CORREGO JENIPAPO": "CORREGO DO JENIPAPO",
#         "ENGENHO MEIO": "ENGENHO DO MEIO",
#         "ILHA DE RETIRO": "ILHA DO RETIRO",
#         "MAD": "MADALENA",                                 # checar
#         "MONTERIO": "MONTEIRO",
#         "NOVA": "NOVA DESCOBERTA",                          # checar
#         "VAR\\EA": "VARZEA",
#         "VASO DA GAMA": "VASCO DA GAMA"
#     }
    
#     anos_excluir = [2015, 2016]                                                    # excluir porque existem muitos registros com dados faltantes na coluna bairros
#     df_tratado = df_api.drop(df_api[df_api['NU_ANO'].isin(anos_excluir)].index)
#     df_tratado['HOSPITALIZ'] = df_tratado.map(cod_hospitalizacao)
#     df_tratado['CLASSI_FIN'] = df_tratado.map(cod_class_fin)
#     df_tratado['NM_BAIRROS'] = df_tratado.map(bairros_truncados)
    
#     # Regularização dos nomes dos bairros
#     return df_tratado

@st.cache_data(ttl=3600)
def carregar_dados_fonte(arquivo_csv=None, json=True):         # fonte será json gravado ou arquivo fornecido pelo usuário
    ''' 
    Pode carregar TANTO os dados da série histórica de casos da doença do json salvo em "data\processed"
    COMO um arquivo fornecido pelo usuário, com arquivo=nome_do_arquivo, json=False
    Retorna um DataFrame com os dados.
    Para carregar diretamente do json salvo, basta invocar sem parâmetros
    '''
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
def agregacao_bairros(df):    
    '''
    Retorna quantidade de casos (confirmados) agregado por bairro - df_bairro_todos
    Quantidade de hospitalizações (pela doença, confirmadas) agregados por bairro - df_bairro_com_hosp    
    NM_BAIRRO - TOTAL_CASOS
    NM_BAIRRO - TOTAL_CASOS - TOTAL_HOSPITALIZACOES - TOTAL_OBITOS
    '''
    
    # Casos por bairro e ano
    df_bairro_todos = (
        df
        .groupby(['NM_BAIRRO', 'NU_ANO'])
        .agg(
            TOTAL_CASOS=('NM_BAIRRO', 'size')
        )
        .reset_index()
        .sort_values(['NM_BAIRRO', 'NU_ANO'])
    )

    # Casos, hospitalizações e óbitos por bairro
    df_bairro_com_hosp = (
        df
        .groupby('NM_BAIRRO')
        .agg(
            TOTAL_CASOS=('NM_BAIRRO', 'size'),
            TOTAL_HOSPITALIZACOES=(
                'HOSPITALIZ', lambda x: (x == 1).sum()
            ),
            TOTAL_OBITOS=(
                'EVOLUCAO', lambda x: (x == 2).sum()
            )
        )
        .reset_index()
    )

    # Casos, hospitalizações e óbitos por bairro e ano
    df_bairro_ano = (
        df
        .groupby(['NM_BAIRRO', 'NU_ANO'])
        .agg(
            TOTAL_CASOS=('NM_BAIRRO', 'size'),
            TOTAL_HOSPITALIZACOES=(
                'HOSPITALIZ', lambda x: (x == 1).sum()
            ),
            TOTAL_OBITOS=(
                'EVOLUCAO', lambda x: (x == 2).sum()
            )
        )
        .reset_index()
        .sort_values(['NM_BAIRRO', 'NU_ANO'])
    )

    return df_bairro_todos, df_bairro_com_hosp, df_bairro_ano


def criar_analise(dataframe_casos, dataframe_populacao):
    
    dataframe_analise = dataframe_casos.copy()
    dataframe_analise['BAIRRO_MERGE'] = dataframe_analise['NM_BAIRRO'].str.upper().apply(unidecode)
    dataframe_populacao['BAIRRO_MERGE'] = dataframe_populacao['NM_BAIRRO'].str.upper().apply(unidecode)
    df_completo = dataframe_analise.merge(
        dataframe_populacao[['BAIRRO_MERGE', 'POPULACAO']],
        on="BAIRRO_MERGE",
        how="left"
        )   
    
    # Cálculo da indicência por 100k habitantes
    df_completo["INCIDENCIA_100K"] = (
        df_completo["TOTAL_CASOS"] / df_completo["POPULACAO"]) * 100_000   
    df_completo["INCIDENCIA_100K"] = df_completo["INCIDENCIA_100K"].round(2)
    
    # Cálculo do percentual de internações por casos
    df_completo['PERC_CASOS_HOSP'] = ((df_completo['TOTAL_HOSPITALIZACOES'] / df_completo['TOTAL_CASOS']) * 100 )
    df_completo['PERC_CASOS_HOSP'] = df_completo['PERC_CASOS_HOSP'].round(2)
    df_completo = df_completo.drop(columns=["BAIRRO_MERGE"])
    
    # TODO # Quais o melhor cálculo para uma métrica incluindo o número de óbitos? Percentual de óbitos por casos ou percentual de óbitos por hospitalizações ?
    # TODO # Ou por população, ou por incidências
        
    return df_completo


# ------------------------------------------------------------------------------------------------ Separar em download dos dados e carga direta pela API
# Alteração foi para tratar os nomes dos bairros


# NOTÍCIAS
@st.cache_data(ttl=3600)
def carregar_noticias():    
    df_noticias = pd.read_csv(r"./data/processed/news.csv", encoding='utf-8')
    #df_noticias = pd.read_csv(PROCESSED / "news.csv", encoding='utf-8')
    return df_noticias


# TODO # Trazer a lista 'anos' anos = [x for x in range(2017, 2026)] e anos_excluir = [2015, 2016] de comum.py

#TODO #
anos = [x for x in range(2017, 2026)]

@st.cache_data(ttl=3600)
def tratamento_dados(dados_api):
        print("------------------------- FUNÇÂO TRATAMENTO ---------------------------")
    #for ano in anos:
        print("\n*** FUNÇÂO TRATAMENTO ***\n")
        colunas_drop = ["EVOLUCAO", "CLASSI_FIN", "NM_BAIRRO"] # Se nan
        
        total_registros = len(dados_api)
        print(f"Total de registros:\n {total_registros}")

        # TODO #
        anos_excluir = [2015, 2016]  # excluir porque existem muitos registros com dados faltantes na coluna bairros
        df_tratado = dados_api.drop(dados_api[dados_api['NU_ANO'].isin(anos_excluir)].index)
        
        cod_hospitalizacao = {
            1: "Sim",
            2: "Não",
            9: "Ignorado"
            }
        
        #cod_hospitalizacao = {float(x): cod_hospitalizacao[x] for x in cod_hospitalizacao}
        
        cod_class_fin = {
            5 : "Descartado",
            10: "Dengue",
            11: "Dengue com sinais de alarme",
            12: "Dengue grave",
            13: "Chikungunya"
        }
        
        cod_evolucao = {
            1: "cura",
            2: "óbito pelo agravo",
            3: "óbito por outras causas",
            4: "óbito em investigação",
            9: "ignorado"
        }
        
        # tp_classificacao_final
        # nos
        # 5-Descartado
        # 10-Dengue
        # 11-Dengue com
        # sinais de alarme
        # 12-Dengue grave
        # 13-Chikungunya
       
        # ‘ ‘, 0 , 9 Ignorado
        # 1 Confirmado
        # 2 Descartado
        # 8 Inconclusivo
        
        # 1, 2, 5, 13 (presentes nos dados)
        # 1 - Dengue Clássico, 2 - Dengue com Complicações, 3 - Febre Hemorrágica do Dengue – FHD, 4 – Síndrome do choque da Dengue – SCD, 5 -Descartado, 8-Inconclusivo, 10-Dengue, 11-Dengue com sinais de alarme, 12-Dengue grave"
        
        #cod_class_fin = {float(x): cod_class_fin[x] for x in cod_class_fin}
        
        bairros_truncados = {
            "ALTO JOSE DO PINH": "ALTO JOSE DO PINHO",
            "BEERIBE": "BEBERIBE",
            "BREJO": "BREJO DA GUABIRABA",
            "BREJO DE GUABIRABA": "BREJO DA GUABIRABA",
            "BEERIBE": "BEBERIBE",
            "CACOTE": "CAÇOTE",
            "CAMPO": "CAMPO GRANDE",                          # checar
            "CASA": "CASA AMARELA",
            "CATUEIRO": "CAJUEIRO",                           # checar
            #"CATUEIRO": "CAJUEIRO,                           # checar
            "CORREGO DO JENPAPO": "CORREGO DO JENIPAPO",
            "CORREGO JENIPAPO": "CORREGO DO JENIPAPO",
            "ENGENHO MEIO": "ENGENHO DO MEIO",
            "ILHA DE RETIRO": "ILHA DO RETIRO",
            "MAD": "MADALENA",                                 # checar
            "MONTERIO": "MONTEIRO",
            "NOVA": "NOVA DESCOBERTA",                          # checar
            "VAR\\EA": "VARZEA",
            "VASO DA GAMA": "VASCO DA GAMA"
        }     
        
        df_tratado['HOSPITALIZ'] = df_tratado['HOSPITALIZ'].map(cod_hospitalizacao)
        df_tratado['CLASSI_FIN'] = df_tratado['CLASSI_FIN'].map(cod_class_fin)
        df_tratado['EVOLUCAO'] = df_tratado['EVOLUCAO'].map(cod_evolucao)
        # df_tratado['NM_BAIRROS'] = df_tratado.map(bairros_truncados)
        
        # for hosp in dados_api['HOSPITALIZ'].unique():
        #     if not pd.isna(hosp):
        #         print(f"Preenchimento de 'HOSPITALIZ' com {cod_hospitalizacao[hosp]}: {len(dados_api[dados_api['HOSPITALIZ'] == hosp])}")                
        
        # for hosp1 in df_tratado['HOSPITALIZ'].unique():
        #     if not pd.isna(hosp1):
        #         print(f"Preenchimento de 'HOSPITALIZ' com {hosp1}: {len(df_tratado[df_tratado['HOSPITALIZ'] == hosp1])}") 
        #         #time.sleep(1)               
                
        # # for evol in dados_api['EVOLUCAO'].unique():
        # #         if not pd.isna(evol):
        # #             print(f"Preenchimento de 'EVOLUCAO' com {evol}: {len(dados_api[dados_api['EVOLUCAO'] == evol])}")
                    
        # for evol in df_tratado['EVOLUCAO'].unique():
        #     if not pd.isna(evol):
        #         print(f"Preenchimento de 'EVOLUCAO' com {evol}: {len(df_tratado[df_tratado['EVOLUCAO'] == evol])}")
        #         #time.sleep(1)
                    
        # # for classi in dados_api['CLASSI_FIN'].unique():
        # #    if not pd.isna(classi):
        # #        print(f"Preenchimento de 'CLASSI_FIN' {classi}")
        # #       print(f"Preenchimento de 'EVOLUCAO' com {cod_class_fin[classi]}")
        # #       : {len(dados_api[dados_api['CLASSI_FIN'] == classi])}")
        
        # for classi in df_tratado['CLASSI_FIN'].unique():
        #     if not pd.isna(classi):
        #         #print(f"Preenchimento de 'CLASSI_FIN' {classi}")
        #         print(f"Preenchimento de 'CLASSI_FIN' com {classi}: {len(df_tratado[df_tratado['CLASSI_FIN'] == classi])}")
        #         #time.sleep(1)
        
        # for col in colunas_drop:
        #     colunas_stats = dados_api[dados_api[col].isna()]    
        #     print(f"Quantidade de registros com {col} vazias: {len(colunas_stats)}")
        #     #time.sleep(1)
        
        print()
        # df_sem_linhas_vazias = dados_api.dropna(subset=colunas_drop)        
        df_tratado = df_tratado.dropna(subset=colunas_drop)        
        registros_sem_linha_vazia = len(df_tratado)
        print(f"Total de registro após exclusão das colunas {', '.join(colunas_drop)}: {registros_sem_linha_vazia}")
        print(f"Correspondendo a uma diminuição de {100 - ((len(df_tratado) / total_registros) * 100):.2f}%")
        print()
        
        print("------------------------- FIM FUNÇÂO TRATAMENTO ---------------------------")
        
        return total_registros, registros_sem_linha_vazia, df_tratado

def mostrar_preenchimento(dados: pd.DataFrame, colunas_analise: list):
    leitura_preenchimento = {col: [] for col in colunas_analise}
    for col in colunas_analise:
        for codigo in dados[col].unique():
            if not pd.isna(codigo):
                #print(f"Preenchimento de {col} com {codigo}: {len(dados[dados[col] == codigo])}")             
                leitura_preenchimento[col].append({int(codigo) : len(dados[dados[col] == codigo])})
            else:
                linhas_com_vazio = dados.isna().any(axis=1).sum()
                leitura_preenchimento[col].append({"vazio" : int(linhas_com_vazio)})
                        
    return leitura_preenchimento


def preparar_metricas_pag_dados(contagem_preenchimento: dict, colunas_analise: dict):
    for col in colunas_analise:
        st.subheader(f"{col} - {colunas_analise[col]}")
        colunas_exibir = st.columns(len(contagem_preenchimento[col]))    
        for index, dados_metricas in enumerate(contagem_preenchimento[col]):
            try:
                with colunas_exibir[index]:
                    for key, value in dados_metricas.items():
                        st.metric(
                                label=str(key),
                                value=str(value) + " casos",
                                #delta="+8,2%",
                                #chart_data=[100, 150, 180, 250, 320, 410, 500],
                                #chart_type="bar",
                                border=True
                            )
            except:
                print(index, dados_metricas)
                
def preparar_metricas_graficos_dados(contagem_preenchimento: dict, colunas_analise: dict):
    print(contagem_preenchimento)
    colunas_exibir = st.columns(len(colunas_analise))
    for index, col in enumerate(colunas_analise):
        X = [list(x.keys()) for x in contagem_preenchimento[col]]
        Y = [list(y.values()) for y in contagem_preenchimento[col]]
        
        X = [str(x[0])for x in X]
        Y = [int(y[0]) for y in Y]
        
        df = pd.DataFrame({
            "X" : X,
            "Y" : Y,
        })
        
        with colunas_exibir[index]:
            st.bar_chart(
                df,
                x="X",
                y="Y",
                horizontal=False,
                x_label=col
            )

def excluir_por_valor(
    df: pd.DataFrame,
    coluna: str,
    valor: Any,
    excluir_vazios: bool = False ) -> tuple[pd.DataFrame, int, int] | None:
    
    """
    Returns:
        tuple[pd.DataFrame, int, int]:
            DataFrame filtrado, número de registros excluídos pelo valor
            e número de registros vazios excluídos (0 se excluir_vazios=False).
    """
    
    vazios_excluidos = 0
    
    try:
        if isinstance(valor, list):
            filtro = df[coluna].isin(valor)
        else:
            filtro = df[coluna] == valor

        n_registros_excluidos = int(filtro.sum())
        df = df[~filtro]
    
        if excluir_vazios:
            registros_vazios = df[coluna].isna()
            vazios_excluidos = int(registros_vazios.sum())
            df = df.dropna(subset=[coluna])
        
        return df, n_registros_excluidos, vazios_excluidos
    
    except KeyError:
        print(f"Erro: a coluna '{coluna}' não existe no DataFrame.")
        raise
    
    except TypeError as erro:
        print(f"Erro: tipo de dado incompatível. Detalhes: {erro}")
        raise

    except Exception as erro:
        print(f"Erro inesperado: {type(erro).__name__}: {erro}")
        raise

def excluir_varios_valores(
        df: pd.DataFrame,
        coluna: str,
        valores: list,
        excluir_vazios: bool = False) -> tuple[pd.DataFrame, list[int]]:
    
    n_valores_excluidos = []
        
    for valor in valores:
        df_pos_exclusao, n_linhas_excluidas, n_vazias_excluidas = excluir_por_valor(
            df, 
            coluna, 
            valor, 
            excluir_vazios=excluir_vazios)
        
        df = df_pos_exclusao
        n_valores_excluidos.append(n_linhas_excluidas)
    
    return df, n_valores_excluidos