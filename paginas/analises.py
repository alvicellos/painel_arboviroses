import streamlit as st
#from comum import inicializar_estado
from src.carga_preparacao import agregacao_bairros, criar_analise, mostrar_preenchimento
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.header("As análises 🔎")

df_analise = st.session_state.df_analise
#df_analise

# ============================================================
# 1. DATAFRAMES DISPONÍVEIS NO PROJETO
# ============================================================

# Substituir pelas variáveis já existentes no projeto.
# df_analise: uma linha por bairro e ano
# df_acumulado: uma linha por bairro, considerando todo o período

df_acumulado = (
    df_analise.groupby("NM_BAIRRO")
    .agg({
        "TOTAL_CASOS": "sum",
        "TOTAL_HOSPITALIZACOES": "sum",
        "TOTAL_OBITOS": "sum",
        "POPULACAO": "first"
    })
    .reset_index()
)

df_acumulado["INCIDENCIA_100K"] = (
    df_acumulado["TOTAL_CASOS"] / df_acumulado["POPULACAO"] * 100000
).round(2)

df_acumulado["PERC_CASOS_HOSP"] = (
    df_acumulado["TOTAL_HOSPITALIZACOES"] / df_acumulado["TOTAL_CASOS"] * 100
).round(2)

# ============================================================
# 2. CONFIGURAÇÕES
# ============================================================

#st.title("Análise de Chikungunya")
#st.caption("Indicadores epidemiológicos por bairro do Recife")

METRICAS = {
    "Casos confirmados": "TOTAL_CASOS",
    "Hospitalizações": "TOTAL_HOSPITALIZACOES",
    "Óbitos": "TOTAL_OBITOS",
    "Incidência / 100 mil": "incidencia_100k",
    "Casos hospitalizados (%)": "perc_casos_hosp",
    "Letalidade (%)": "letalidade",
    "Mortalidade / 100 mil": "mortalidade_100k",
}

COLUNAS_CONTAGEM = [
    "TOTAL_CASOS",
    "TOTAL_HOSPITALIZACOES",
    "TOTAL_OBITOS",
]

ANOS = sorted(df_analise["NU_ANO"].unique().tolist())
BAIRROS = sorted(df_analise["NM_BAIRRO"].dropna().unique().tolist())

TODOS_ANOS = "Todos os anos"


# ============================================================
# 3. FUNÇÕES AUXILIARES
# ============================================================

def dados_periodo(periodo, df_anual, df_acumulado):
    """
    Retorna os dados do período selecionado.
    """
    if periodo == TODOS_ANOS:
        return df_acumulado.copy()

    return df_analise.loc[
        df_anual["NU_ANO"] == periodo
    ].copy()


def formatar_numero(valor, casas=0):
    return f"{valor:,.{casas}f}".replace(
        ",", "X"
    ).replace(".", ",").replace("X", ".")


def formatar_percentual(valor):
    return f"{formatar_numero(valor, 1)}%"


# ============================================================
# 4. FILTROS PRINCIPAIS
# ============================================================

# ''' ##### Filtros da análise:'''
# with st.form("filtro_analises"):

#     col_bairros, col_periodo = st.columns(2)

#     with col_periodo:
#         periodo = st.selectbox(
#             "Período",
#             options=[TODOS_ANOS] + ANOS,
#             key="analise_periodo",
#         )

#     with col_bairros:
               
#         bairros_selecionados = st.multiselect(
#             "Selecione os bairros",
#             options=BAIRROS,
#             key="analise_bairros",
#             default=BAIRROS
#         )


#     aplicar = st.form_submit_button(
#         "Aplicar filtros",
#         type="primary",
#         #on_click=aplicar_filtros
#     )


# # Dados correspondentes aos filtros principais
# df_periodo = dados_periodo(
#     periodo, df_analise, df_acumulado
# )

# df_filtrado = df_periodo.loc[
#     df_periodo["NM_BAIRRO"].isin(bairros_selecionados)
# ].copy()

# ============================================================
# 6. GRÁFICO DE LINHAS — EVOLUÇÃO ANUAL
# ============================================================

'''##### Evolução anual'''

st.caption(
    "Comparação entre casos confirmados e "
    "percentual de casos hospitalizados"
)

with st.form("filtro_evolucao"):

    col1, col2 = st.columns(2)
    

    with col2:
    
        modo_selecao = st.radio(
            "Abrangência da análise",
            options=["Todos os bairros", "Bairros selecionados"],
            horizontal=True,
            key="modo_evolucao"
        )

    with col1: 
        bairros_personalizados = st.multiselect(
            "Selecione os bairros",
            options=BAIRROS,
            default=[],
            key="evolucao_bairros"
        )

    aplicar = st.form_submit_button(
        "Aplicar filtros",
        type="primary"
    )

if modo_selecao == "Todos os bairros":
    bairros_selecionados = BAIRROS.copy()
else:
    bairros_selecionados = bairros_personalizados

# Exibição dos bairros selecionados
if len(bairros_selecionados) == len(BAIRROS):
    st.caption(
        f"Todos os bairros selecionados ({len(BAIRROS)})"
    )

else:
    with st.expander(
        f"Bairros selecionados ({len(bairros_selecionados)})"
    ):
        st.write(
            ", ".join(bairros_selecionados)
            or "Nenhum bairro selecionado"
        )

# Filtragem dos bairros selecionados
df_evolucao = df_analise.loc[
    df_analise["NM_BAIRRO"].isin(bairros_selecionados)
].copy()

# Agregação anual dos bairros selecionados
df_evolucao = (
    df_evolucao
    .groupby("NU_ANO", as_index=False)
    .agg(
        TOTAL_CASOS=("TOTAL_CASOS", "sum"),
        TOTAL_HOSPITALIZACOES=("TOTAL_HOSPITALIZACOES", "sum"),
    )
)

# Cálculo do percentual de casos hospitalizados
df_evolucao["perc_casos_hosp"] = (
    df_evolucao["TOTAL_HOSPITALIZACOES"]
    / df_evolucao["TOTAL_CASOS"].replace(0, float("nan"))
    * 100
)

# Criação do gráfico
fig_linhas = go.Figure()

# Primeira linha — casos confirmados
fig_linhas.add_trace(
    go.Scatter(
        x=df_evolucao["NU_ANO"],
        y=df_evolucao["TOTAL_CASOS"],
        name="Casos confirmados",
        mode="lines+markers",
        line=dict(color="#3869D4", width=3),
        yaxis="y",
        hovertemplate="%{y:,.0f} casos<extra></extra>",
    )
)

# Segunda linha — percentual de casos hospitalizados
fig_linhas.add_trace(
    go.Scatter(
        x=df_evolucao["NU_ANO"],
        y=df_evolucao["perc_casos_hosp"],
        name="Casos hospitalizados (%)",
        mode="lines+markers",
        line=dict(color="#009E91", width=3),
        yaxis="y2",
        hovertemplate="%{y:.2f}%<extra></extra>",
    )
)

# Configuração visual
fig_linhas.update_layout(
    height=420,
    hovermode="x unified",
    margin=dict(l=20, r=20, t=40, b=20),

    legend=dict(
        orientation="h",
        y=1.12,
        x=0,
    ),

    xaxis=dict(
        title="Ano",
        tickmode="linear",
        dtick=1,
    ),

    yaxis=dict(
        title="Casos confirmados",
        rangemode="tozero",
        tickfont=dict(color="#3869D4"),
    ),

    yaxis2=dict(
        title="Casos hospitalizados (%)",
        overlaying="y",
        side="right",
        rangemode="tozero",
        ticksuffix="%",
        tickfont=dict(color="#009E91"),
        showgrid=False,
    ),
)

st.plotly_chart(
    fig_linhas,
    use_container_width=True,
)

# ============================================================
# 7. RANKING DOS BAIRROS — FILTROS INDEPENDENTES
# ============================================================

st.divider()
st.subheader("Ranking dos bairros")

col_ranking_periodo, col_ranking_metrica = st.columns(2)

with col_ranking_periodo:

    ano_inicio, ano_fim = st.slider(
        "Período do ranking",
        min_value=int(min(ANOS)),
        max_value=int(max(ANOS)),
        value=(int(min(ANOS)), int(max(ANOS))),
        step=1,
        key="ranking_periodo_slider",
    )

with col_ranking_metrica:
    metrica_ranking = st.selectbox(
        "Métrica do ranking",
        options=list(METRICAS.keys()),
        key="ranking_metrica",
    )

coluna_metrica = METRICAS[metrica_ranking]

# O ranking não é afetado pelos filtros principais.
df_ranking = df_analise.loc[
    df_analise["NU_ANO"].between(ano_inicio, ano_fim)
].copy()

df_ranking = (
    df_ranking.groupby("NM_BAIRRO", as_index=False)
    .agg({
        "TOTAL_CASOS": "sum",
        "TOTAL_HOSPITALIZACOES": "sum",
        "TOTAL_OBITOS": "sum",
        "POPULACAO": "first"
    })
)

populacao = df_ranking["POPULACAO"].replace(0, float("nan"))
casos = df_ranking["TOTAL_CASOS"].replace(0, float("nan"))

df_ranking["INCIDENCIA_100K"] = (
    df_ranking["TOTAL_CASOS"] / populacao * 100000
).round(2)

df_ranking["PERC_CASOS_HOSP"] = (
    df_ranking["TOTAL_HOSPITALIZACOES"] / casos * 100
).round(2)

df_ranking["LETALIDADE"] = (
    df_ranking["TOTAL_OBITOS"] / casos * 100
).round(2)

df_ranking["MORTALIDADE_100K"] = (
    df_ranking["TOTAL_OBITOS"] / populacao * 100000
).round(2)

fig_barras = px.bar(
    df_ranking,
    x="NM_BAIRRO",
    y=coluna_metrica,
    text=coluna_metrica,
    labels={
        "NM_BAIRRO": "Bairro",
        coluna_metrica: metrica_ranking,
    },
)

fig_barras.update_traces(
    marker_color="#9EB7EB",
    textposition="outside",
)

fig_barras.update_layout(
    height=450,
    showlegend=False,
    margin=dict(l=20, r=20, t=30, b=70),
    xaxis_tickangle=-35,
    yaxis=dict(rangemode="tozero"),
)

st.caption(
    f"Ranking dos bairros — período de {ano_inicio} a {ano_fim}"
)

st.plotly_chart(
    fig_barras,
    use_container_width=True,
)


# ============================================================
# 5. CARDS DE MÉTRICAS
# ============================================================


total_casos = df_analise["TOTAL_CASOS"].sum()
total_hosp = df_analise["TOTAL_HOSPITALIZACOES"].sum()
total_obitos = df_analise["TOTAL_OBITOS"].sum()

perc_hosp = (
    total_hosp / total_casos * 100
    if total_casos > 0 else 0
)

letalidade = (
    total_obitos / total_casos * 100
    if total_casos > 0 else 0
)


# with st.container(border=True):

#     c1, c2, c3, c4, c5 = st.columns(5)

#     c1.metric(
#         "Casos confirmados",
#         formatar_numero(total_casos),
#         border=True
#     )

#     c2.metric(
#         "Hospitalizações",
#         formatar_numero(total_hosp),
#         border=True
#     )

#     c3.metric(
#         "Óbitos",
#         formatar_numero(total_obitos),
#         border=True
#     )

#     c4.metric(
#         "Casos hospitalizados",
#         formatar_percentual(perc_hosp),
#         border=True
#     )

#     c5.metric(
#         "Letalidade",
#         f"{letalidade:.3f}%",
#         #formatar_percentual(letalidade),
#         border=True
#     )


# st.divider()
