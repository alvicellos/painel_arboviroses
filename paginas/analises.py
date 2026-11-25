import streamlit as st
#from comum import inicializar_estado
#from src.carga_preparacao import agregacao_bairros, criar_analise, mostrar_preenchimento
#import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from math import isfinite

st.set_page_config(layout="wide")

st.header("🔎 As análises")

df_analise = st.session_state.df_analise
#df_analise

# ============================================================
# CONFIGURAÇÕES
# ============================================================

#st.title("Análise de Chikungunya")
#st.caption("Indicadores epidemiológicos por bairro do Recife")

METRICAS = {
    "Casos confirmados": "TOTAL_CASOS",
    "Hospitalizações": "TOTAL_HOSPITALIZACOES",
    "Óbitos": "TOTAL_OBITOS",
    "Incidência / 100 mil": "INCIDENCIA_100K",
    "Casos hospitalizados (%)": "PERC_CASOS_HOSP",
    "Letalidade (%)": "LETALIDADE",
    "Mortalidade / 100 mil": "MORTALIDADE_100K",
}

ANOS = sorted(df_analise["NU_ANO"].unique().tolist())
BAIRROS = sorted(df_analise["NM_BAIRRO"].dropna().unique().tolist())

if "filtros_evolucao" not in st.session_state:
    st.session_state.filtros_evolucao = {
        "bairros": []
    }

if "filtros_ranking" not in st.session_state:
    st.session_state.filtros_ranking = {
        "metrica": "Casos confirmados",
        "metrica_secundaria": "Nenhuma",
        "periodo": (int(min(ANOS)), int(max(ANOS))),
        "qtd_bairros": 10
    }

# ============================================================
# INTERFACE ASSISTENTE
# ============================================================

# with st.expander("Assistente de análise"):
#     with st.form("assistente_analises_pergunta"):
#         pergunta = st.text_input(
#             "O que você quer explorar?",
#             max_chars=1000,
#             placeholder="Como vejo os cinco bairros com maior incidência?",
#         )
#         gerar = st.form_submit_button("Gerar orientação")

#     if gerar:
#         st.session_state.pop("assistente_analises_plano", None)

#         if not pergunta.strip():
#             st.info("Digite uma pergunta para gerar uma orientação.")
#         else:
#             contexto = {
#                 "metricas": list(METRICAS),
#                 "anos": [int(ano) for ano in ANOS],
#                 "bairros": BAIRROS,
#             }

#             try:
#                 with st.spinner("Gerando orientação com o modelo local..."):
#                     resposta = requests.post(
#                         "http://127.0.0.1:8000/assistente-analises/orientar",
#                         json={"pergunta": pergunta, "contexto": contexto},
#                         timeout=(3, 90),
#                     )
#                 dados = resposta.json()

#                 if resposta.ok:
#                     st.session_state.assistente_analises_plano = dados
#                 else:
#                     detalhe = dados.get("detail")
#                     mensagem = (
#                         detalhe.get("mensagem")
#                         if isinstance(detalhe, dict)
#                         else None
#                     )
#                     if resposta.status_code == 404:
#                         st.warning("A rota de orientação não está disponível. Confira a API local.")
#                     else:
#                         st.warning(
#                             mensagem
#                             or f"Não foi possível gerar a orientação (HTTP {resposta.status_code})."
#                         )
#             except requests.exceptions.Timeout:
#                 st.warning("A orientação demorou mais que o esperado. Tente novamente.")
#             except requests.exceptions.ConnectionError:
#                 st.warning("Verifique se a API local do painel está em execução.")
#             except (requests.exceptions.RequestException, ValueError):
#                 st.warning("Não foi possível ler a resposta da API local.")

#     plano = st.session_state.get("assistente_analises_plano")
#     if plano:
#         if plano["secao"] == "esclarecer":
#             st.text(plano["esclarecimento"])
#         elif plano["secao"] == "evolucao":
#             bairros = plano["bairros"]
#             if bairros:
#                 st.write(f"Em **Evolução anual**, selecione {', '.join(bairros)}.")
#             else:
#                 st.write("Em **Evolução anual**, limpe a seleção para ver todos os bairros.")
#         else:
#             st.write("Na barra lateral, abra **Filtros (comparação de indicadores)**.")

#             if plano["metrica"] is not None:
#                 st.write(f"**Métrica do ranking** — {plano['metrica']}")

#             if plano["periodo"] is not None:
#                 inicio, fim = plano["periodo"]
#                 st.write(f"**Período do ranking** — {inicio} a {fim}")

#             if plano["qtd_bairros"] is not None:
#                 st.write(f"**Quantidade de bairros a exibir** — {plano['qtd_bairros']}")

#             st.write("Clique em **Aplicar filtros** para atualizar o ranking e o mapa de calor.")

# ============================================================
# GRÁFICO DE LINHAS — EVOLUÇÃO ANUAL
# ============================================================

st.subheader("Evolução anual")
"Exibição da série histórica"

st.space()

# Espaço reservado para o gráfico
espaco_grafico = st.empty()

# Filtro dos bairros

with st.expander("Selecione bairros para filtrar a exibição dos dados de evolução anual. Se não houver seleção, todos os bairros serão exibidos."):
    bairros_selecionados = st.multiselect(
        "Selecione os bairros",
        options=BAIRROS,
        default=st.session_state.filtros_evolucao["bairros"],
        placeholder="Todos os bairros",
        key="evolucao_bairros"
    )

st.session_state.filtros_evolucao["bairros"] = bairros_selecionados.copy()

# Se nenhum bairro for selecionado, considerar todos
if not bairros_selecionados:
    bairros_selecionados = BAIRROS.copy()

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

    title=dict(
        text=(
            "Casos confirmados X Percentual de casos hospitalizados<br>"
            f"({df_evolucao['NU_ANO'].min()} a "
            f"{df_evolucao['NU_ANO'].max()})"
        ),
        x=0.5,
        xanchor="center",
        y=0.98,
        yanchor="top",
        font=dict(size=16)
    ),


    height=480,
    hovermode="x unified",
    margin=dict(l=20, r=20, t=65, b=90),

    legend=dict(
        orientation="h",
        y=-0.17,
        yanchor="top",
        x=0.5,
        xanchor="center",
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

espaco_grafico.plotly_chart(
    fig_linhas,
    use_container_width=True,
)

if len(bairros_selecionados) == len(BAIRROS):
    st.caption(f"O gráfico está exibindo dados de todos os bairros.")
else:
    bairro = "do bairro" if len(bairros_selecionados) == 1 else "dos bairros"
    st.caption(
        f"O gráfico está exibindo dados {bairro}: {', '.join(bairros_selecionados[:-1])} e {bairros_selecionados[-1]}."
    )

def numero_para_json(valor):
    numero = float(valor)
    return numero if isfinite(numero) else None


def exibir_resumo(grafico, chave_resposta, rotulo):
    tem_dados = bool(grafico.get("pontos") or grafico.get("bairros") or grafico.get("indicadores"))
    if not tem_dados:
        st.info("Este gráfico está vazio para o recorte atual.")

    if st.button(rotulo, key=f"{chave_resposta}_botao", disabled=not tem_dados):
        try:
            with st.spinner("Consultando o modelo local..."):
                resposta = requests.post(
                    "http://127.0.0.1:8000/assistente-analises/analisar-grafico",
                    json={"grafico": grafico},
                    timeout=(3, 120),
                )

            if resposta.ok:
                st.session_state[chave_resposta] = {
                    "grafico": grafico,
                    "texto": resposta.json()["analise"],
                }
            elif resposta.status_code == 404:
                st.warning("A rota de análise está ausente. Confira a API local.")
            elif resposta.status_code == 422:
                st.warning("A API rejeitou os dados do gráfico.")
            else:
                detalhe = resposta.json().get("detail")
                mensagem = (
                    detalhe.get("mensagem") if isinstance(detalhe, dict) else None
                )
                st.warning(
                    mensagem or f"Falha ao resumir o gráfico (HTTP {resposta.status_code})."
                )
        except requests.exceptions.Timeout:
            st.warning("O modelo demorou mais que o esperado.")
        except requests.exceptions.ConnectionError:
            st.warning("Verifique se a API local está em execução.")
        except (requests.exceptions.RequestException, ValueError, KeyError):
            st.warning("Não foi possível ler a resposta da API local.")

    resposta_salva = st.session_state.get(chave_resposta)
    if resposta_salva:
        if resposta_salva["grafico"] != grafico:
            st.caption("Última análise gerada para o recorte anterior.")
        st.write(resposta_salva["texto"])


# ============================================================
# 7. RANKING DOS BAIRROS — FILTROS INDEPENDENTES
# ============================================================

st.divider()

st.subheader("🏘️ Ranking dos bairros")

'''➡️ Utilize o filtro disponível na barra lateral e selecione as métricas que deseja comparar.'''
'''➡️ O primeiro gráfico exibe um ranking dos bairros com os maiores números para a métrica escolhida (gráfico de barras). Ao selecionar a métrica comparativa, essa será exibida como gráfico de linha sobre o gráfico de barras.

➡️ O segundo gráfico é um mapa de calor. Ele mostra uma comparação das posições dos bairros selecionados no primeiro gráfico para cada indicador epidemiológico.'''


#metricas_ranking = ["Casos confirmados", "Incidência / 100 mil", "Hospitalizações"]
#ranking_secundaria = ["Óbitos", "Incidência / 100 mil", "Casos hospitalizados (%)", "Letalidade (%)"]

filtros = st.session_state.filtros_ranking

with st.sidebar:

    st.divider()
    st.subheader("Filtros (comparação de indicadores)")

    with st.form("Filtros"):

        metrica_ranking = st.selectbox(
            "Métrica do ranking",
            options=list(METRICAS.keys()),
            index=list(METRICAS.keys()).index(filtros["metrica"]),
            key="ranking_metrica"
        )

        opcoes_secundarias = ["Nenhuma"] + [
            metrica for metrica in METRICAS
            if metrica != metrica_ranking
        ]

        metrica_secundaria = st.selectbox(
            "Métrica comparativa",
            options=opcoes_secundarias,
            index=(
                opcoes_secundarias.index(filtros["metrica_secundaria"])
                if filtros["metrica_secundaria"] in opcoes_secundarias
                else 0
            ),
            key="ranking_metrica_secundaria"
        )

        ano_inicio, ano_fim = st.slider(
            "Período do ranking",
            min_value=int(min(ANOS)),
            max_value=int(max(ANOS)),
            value=filtros["periodo"],
            step=1,
            key="ranking_periodo_slider"
        )

        qtd_bairros = st.slider(
            "Quantidade de bairros a exibir",
            min_value=1,
            max_value=20,
            value=filtros["qtd_bairros"],
            step=1,
            key="ranking_qtd_bairros"
        )

        aplicar = st.form_submit_button(
            "Aplicar filtros",
            type="primary"
        )

    st.caption(
        "Os filtros se aplicam ao ranking e ao mapa de calor."
    )

if aplicar:
    st.session_state.filtros_ranking = {
        "metrica": metrica_ranking,
        "metrica_secundaria": metrica_secundaria,
        "periodo": (ano_inicio, ano_fim),
        "qtd_bairros": qtd_bairros
    }

filtros = st.session_state.filtros_ranking
metrica_ranking = filtros["metrica"]
metrica_secundaria = filtros["metrica_secundaria"]
ano_inicio, ano_fim = filtros["periodo"]
qtd_bairros = filtros["qtd_bairros"]

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

df_ranking_completo = df_ranking.copy()

df_ranking = (
    df_ranking
    .dropna(subset=[coluna_metrica])
    .sort_values(coluna_metrica, ascending=False)
    .head(qtd_bairros)
)

###############################################

metrica_comparativa = (
    None if metrica_secundaria == "Nenhuma" else metrica_secundaria
)
coluna_comparativa = (
    METRICAS[metrica_comparativa] if metrica_comparativa else None
)

bairros_do_grafico = []
for registro in df_ranking.to_dict("records"):
    comparativa = (
        float(registro[coluna_comparativa]) if coluna_comparativa else None
    )
    if comparativa is not None and not isfinite(comparativa):
        comparativa = None

    bairros_do_grafico.append({
        "bairro": registro["NM_BAIRRO"],
        "principal": float(registro[coluna_metrica]),
        "comparativa": comparativa,
    })

resumo_ranking = {
    "metrica": metrica_ranking,
    "metrica_comparativa": metrica_comparativa,
    "periodo": [int(ano_inicio), int(ano_fim)],
    "bairros": bairros_do_grafico,
}

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

# Inclusão da métrica comparativa
if metrica_secundaria != "Nenhuma":

    coluna_secundaria = METRICAS[metrica_secundaria]

    fig_barras.add_trace(
        go.Scatter(
            x=df_ranking["NM_BAIRRO"],
            y=df_ranking[coluna_secundaria],
            name=metrica_secundaria,
            mode="lines+markers",
            line=dict(
                color="#D98B3B",
                width=3
            ),
            marker=dict(size=8),
            yaxis="y2",
            connectgaps=False
        )
    )

    fig_barras.update_layout(
        yaxis2=dict(
            title=metrica_secundaria,
            overlaying="y",
            side="right",
            rangemode="tozero",
            showgrid=False,
            tickfont=dict(color="#D98B3B")
        )
    )


titulo_metricas = (
    metrica_ranking
    if metrica_secundaria == "Nenhuma"
    else f"{metrica_ranking} X {metrica_secundaria}<br>"
)

fig_barras.update_layout(
    title=dict(
    text=(
        f"{titulo_metricas}" 
        f"({ano_inicio} a {ano_fim})<br>"
    ),
    x=0.5,
    xanchor="center",
    font=dict(size=16)
    ),
        
    height=500,
    showlegend=metrica_secundaria != "Nenhuma",
    margin=dict(l=20, r=30, t=40, b=80),
    #margin=dict(l=20, r=30, t=110, b=80),
    xaxis_tickangle=-45,

    yaxis=dict(
        title=metrica_ranking,
        rangemode="tozero"
    ),

    legend=dict(
        orientation="h",
        y=1.12,
        x=0
    )
)

fig_barras.update_xaxes(
    categoryorder="array",
    categoryarray=df_ranking["NM_BAIRRO"].tolist()
)


with st.container(border=True):

    st.plotly_chart(
        fig_barras,
        use_container_width=True,
    )

with st.expander("Assistente do ranking de bairros"):
    exibir_resumo(
        {"tipo": "ranking", **resumo_ranking},
        "assistente_resumo_ranking",
        "Resumir ranking de bairros",
    )


# ============================================================
# MAPA DE CALOR — COMPARAÇÃO ENTRE MÉTRICAS
# ============================================================

# Colunas das métricas
colunas_metricas = list(METRICAS.values())

# Bairros exibidos no gráfico de ranking
bairros_ranking = df_ranking["NM_BAIRRO"].tolist()

# DataFrame completo indexado por bairro
df_heatmap = df_ranking_completo.set_index("NM_BAIRRO")

# Cálculo das posições no ranking geral
df_posicoes = df_heatmap[colunas_metricas].rank(
    ascending=False,
    method="min"
)

# Seleção dos mesmos bairros do gráfico de barras
df_posicoes = df_posicoes.loc[bairros_ranking]

# Valores reais das métricas para exibição no hover
df_valores = df_heatmap.loc[
    bairros_ranking, colunas_metricas
]

# Criação do mapa de calor
fig_heatmap = go.Figure(
    data=go.Heatmap(
        z=df_posicoes.to_numpy(),
        x=list(METRICAS.keys()),
        y=bairros_ranking,

        text=df_posicoes.to_numpy(),
        texttemplate="%{text:.0f}º",

        customdata=df_valores.to_numpy(),

        colorscale="Blues_r",
        zmin=1,
        zmax=len(df_ranking_completo),

        xgap=2,
        ygap=2,

        colorbar=dict(
            title="Posição",
            #autorange="reversed"
        ),

        hovertemplate=(
            "<b>%{y}</b><br>"
            "Indicador: %{x}<br>"
            "Valor: %{customdata:.2f}<br>"
            "Posição no ranking: %{z:.0f}º"
            "<extra></extra>"
        )
    )
)

# Configuração visual
fig_heatmap.update_layout(
    title=dict(
        text=f"Comparação dos indicadores ({ano_inicio} a {ano_fim})",
        x=0.5,
        xanchor="center",
        font=dict(size=16)
    ),

    height=max(350, 180 + len(bairros_ranking) * 32),

    margin=dict(l=20, r=20, t=70, b=100),

    xaxis=dict(
        title=None,
        tickangle=-35
    ),

    yaxis=dict(
        title=None,
        autorange="reversed"
    )
)

with st.container(border=True):
    st.plotly_chart(
        fig_heatmap,
        use_container_width=True
    )

with st.expander("Assistente do mapa de calor"):
    if bairros_ranking:
        bairro_mapa = st.selectbox(
            "Bairro para analisar",
            bairros_ranking,
            key="assistente_bairro_mapa",
        )
        indicadores = []
        for indicador, coluna in METRICAS.items():
            posicao = numero_para_json(df_posicoes.loc[bairro_mapa, coluna])
            indicadores.append({
                "indicador": indicador,
                "posicao": int(posicao) if posicao is not None else None,
            })

        resumo_mapa = {
            "tipo": "mapa_calor",
            "periodo": resumo_ranking["periodo"],
            "bairro": bairro_mapa,
            "indicadores": indicadores,
        }
        exibir_resumo(resumo_mapa, "assistente_resumo_mapa", "Resumir posições do bairro")
    else:
        exibir_resumo(
            {"tipo": "mapa_calor", "indicadores": []},
            "assistente_resumo_mapa",
            "Resumir posições do bairro",
        )
