import streamlit as st
import pandas as pd
from src.carga_preparacao import carregar_dados_populacao, carregar_dados_fonte, excluir_por_valor

colunas_analise = {'HOSPITALIZ': 'quantidade hospitalizacoes' , 'EVOLUCAO': 'como paciente evoluiu', 'CLASSI_FIN': 'confirmação diagnóstico'}
anos_exclusao = [2015, 2016]

df_populacao, fonte_populacao = carregar_dados_populacao()
dados = carregar_dados_fonte() 

def inicializar_estado() -> None:
    
    # Armazenando os dados populacionais no estado da sessão
    if "dados_populacao" not in st.session_state:    
        st.session_state.dados_populacao = df_populacao
    
    # Armazenando no estado da sessão se a fonte de dados de população foi API ou cache
    if "fonte_dados_populacao" not in st.session_state:    
        st.session_state.fonte_dados_populacao = fonte_populacao
    
    # Armazenando o Dataset no estado da sessão
    if "dados_api" not in st.session_state:    
        st.session_state.dados_api = dados
        
    # Inicializado estado da sessão para os Dados tratados
    if "dados_tratados" not in st.session_state:    
            st.session_state.dados_tratados = None
        

#df_pos_exclusao, n_linhas_excluidas, n_vazias_excluidas = excluir_por_valor(dados, "NU_ANO", 2015)
#print(n_linhas_excluidas, n_vazias_excluidas)

#df_tratado = None
#for ano in anos_exclusao:    
#    df_pos_exclusao, n_linhas_excluidas, n_vazias_excluidas = excluir_por_valor(dados, "NU_ANO", ano)
    

def excluir_varios_valores(
        df: pd.DataFrame,
        coluna: str,
        valores: list,
        excluir_vazios: bool = False) -> tuple[pd.DataFrame, list[int]]:
    
    n_valores_excluidos = []
        
    for valor in valores:
        df_pos_exclusao, n_linhas_excluidas, n_vazias_excluidas = excluir_por_valor(
            df, 
            coluna, 
            valor, 
            excluir_vazios=excluir_vazios)
        
        df = df_pos_exclusao
        n_valores_excluidos.append(n_linhas_excluidas)
    
    return df, n_valores_excluidos

#df_limpo, valores = excluir_varios_valores(dados, "NU_ANO", anos_exclusao)
#print(valores)