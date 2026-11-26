import streamlit as st

# --------------------------------------------------------------------------------------------------------------------- Configuração da página
st.set_page_config(layout="wide")

# --------------------------------------------------------------------------------------------------------------------- DEFINIÇÃO DE VARIÁVEIS; CONTROLE DE FLUXO

# if "dados_exibir" not in st.session_state:    
#     st.session_state.dados_exibir = "Exibir dados originais (2015 a 2025)"
# if "arquivo_usuario" not in st.session_state:    
#     st.session_state.arquivo_usuario = None
# if "subtitulo_dados" not in st.session_state:    
#     st.session_state.subtitulo_dados = ""    

#if st.session_state.arquivo_usuario == None:
#    st.session_state.dados_exibir = "Exibir dados originais (2015 a 2025)"   

#if st.session_state.dados_exibir == "Exibir dados originais (2015 a 2025)":
    # if "df_bairros_hosp" not in st.session_state:
    #     st.session_state.df_bairros_hosp = df_bairros_hosp    
    # if "df_bairros_todos" not in st.session_state:
    #     st.session_state.df_bairros_todos = df_bairros_todos    
    # if "df_analise" not in st.session_state:
    #     st.session_state.df_analise = df_analise    
#    if "subtitulo_dados" not in st.session_state:
#        st.session_state.subtitulo_dados = ''' ## Incidência de casos confirmados de dengue ou chikungunya na cidade do Recife:'''    
    # Para recarregar os dados originais na exclusão do arquivo carregado pelo usuário
    #st.session_state.df_bairros_hosp = df_bairros_hosp
    #st.session_state.df_bairros_todos = df_bairros_todos
    #st.session_state.df_analise = df_analise
#    st.session_state.subtitulo_dados = ''' ## Incidência de casos confirmados de dengue ou chikungunya na cidade do Recife:'''
    
# ---------------------------------------------------------------------------------------------------------------------  TELA

st.divider()
st.title('🦟 Gravidade clínica dos casos de Chikungunya na cidade do Recife:')
st.divider()

st.title('O que temos aqui ? 🦟🌡️🩺💊🩸🏥🩹🤕')

#st.subheader("Problema de negócio e objetivos:")
#st.write("Verificar os três bairros do município do Recife com maior proporção de mortes por casos confirmados de chikungunya")

#st.write("Orientar gestores em saúde a respeito das localidades de ocorrência dos casos mais graves de chikungunya, a partir da proporção de hospitalizações por casos confirmados e da incidência total de casos na população.")

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

st.markdown("""
### 🦟 Conheça o painel
Explore dados obtidos pela API da Prefeitura do Recife para identificar
os bairros com maior gravidade dos casos de chikungunya,
considerando hospitalizações e óbitos entre os casos confirmados.

### 🔎 Entenda os dados
Na página **Dados**, conheça a base utilizada, explore os registros com filtros
e entenda os conceitos e critérios de tratamento que orientam as análises.

### 💬 Consulte o assistente de análise
Na página **Análises**, abra **Assistente de análise** para fazer perguntas
sobre os indicadores e receber sugestões de filtros para conferir nos gráficos.

### 📰 Acompanhe as notícias
Na página **Notícias**, encontre conteúdos relevantes para o tema coletados no site da Fiocruz.
""")