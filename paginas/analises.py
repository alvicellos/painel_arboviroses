import streamlit as st
from src.carga_preparacao import agregacao_bairros, criar_analise, mostrar_preenchimento

st.header("As análises 🔎")

# Retirando bairros que sobraram com None
st.session_state.dados_tratados = st.session_state.dados_tratados.dropna(subset='NM_BAIRRO')


df_bairros_todos, df_bairros_hosp, df_bairro_ano = agregacao_bairros(st.session_state.dados_tratados)  # casos carregados são apenas os confirmados

df_analise = criar_analise(df_bairro_ano, st.session_state.dados_populacao)
df_analise


# Visões e perguntas para a IA

# Agrgar por bairros (série completa)
# Ano a ano
# Agreando por ano tem o total da cidade
# Por periodo
# Tops e comparação por cada métrica

# Em que ano houve a maior quantidade de casos registrados ? (geral)
#                                         hospitalizações  ?
#                                         de incidência    ?
#                                         de óbitos        ? Ainda não temos o percentual

# Qual bairro teve a maior quantidade de casos registrados ? Em que ano ?
#                                         hospitalizações  ?
#                                         de incidência    ?
#                                         de óbitos        ? Ainda não temos o percentual

# Os três bairros com maior índice de hospitalizações (na série)
#                                         entre 2017 e 2020
# Como esses três bairros aparecem na métrica indidência ?

# Comparar a incidência com % de hospitalizações

#