import streamlit as st
from comum import inicializar_estado
from src.carga_preparacao import agregacao_bairros, criar_analise, mostrar_preenchimento
import pandas as pd

st.set_page_config(layout="wide")

st.header("As análises 🔎")

st.session_state.df_analise
