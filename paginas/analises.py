import streamlit as st
#from comum import inicializar_estado
#from src.carga_preparacao import agregacao_bairros, criar_analise, mostrar_preenchimento
#import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.agente_analises import ConsultaInvalida, opcoes_metrica, responder_analises
from src.modelo_groq import ErroGroq
from src.metricas_analises import METRICAS, agregar_evolucao, agregar_ranking, selecionar_ranking

st.set_page_config(layout="wide")

st.header("🔎 As análises")

st.markdown(
    "Os registros de chikungunya da Prefeitura do Recife foram tratados, "
    "agrupados por bairro e ano e cruzados com a população do Censo 2022. "
    "Dessa base saem o ranking, o mapa de calor e a evolução anual."
)
st.markdown(
    "Abra o **Assistente de análise**, escreva uma pergunta sobre os dados e clique "
    "em **Consultar dados**. Ele interpreta os resultados e sugere filtros para "
    "conferir a resposta nos gráficos."
)

df_analise = st.session_state.df_analise
#df_analise

# ============================================================
# CONFIGURAÇÕES
# ============================================================

#st.title("Análise de Chikungunya")
#st.caption("Indicadores epidemiológicos por bairro do Recife")

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

filtros_ranking = st.session_state.filtros_ranking
if filtros_ranking["metrica"] not in METRICAS:
    filtros_ranking["metrica"] = "Casos confirmados"
    st.session_state.pop("ranking_metrica", None)
if (
    filtros_ranking["metrica_secundaria"] not in ("Nenhuma", *METRICAS)
    or filtros_ranking["metrica_secundaria"] == filtros_ranking["metrica"]
):
    filtros_ranking["metrica_secundaria"] = "Nenhuma"
    st.session_state.pop("ranking_metrica_secundaria", None)

# ============================================================
# INTERFACE ASSISTENTE
# ============================================================

with st.expander("Assistente de análise"):
    with st.form("pergunta_agente_analises"):
        pergunta = st.text_input("O que você quer investigar nos dados?", max_chars=500).strip()
        enviar = st.form_submit_button("Consultar dados")

    metrica_confirmada = None
    consultar = False
    chave_esclarecimento = "pergunta_aguardando_metrica"
    if enviar:
        if not pergunta:
            st.info("Digite uma pergunta sobre os dados.")
        else:
            opcoes = opcoes_metrica(pergunta)
            if opcoes:
                st.session_state[chave_esclarecimento] = pergunta
            else:
                st.session_state.pop(chave_esclarecimento, None)
                consultar = True

    pergunta_pendente = st.session_state.get(chave_esclarecimento)
    if pergunta_pendente:
        st.caption(pergunta_pendente)
        with st.form("esclarecer_metrica_analises"):
            metrica_confirmada = st.radio(
                "Qual métrica você quer usar?",
                opcoes_metrica(pergunta_pendente),
                index=None,
            )
            confirmar = st.form_submit_button("Consultar com esta métrica")
        if confirmar:
            if metrica_confirmada is None:
                st.info("Selecione uma das métricas para continuar.")
            else:
                pergunta = pergunta_pendente
                consultar = True

    falha_consulta = False
    if consultar:
        try:
            with st.spinner("Consultando os dados e preparando a resposta..."):
                resposta = responder_analises(
                    pergunta, df_analise, st.session_state.filtros_ranking,
                    st.session_state.filtros_evolucao["bairros"],
                    metrica_confirmada=metrica_confirmada,
                )
            st.session_state.resposta_agente_analises_com_evidencias = (pergunta, resposta)
            st.session_state.pop(chave_esclarecimento, None)
            if metrica_confirmada:
                st.rerun()
        except (ConsultaInvalida, ErroGroq) as exc:
            falha_consulta = True
            st.warning(str(exc))
        except (RuntimeError, OSError, ValueError):
            falha_consulta = True
            st.warning("Não foi possível gerar a resposta com a Groq.")

    ultima_resposta = st.session_state.get("resposta_agente_analises_com_evidencias")
    if ultima_resposta and not st.session_state.get(chave_esclarecimento):
        pergunta_respondida, (texto, sugestoes, resultados, *avisos) = ultima_resposta
        st.caption(f"Consulta anterior — {pergunta_respondida}" if falha_consulta else pergunta_respondida)
        st.write(texto)
        for resultado in resultados:
            st.markdown(f"**{resultado['grafico']}**")
            if resultado["grafico"] == "Ranking de bairros":
                recorte = resultado["filtros"]
                st.caption(f"Período de {recorte['inicio']} a {recorte['fim']}")
                dados_consultados = resultado["bairros_exibidos"]
            else:
                bairros_consultados = resultado["bairros"]
                st.caption(
                    bairros_consultados
                    if isinstance(bairros_consultados, str)
                    else ", ".join(bairros_consultados)
                )
                dados_consultados = resultado["serie_anual"]

            if dados_consultados:
                st.dataframe(dados_consultados, hide_index=True)
            else:
                st.info("A consulta não retornou dados para este recorte.")

        if sugestoes:
            st.markdown("**Como conferir nos gráficos**")
            for sugestao in sugestoes:
                st.markdown(sugestao)

        if not falha_consulta and avisos and avisos[0]:
            st.warning(avisos[0])

# ============================================================
# 7. RANKING DOS BAIRROS — FILTROS INDEPENDENTES
# ============================================================

st.divider()


st.subheader("🏘️ Ranking dos bairros")
with st.expander("Sobre os gráficos"):
    '''➡️ Utilize o filtro disponível na barra lateral e selecione as métricas que deseja comparar.  
    ➡️ O primeiro gráfico exibe um ranking dos bairros com os maiores números para a métrica escolhida (gráfico de barras). Ao selecionar a métrica comparativa, essa será exibida como gráfico de linha sobre o gráfico de barras.  
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

        opcoes_secundarias = ["Nenhuma", *METRICAS]

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

if aplicar and metrica_secundaria == metrica_ranking:
    st.sidebar.warning("Escolha métricas diferentes para o ranking e a comparação.")
elif aplicar:
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

df_ranking_completo = agregar_ranking(df_analise, ano_inicio, ano_fim)
df_ranking = selecionar_ranking(df_ranking_completo, metrica_ranking, qtd_bairros)

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

st.divider()

# ============================================================
# GRÁFICO DE LINHAS — EVOLUÇÃO ANUAL
# ============================================================

st.subheader("📅 Evolução anual")
"Panorama histórico da cidade. Você pode filtrar os dados para exibir apenas os dados correspondentes aos bairros selecionados."

# Filtro dos bairros

with st.expander("Seleção de bairros"):
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

df_evolucao = agregar_evolucao(df_analise, bairros_selecionados)

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
    margin=dict(l=20, r=20, t=105, b=45),

    legend=dict(
        orientation="h",
        y=1.02,
        yanchor="bottom",
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

st.plotly_chart(
    fig_linhas,
    use_container_width=True,
)

if len(bairros_selecionados) == len(BAIRROS):
    st.caption("O gráfico está exibindo dados de todos os bairros.")
else:
    bairro = "do bairro" if len(bairros_selecionados) == 1 else "dos bairros"
    nomes = " e ".join(filter(None, (", ".join(bairros_selecionados[:-1]), bairros_selecionados[-1])))
    st.caption(f"O gráfico está exibindo dados {bairro}: {nomes}.")

