import pandas as pd
import json
import numpy as np
from functools import reduce
import streamlit as st
import time
from src.carga_preparacao import carregar_dados_fonte, carregar_dados_populacao, agregacao_bairros, criar_analise, carregar_noticias

# ----------------------------------------------------------------------
# Configuração da página
# ----------------------------------------------------------------------

st.set_page_config(layout="wide")

# ----------------------------------------------------------------------
# DEFINIÇÃO DE VARIÁVEIS; CONTROLE DE FLUXO
# ----------------------------------------------------------------------

if "dados_exibir" not in st.session_state:    
    st.session_state.dados_exibir = "Exibir dados originais (2015 a 2025)"
if "arquivo_usuario" not in st.session_state:    
    st.session_state.arquivo_usuario = None
if "subtitulo_dados" not in st.session_state:    
    st.session_state.subtitulo_dados = ""    

if st.session_state.arquivo_usuario == None:
    st.session_state.dados_exibir = "Exibir dados originais (2015 a 2025)"   

# --------------------------------------------------------------------------------------------------- CARGA DE DADOS API POPULAÇÃO
df_populacao = carregar_dados_populacao()

# REORDENAR O DF_ANÁLSE COM AS COLUNAS DE MAIOR INTERESSE PRIMEIRO

dados = carregar_dados_fonte()                                                                        # carregar_dados_fonte(arquivo=None, json=True)
df_bairros_hosp, df_bairros_todos = agregacao_bairros(dados)                                          # casos carregados são apenas os confirmados
df_analise = criar_analise(df_bairros_hosp, df_populacao)

if st.session_state.dados_exibir == "Exibir dados originais (2015 a 2025)":
    if "df_bairros_hosp" not in st.session_state:
        st.session_state.df_bairros_hosp = df_bairros_hosp    
    if "df_bairros_todos" not in st.session_state:
        st.session_state.df_bairros_todos = df_bairros_todos    
    if "df_analise" not in st.session_state:
        st.session_state.df_analise = df_analise    
    if "subtitulo_dados" not in st.session_state:
        st.session_state.subtitulo_dados = ''' ## Incidência de casos confirmados de dengue ou chikungunya na cidade do Recife'''    
    # Para recarregar os dados originais na exclusão do arquivo carregado pelo usuário
    st.session_state.df_bairros_hosp = df_bairros_hosp
    st.session_state.df_bairros_todos = df_bairros_todos
    st.session_state.df_analise = df_analise
    st.session_state.subtitulo_dados = ''' ## Incidência de casos confirmados de dengue ou chikungunya na cidade do Recife'''

st.divider()

# --------------------------------------------------------------------------------------------------- TELA
st.title('Gravidade clínica dos casos de arboviroses 🦟 - Chikungunya e Dengue - na cidade do Recife')
st.divider()

#st.subheader("Problema de negócio e objetivos:")
#st.write("Verificar os três bairros do município do Recife com maior proporção de mortes por casos confirmados de chikungunya")

st.write("Orientar gestores em saúde a respeito das localidades de ocorrência dos casos mais graves de chikungunya, a partir da proporção de hospitalizações por casos confirmados e da incidência total de casos na população.")

# st.subheader("KIPs:")
# st.markdown(
#     '''
#     * Visualizar os bairros com maiores incidências:
#        - por total de casos, 
#        - por incidência em 100k hab, 
#        - por percentual de hospitalizações
#     * em até 4 cliques;
#     * incorporar dados de outros anos nas exibições;
#     * prazo imediato (este TP)
#     '''
#     )

# Registros de casos confirmados de dengue ou chikungunya na cidade do Recife (ano ou usuário)


# --------------------------------------------------------------------------------------------------- SUBTÍTULO
st.session_state.subtitulo_dados

# --------------------------------------------------------------------------------------------------- UM DOS DOIS COM A ANÁLISE CORRETA
''' ### Um dos dois com a análise correta '''
st.session_state.df_bairros_todos
st.session_state.df_bairros_hosp

# --------------------------------------------------------------------------------------------------- OCORRÊNCIA POR BAIRROS
# --------------------------------------------------------------------------------------------------- AGREGAR POR ANO
''' ### Ocorrência por bairros:'''
'''###### Agregar por ano:'''

st.session_state.df_analise

''' #### Filtre e ordene a visualização dos dados com os controles abaixo:'''
lista_bairros = list(st.session_state.df_analise['NM_BAIRRO'])
if "selecao_multi" not in st.session_state:
    options = st.multiselect("Selecione os bairros que deseja visualizar: ", lista_bairros)
else:
    options = st.multiselect("Selecione os bairros que deseja visualizar: ", lista_bairros, default=st.session_state.selecao_multi)

st.session_state.selecao_multi = options

option_radio = st.radio(
    "Exibir os dados ordenados por (maior para o menor): ",
    ["bairro (alfabética)", 
     "total de casos",
     "incidência por 100k/hab",
     "percentual de hospitalizações"]
    )

equivalencia_opcoes = {
    "bairro (alfabética)": "NM_BAIRRO", 
     "total de casos": "TOTAL_CASOS",
     "incidência por 100k/hab": "INCIDENCIA_100K",
     "percentual de hospitalizações": "PERC_CASOS_HOSP"
    }

crescente_decrescente = {
    "bairro (alfabética)": True , 
    "total de casos": False,
    "incidência por 100k/hab": False,
    "percentual de hospitalizações": False
         }

# if "opcao_radio" not in st.session_state:
st.session_state.opcao_radio = option_radio

if len(options) > 0:
    df_exibir = st.session_state.df_analise[st.session_state.df_analise['NM_BAIRRO'].isin(options)].sort_values(by=equivalencia_opcoes[option_radio], ascending=crescente_decrescente[option_radio])
else:
    df_exibir = st.session_state.df_analise.sort_values(by=equivalencia_opcoes[option_radio], ascending=crescente_decrescente[option_radio])

df_exibir

st.markdown("##### Se quiser, você pode pode baixar os dados filtrados aqui:")
st.download_button("Dados filtrados", df_exibir.to_csv(index=False), file_name="casos_filtro.csv")

st.divider()

""" ### Aqui você pode acrescentar arquivos de outros anos a esta análise:"""
st.write("Os arquivos estão disponíveis do Portal de Dados da Prefeitura da Cidade do Recife:")
st.markdown('''
[Casos de Dengue, Zika e Chikungunya](https://dados.recife.pe.gov.br/sv/dataset/casos-de-dengue-zika-e-chikungunya)''')

st.write("Escolha algum dos arquivos referentes aos 'Casos confirmados de Chikungunya'")

arquivo_usuario = st.file_uploader("Submeta aqui o arquivo:", type=["csv"])
st.session_state.arquivo_usuario = arquivo_usuario

if arquivo_usuario is not None:    
    st.write(f"Arquivo anexado: {arquivo_usuario.name}")
    
    radio_rodar_arquivo = st.radio(
    "Escolha os dados que deseja exibir:",
    ["Exibir dados originais (2015 a 2025)", 
    "Exibir dados do usuário"]
    )    
    st.session_state.dados_exibir = radio_rodar_arquivo
    botao_filtrar_dados = st.button("Aplicar alterações na tela")
    st.write("Os dados escolhidos serão exibidos nas tabelas acima.")
    
    if botao_filtrar_dados:
        st.write("Alterações aplicadas")
        time.sleep(1.5)        
        if st.session_state.dados_exibir == "Exibir dados do usuário":
            
            dados_usuario = carregar_dados_fonte(st.session_state.arquivo_usuario, json=False)
            # df_bairros_hosp_1, df_bairros_todos_1 = carregar_dados_fonte(st.session_state.arquivo_usuario, json=False)
            df_bairros_hosp_1, df_bairros_todos_1 = agregacao_bairros(dados_usuario)
            df_analise_1 = criar_analise(df_bairros_hosp_1, df_populacao)           
            
            # Refatoração
            # dados = carregar_dados_fonte() # carregar_dados_fonte(arquivo=None, json=True)
            # df_bairros_hosp, df_bairros_todos = agregacao_bairros(dados)
            # df_analise = criar_analise(df_bairros_hosp, df_populacao)
            
            # Para trocar os dados exibidos
            st.session_state.df_bairros_hosp = df_bairros_hosp_1
            st.session_state.df_bairros_todos = df_bairros_todos_1              
            st.session_state.df_analise = df_analise_1
            st.session_state.subtitulo_dados = ''' ## Incidência de casos confirmados de dengue ou chikungunya na cidade do Recife - fornecido pelo usuário'''        
            st.rerun()
            
        elif st.session_state.dados_exibir == "Exibir dados originais (2015 a 2025)":
            st.session_state.df_bairros_hosp = df_bairros_hosp
            st.session_state.df_bairros_todos = df_bairros_todos
            st.session_state.df_analise = df_analise
            st.session_state.subtitulo_dados = ''' ## Incidência de casos confirmados de dengue ou chikungunya na cidade do Recife'''
            st.rerun()          

#if arquivo_usuario is None and st.session_state.dados_exibir != "Exibir #dados originais (2015 a 2025)":
#    st.rerun()
    
# st.divider()
    
if arquivo_usuario is None and st.session_state.dados_exibir != "Exibir dados originais (2015 a 2025)":
    st.rerun()