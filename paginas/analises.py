import streamlit as st
#from src.carga_preparacao import agregacao_bairros, criar_analise, mostrar_preenchimento
import pandas as pd

st.header("As análises 🔎")

# Retirando bairros que sobraram com None
# st.session_state.dados_tratados = st.session_state.dados_tratados.dropna(subset='NM_BAIRRO')

df_analise = st.session_state.df_analise
df_analise