from pathlib import Path

import pandas as pd
import streamlit as st

from src.assistente_dados import gerar_resposta
from src.consultar_dados import consultar_dados


BASE = Path(__file__).resolve().parent.parent
ARQUIVO_DADOS = BASE / "data" / "processed" / "dados_bairros_anos.csv"

df_limpo_classi = st.session_state.dados_tratados

st.header("Pergunte aos dados 💬")

st.write("Informe um bairro ou ano na pergunta.")

st.caption(
    "Exemplos: Quantos casos foram registrados nos Aflitos em 2017? "
    "Qual bairro registrou mais casos em 2020?"
)

with st.form("consulta_llm"):
    pergunta = st.text_area("Sua pergunta", max_chars=1000)
    enviar = st.form_submit_button("Perguntar")

if enviar:
    pergunta = pergunta.strip()

    if not pergunta:
        st.warning("Digite uma pergunta.")
    else:
        try:
            df = pd.read_csv(ARQUIVO_DADOS)
            dados = consultar_dados(df, pergunta)

            if dados.empty:
                st.warning("Não há dados para essa consulta.")
            else:
                #with st.expander("Dados utilizados na resposta"):
                #    st.dataframe(dados, hide_index=True)

                with st.spinner("Preparando a resposta..."):
                    resposta = gerar_resposta(pergunta, dados)

                    st.session_state.ultima_resposta_llm = {
                        "pergunta": pergunta,
                        "resposta": resposta,
                        "dados": dados,
                    }

                st.subheader("Resposta")
                st.write(resposta)

                st.caption(
                    "Modelo: Qwen3-0.6B. "
                    "Confira os valores na tabela: o modelo pode cometer erros."
                )

        except (ValueError, OSError, RuntimeError) as erro:
            st.error(f"Não foi possível responder: {erro}")


if "ultima_resposta_llm" in st.session_state:
    resultado = st.session_state.ultima_resposta_llm

    st.subheader("Resposta")
    st.write(f"**Pergunta:** {resultado['pergunta']}")
    st.write(resultado["resposta"])

    with st.expander("Dados utilizados na resposta"):
        st.dataframe(resultado["dados"], hide_index=True)

st.divider()

st.subheader("Confira a resposta nos dados")
st.caption(
    "Selecione os mesmos bairros e anos da pergunta. "
    "Sem seleção, todos os registros serão considerados."
)

col1, col2 = st.columns(2)

with col1:
    bairros = st.multiselect(
        "Bairros",
        options=sorted(df_limpo_classi["NM_BAIRRO"].dropna().unique()),
    )

with col2:
    anos = st.multiselect(
        "Anos",
        options=sorted(df_limpo_classi["NU_ANO"].dropna().unique()),
    )

df_conferencia = df_limpo_classi.copy()

if bairros:
    df_conferencia = df_conferencia[
        df_conferencia["NM_BAIRRO"].isin(bairros)
    ]

if anos:
    df_conferencia = df_conferencia[
        df_conferencia["NU_ANO"].isin(anos)
    ]

if df_conferencia.empty:
    st.info("Não há registros para os filtros selecionados.")
else:

    # resumo = (
    #     df_conferencia
    #     .groupby(["NM_BAIRRO", "NU_ANO"])
    #     .agg(
    #         TOTAL_CASOS=("NM_BAIRRO", "size"),
    #         TOTAL_HOSPITALIZACOES=(
    #             "HOSPITALIZ", lambda coluna: (coluna == 1).sum()
    #         ),
    #         TOTAL_OBITOS=(
    #             "EVOLUCAO", lambda coluna: (coluna == 2).sum()
    #         ),
    #     )
    #     .reset_index()
    # )

    resumo = st.session_state.df_analise.copy()

    if bairros:
        resumo = resumo[resumo["NM_BAIRRO"].isin(bairros)]

    if anos:
        resumo = resumo[resumo["NU_ANO"].isin(anos)]

    st.write("**Resumo por bairro e ano**")
    st.dataframe(resumo, hide_index=True)