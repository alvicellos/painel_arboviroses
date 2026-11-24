import streamlit as st
import pandas as pd
from src.carga_preparacao import (carregar_dados_populacao, 
                                carregar_dados_fonte, 
                                excluir_por_valor, 
                                excluir_varios_valores, 
                                agregacao_bairros, 
                                criar_analise)
from src.tratamento_final import gerar_dados_analise

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
    if st.session_state.get("dados_tratados") is None:
        (
            df_limpo_classi,
            dados_exclusao_anos,
            n_linhas_excluidas_classi,
            n_vazias_excluidas_classi,
        ) = gerar_dados_analise(
            st.session_state.dados_api,
            anos_exclusao,
        )

        #gerar_dados_analise()

        st.session_state.dados_tratados_restante_bairros = df_limpo_classi
        st.session_state.dados_tratados = df_limpo_classi.dropna(subset='NM_BAIRRO')
        st.session_state.dados_exclusao_anos = dados_exclusao_anos
        st.session_state.n_linhas_excluidas_classi = n_linhas_excluidas_classi
        st.session_state.n_vazias_excluidas_classi = n_vazias_excluidas_classi

        # dados_agregar = st.session_state.dados_tratados
        
        # (   
        #     df_bairros_todos, 
        #     df_bairros_hosp, 
        #     df_bairro_ano
        # ) = (
        #     agregacao_bairros(
        #     dados_agregar)
        # )

        # df_analise = criar_analise(
        #     df_bairro_ano,
        #     st.session_state.dados_populacao.copy(),
        # )

        # st.session_state.df_bairros_todos = df_bairros_todos
        # st.session_state.df_bairros_hosp = df_bairros_hosp
        # st.session_state.df_bairro_ano = df_bairro_ano
        # st.session_state.df_analise = df_analise

    if st.session_state.get("df_analise") is None:
    
        dados_agregar = st.session_state.dados_tratados

        (   
            df_bairros_todos, 
            df_bairros_hosp, 
            df_bairro_ano
        ) = (
            agregacao_bairros(
            dados_agregar)
        )

        df_analise = criar_analise(
            df_bairro_ano,
            st.session_state.dados_populacao.copy(),
        )

        st.session_state.df_bairros_todos = df_bairros_todos
        st.session_state.df_bairros_hosp = df_bairros_hosp
        st.session_state.df_bairro_ano = df_bairro_ano
        st.session_state.df_analise = df_analise