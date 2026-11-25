import streamlit as st
from src.carga_preparacao import carregar_noticias
from src.news_utils import contar_palavras_news
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("📢 Últimas notícias")
st.divider()

# ----------------------------------------------------------------  # Carregamento das notícias
df_news = carregar_noticias()                    

# ----------------------------------------------------------------  # Exibição da tabela de notícias
'''### Notícias em forma de tabela:'''                                          # Subtítulo

st.html("<p>")

# ----------------------------------------------------------------  # Exibe o DataFrame
df_news                                          

# ----------------------------------------------------------------  # Observação
#'''**Fazer aqui um botão de download**'''        

# ----------------------------------------------------------------  # Título Resumo das Notícias
st.divider()

'''### 📰 Notícias em forma de texto:'''      

# ----------------------------------------------------------------- # Monta string markdown para exibição das notícias
mark = ""
for index, row in df_news.iterrows():           
    mark += f"""##### {row['titulo']}  
*Link: [{row['link'].split("/")[-1]}]({row['link']})*  
**Trecho da matéria:** {row["texto_materia"][:250]}...
"""

# ----------------------------------------------------------------- # Exibição das notícias
with st.expander("Manchetes, trechos e links para acesso ao conteúdo (clique para exibir)"):
    mark                                 

st.divider()

# ----------------------------------------------------------------- # Subtítulo Ocorrência de palavras nas notícias:
st.header("Palavras nas notícias:")   

# ----------------------------------------------------------------- # Slider para escolha da quantidade de palavras a exibir
#palavras = st.slider("Selecione a quantidade de palavras para exibição:", 3, 45, step=3, value=15)
f'''###### Um _tour_ pelas palavras que estão na mídia:'''


# Reserva o espaço para as métricas
container_metricas = st.container()

st.space()

palavras = st.slider(
    "Selecione a quantidade de palavras para exibição:",
    3, 45, step=3, value=15
)

# Instanciação do DataFrame de palavras
df_palavras, total_palavras, palavras_sem_repetir, total_caracteres = contar_palavras_news(
    r'data\processed\news_texto.txt', palavras
)

with container_metricas:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Total de palavras nas notícias:",
            value=str(total_palavras),
            border=True
        )
    
    with col2:
        st.metric(
            label="Palavras diferentes encontradas:",
            value=str(palavras_sem_repetir),
            border=True
        )

    with col3:
        st.metric(
            label="Total de caracteres:",
            value=str(total_caracteres),
            border=True
        )

f'''### As {palavras} palavras mais frequentes:'''
"Compare a frequência das palavras:"

# -------------- #Exibição do gráfico
st.bar_chart(
    df_palavras,
    x="palavra",
    y="ocorrencias",
    x_label="Palavras",
    y_label="Número de ocorrências",
    color="#4C78A8"
)

# -------------- #Exibição do DataFrame de frequência de palavras
with st.expander("Visualize as palavras mais frequentes em formato de tabela"):
    st.dataframe(df_palavras)
