import streamlit as st
pagina = st.navigation(
    {
        "Painel": [
            st.Page("paginas/inicio.py", title="Início", icon="🏠", default=True),
            # st.Page("paginas/bairro.py", title="Por bairro", icon="📊"),
            # st.Page("paginas/usuario.py", title="Análises usuário", icon="📊"),
            #st.Page("paginas/noticias.py", title="Notícias", icon="⭐"),
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
)

pagina.run()