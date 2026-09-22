import pandas as pd
import json
import numpy as np
from functools import reduce
import streamlit as st
import time
from src.carga_preparacao import carregar_dados_casos, carregar_dados_populacao, criar_analise, carregar_noticias

palavras_chave = [
    "arbovirose",
    "dengue",
    "chikungunya",
    "zika",
    "Aedes aegypti",
    "mosquito",
    "vetor",
    "epidemiologia",
    "incidência",
    "prevalência",
    "hospitalização",
    "mortalidade",
    "letalidade",
    "surto",
    "vigilância epidemiológica",
    "pernilongo",
    "muriçoca",
]

if "dados_exibir" not in st.session_state:    
    st.session_state.dados_exibir = "Exibir dados originais (ano de 2025)"
if "arquivo_usuario" not in st.session_state:    
    st.session_state.arquivo_usuario = None
if "subtitulo_dados" not in st.session_state:    
    st.session_state.subtitulo_dados = ""    

if st.session_state.arquivo_usuario == None:
    st.session_state.dados_exibir = "Exibir dados originais (ano de 2025)"   

df_populacao = carregar_dados_populacao()

# Precisa ?
if st.session_state.arquivo_usuario == None:
    arquivo = r"data/resources_b300a634-1ab7-49fc-8592-4b45227822a8_casos-confirmados-de-chikungunya-em-2025.csv"    
    df_casos_carregados, df_hospitalizacoes = carregar_dados_casos(arquivo)    
    df_analise = criar_analise(df_casos_carregados, df_populacao)

arquivo = r"data/resources_b300a634-1ab7-49fc-8592-4b45227822a8_casos-confirmados-de-chikungunya-em-2025.csv"    
df_casos_carregados, df_hospitalizacoes = carregar_dados_casos(arquivo)    
df_analise = criar_analise(df_casos_carregados, df_populacao)

if st.session_state.dados_exibir == "Exibir dados originais (ano de 2025)":
    if "df_casos_carregados" not in st.session_state:
        st.session_state.df_casos_carregados = df_casos_carregados    
    if "df_hospitalizacoes" not in st.session_state:
        st.session_state.df_hospitalizacoes = df_hospitalizacoes    
    if "df_analise" not in st.session_state:
        st.session_state.df_analise = df_analise    
    if "subtitulo_dados" not in st.session_state:
        st.session_state.subtitulo_dados = ''' ## Incidência de casos confirmados de dengue ou chikungunya na cidade do Recife (2025)'''
    
    # Para recarregar na exclusão do arquivo
    st.session_state.df_casos_carregados = df_casos_carregados
    st.session_state.df_hospitalizacoes = df_hospitalizacoes
    st.session_state.df_analise = df_analise
    st.session_state.subtitulo_dados = ''' ## Incidência de casos confirmados de dengue ou chikungunya na cidade do Recife (2025)'''

st.divider()

# ----------------------------------------------------------------------
# TELA
# ----------------------------------------------------------------------

st.title('Gravidade clínica dos casos de arboviroses - Chikungunya e Dengue - na cidade do Recife')
st.divider()

st.subheader("Problema de negócio e objetivos:")
#st.write("Verificar os três bairros do município do Recife com maior proporção de mortes por casos confirmados de chikungunya")

st.write("Orientar gestores em saúde a respeito das localidades de ocorrência dos casos mais graves de chikungunya, a partir da proporção de hospitalizações por casos confirmados e da incidência total de casos na população.")

st.subheader("KIPs:")
st.markdown(
    '''
    * Visualizar os bairros com maiores incidências:
       - por total de casos, 
       - por incidência em 100k hab, 
       - por percentual de hospitalizações
    * em até 4 cliques;
    * incorporar dados de outros anos nas exibições;
    * prazo imediato (este TP)
    '''
    )

# Registros de casos confirmados de dengue ou chikungunya na cidade do Recife (ano ou usuário)
st.session_state.subtitulo_dados
st.session_state.df_hospitalizacoes

''' ### Ocorrência por bairros:'''
st.session_state.df_analise

''' #### Filtre a visualização dos dados com os controles abaixo:'''

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
    ["Exibir dados originais (ano de 2025)", 
    "Exibir dados do usuário"]
    )    
    st.session_state.dados_exibir = radio_rodar_arquivo
    botao_filtrar_dados = st.button("Aplicar alterações na tela")
    st.write("Os dados escolhidos serão exibidos nas tabelas acima.")
    
    if botao_filtrar_dados:
        st.write("Alterações aplicadas")
        time.sleep(1.5)        
        if st.session_state.dados_exibir == "Exibir dados do usuário":    
            df_casos_carregados_1, df_hospitalizacoes_1 = carregar_dados_casos(st.session_state.arquivo_usuario)            
            df_analise_1 = criar_analise(df_casos_carregados_1, df_populacao)             
            # Para trocar os dados exibidos
            st.session_state.df_casos_carregados = df_casos_carregados_1
            st.session_state.df_hospitalizacoes = df_hospitalizacoes_1              
            st.session_state.df_analise = df_analise_1
            st.session_state.subtitulo_dados = ''' ## Incidência de casos confirmados de dengue ou chikungunya na cidade do Recife - fornecido pelo usuário'''        
            st.rerun()
            
        elif st.session_state.dados_exibir == "Exibir dados originais (ano de 2025)":
            st.session_state.df_casos_carregados = df_casos_carregados
            st.session_state.df_hospitalizacoes = df_hospitalizacoes
            st.session_state.df_analise = df_analise
            st.session_state.subtitulo_dados = ''' ## Incidência de casos confirmados de dengue ou chikungunya na cidade do Recife (2025)'''
            st.rerun()          

#if arquivo_usuario is None and st.session_state.dados_exibir != "Exibir #dados originais (ano de 2025)":
#    st.rerun()
    
st.divider()
st.subheader("Últimas notícias relacionadas")
df_news = carregar_noticias()

contagem_chaves = 0
for index, row in df_news.iterrows():
    for palavra in palavras_chave:
        if palavra in row['resumo_materia']:
            contagem_chaves += 1
            
num_palavras_chave, palavras_chave_resumos, col_palavras = st.columns(3)

with num_palavras_chave:    
    st.metric(label="Palavras chave:", value=len(palavras_chave))

with palavras_chave_resumos:
    st.metric(label="Palavras-chave nos resumos:", value=contagem_chaves)

with col_palavras:
    f'''Palavras-chave: *{", ".join(palavras_chave)}*'''
    
st.write("\n")

for index, row in df_news.iterrows():
    f"""###### {row['titulo_noticia']}"""
    f"""*Publicado em: {row['hora_publi_origem']}*"""
    f"""*{row["resumo_materia"]}*"""

""" #### Links úteis para as iniciativas e fontes de inspiração do projeto."""
st.markdown(f"Dataset (2025) em [dataset](https://dados.recife.pe.gov.br/pt_BR/dataset/casos-de-dengue-zika-e-chikungunya/resource/b300a634-1ab7-49fc-8592-4b45227822a8)") 
st.markdown("*a plataforma disponibiliza dados a partir do ano de 2015*")
st.markdown(f"Metadados do registro de casos em JSON [metadados](https://dados.recife.pe.gov.br/pt_BR/dataset/casos-de-dengue-zika-e-chikungunya/resource/2b62054a-6709-4678-b26d-595c92921a9b)")
st.markdown(f"ODS escolhido: [3 - Saúde e Bem-Estar](https://gtagenda2030.org.br/ods/ods3/)")

if arquivo_usuario is None and st.session_state.dados_exibir != "Exibir dados originais (ano de 2025)":
    st.rerun()