import streamlit as st
pagina = st.navigation(
    {
        "Painel": [
            st.Page("paginas/inicio.py", title="Início", icon="🏠", default=True),
            st.Page("paginas/indicadores.py", title="Indicadores por UF", icon="📊"),
            #st.Page("paginas/comparador.py", title="Comparador de UFs", icon="⭐"),
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
    f"Bla bla \n\nFontes: IBGE (API) · Agência Brasil/EBC (WebScraping) · INPE/PRODES (Selenium)"
)

pagina.run()