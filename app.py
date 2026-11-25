import streamlit as st
from src.carga_preparacao import carregar_dados_fonte, carregar_dados_populacao
from comum import inicializar_estado


dados = carregar_dados_fonte()

# TODO # Validação entradas e saídas API para serviço da LLM (a final)

inicializar_estado()
#df_limpo_classi, n_linhas_excluidas_classi, n_vazias_excluidas_classi = gerar_dados_analise()

pagina = st.navigation(
    {
        "Painel": [
            st.Page("paginas/inicio.py", title="Início", icon="🏠", default=True),
            # st.Page("paginas/bairro.py", title="Por bairro", icon="📊"),
            # st.Page("paginas/usuario.py", title="Análises usuário", icon="📊"),
            #st.Page("paginas/noticias.py", title="Notícias", icon="⭐"),
            st.Page("paginas/dados.py", title="E esses dados ?", icon="🎲"),
            #st.Page("paginas/analises.py", title="Análises", icon="🎯"),
            st.Page("paginas/integracao_llm.py", title="Pergunte aos dados", icon="📰"),
            st.Page("paginas/analises.py", title="Análises", icon="🎯"),
            st.Page("paginas/noticias.py", title="Notícias", icon="📰"),            
            # st.Page("paginas/links.py", title="Links / Inspirações", icon="📊"),
            #st.Page("paginas/desmatamento.py", title="Desmatamento (PRODES)", icon="🌳"),
        ],
        # "Fontes e texto": [
        #     st.Page("paginas/noticias.py", title="Notícias", icon="📰"),
        #     st.Page("paginas/palavras.py", title="Palavras", icon="🔤"),
        # ],
        # "Sobre o projeto": [
        #     st.Page("paginas/sobre.py", title="Dados e método", icon="ℹ️"),
        # ],
    }
)

st.sidebar.caption(
    f'''Fontes:'''
)

st.sidebar.caption(
    f''' 
    · API Prefeitura da Cidade do Recife  
    · Fiocruz (Webscraping)  
    · Origem dos dados populacionais: {st.session_state.fonte_dados_populacao.upper()}'''
)

pagina.run()