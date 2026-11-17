import streamlit as st
from src.carga_preparacao import carregar_dados_fonte, carregar_dados_populacao
from comum import inicializar_estado

inicializar_estado()

pagina = st.navigation(
    {
        "Painel": [
            st.Page("paginas/inicio.py", title="Início - o que temos aqui ? 👀", icon="🏠", default=True),
            # st.Page("paginas/bairro.py", title="Por bairro", icon="📊"),
            # st.Page("paginas/usuario.py", title="Análises usuário", icon="📊"),
            #st.Page("paginas/noticias.py", title="Notícias", icon="⭐"),
            st.Page("paginas/dados.py", title="E esses dados ?", icon="🎲"),
            st.Page("paginas/analises.py", title="Análises", icon="🎯"),
            st.Page("paginas/arquivo_usuario.py", title="E mais interação", icon="📰"),
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

# O que o roteador desenha aparece em TODA página — aqui, só um rodapé na barra lateral.
st.sidebar.caption(
    f"Sobre, etc  \n\nFontes: Exemplo (API) · Outra Fonte/EBC (WebScraping) · Outro exemplo/Instituição (Selenium)"
    f"\n\nFonte dos dados de população: ({st.session_state.fonte_dados_populacao.upper()})"
)

pagina.run()

# oi