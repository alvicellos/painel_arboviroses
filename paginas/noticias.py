import streamlit as st
from src.carga_preparacao import carregar_noticias
from src.news_utils import contar_palavras_news
import matplotlib.pyplot as plt

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

st.title("Últimas notícias relacionadas 📰")
st.divider()       


# ----------------------------------------------------------------  # Carregamento das notícias
df_news = carregar_noticias()                    

# ----------------------------------------------------------------  # Exibição da tabela de notícias
'''### Tabela notícias:'''                                          # Subtítulo

st.html("<p>")

# ----------------------------------------------------------------  # Exibe o DataFrame
df_news                                          

# ----------------------------------------------------------------  # Observação
'''**Fazer aqui um botão de download**'''        

# ----------------------------------------------------------------  # Título Resumo das Notícias
st.divider()
'''### Conteúdo das notícias:'''      

# ----------------------------------------------------------------- # Monta string markdown para exibição das notícias
mark = ""
for index, row in df_news.iterrows():           
    mark += f"""##### {row['titulo']}  
*Link: [{row['link'].split("/")[-1]}]({row['link']})*  
**Trecho da matéria:** {row["texto_materia"][:250]}...
"""

# ----------------------------------------------------------------- # Exibição das notícias
mark                                 
st.divider()

# ----------------------------------------------------------------- # Subtítulo Ocorrência de palavras nas notícias:
st.header("Ocorrência de palavras nas notícias:")   

# ----------------------------------------------------------------- # Slider para escolha da quantidade de palavras a exibir
palavras = st.slider("Selecione a quantas palavras mais presentes nas notícias deseja exibir:", 5, 45)  # 

# ----------------------------------------------------------------- # Instanciação do DataFrame de palavras
palavras, contagem, df_palavras = contar_palavras_news(r'data\processed\news_texto.txt', palavras)

# ----------------------------------------------------------------- # Criação do gráfico de frequência de palavras com matplotlib
fig, ax = plt.subplots(figsize=(35, 10))
plt.bar(palavras, contagem)

# -------------- # Seção de métricas
st.subheader("Métricas")                           
contagem_chaves = 0
for index, row in df_news.iterrows():
    for palavra in palavras_chave:
        if palavra in row['texto_materia']:
            contagem_chaves += 1
            
num_palavras_chave, palavras_chave_resumos, col_palavras = st.columns(3)

with num_palavras_chave:    
    st.metric(label="Palavras chave:", value=len(palavras_chave))

with palavras_chave_resumos:    
    st.metric(label= "Frequência de palavras-chave", value=contagem_chaves)

with col_palavras:
    f'''*Palavras-chave*:  
    {", ".join(palavras_chave)}'''   

# -------------- #Exibição do gráfico
st.pyplot(fig)

# -------------- #Exibição do DataFrame de frequência de palavras
st.dataframe(df_palavras)