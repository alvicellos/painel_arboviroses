import pandas as pd


METRICAS = {
    "Casos confirmados": "TOTAL_CASOS",
    "Hospitalizações": "TOTAL_HOSPITALIZACOES",
    "Óbitos": "TOTAL_OBITOS",
    "Incidência / 100 mil": "INCIDENCIA_100K",
    "Casos hospitalizados (%)": "PERC_CASOS_HOSP",
    "Letalidade (%)": "LETALIDADE",
}


def agregar_evolucao(dados: pd.DataFrame, bairros: list[str]) -> pd.DataFrame:
    recorte = dados.loc[dados["NM_BAIRRO"].isin(bairros)] if bairros else dados
    anual = recorte.groupby("NU_ANO", as_index=False).agg(
        TOTAL_CASOS=("TOTAL_CASOS", "sum"),
        TOTAL_HOSPITALIZACOES=("TOTAL_HOSPITALIZACOES", "sum"),
    )
    anual["perc_casos_hosp"] = (
        anual["TOTAL_HOSPITALIZACOES"]
        / anual["TOTAL_CASOS"].replace(0, float("nan")) * 100
    )
    return anual


def agregar_ranking(dados: pd.DataFrame, inicio: int, fim: int) -> pd.DataFrame:
    recorte = dados.loc[dados["NU_ANO"].between(inicio, fim)]
    ranking = recorte.groupby("NM_BAIRRO", as_index=False).agg(
        TOTAL_CASOS=("TOTAL_CASOS", "sum"),
        TOTAL_HOSPITALIZACOES=("TOTAL_HOSPITALIZACOES", "sum"),
        TOTAL_OBITOS=("TOTAL_OBITOS", "sum"),
        POPULACAO=("POPULACAO", "first"),
    )
    populacao = ranking["POPULACAO"].replace(0, float("nan"))
    casos = ranking["TOTAL_CASOS"].replace(0, float("nan"))
    ranking["INCIDENCIA_100K"] = (ranking["TOTAL_CASOS"] / populacao * 100000).round(2)
    ranking["PERC_CASOS_HOSP"] = (ranking["TOTAL_HOSPITALIZACOES"] / casos * 100).round(2)
    ranking["LETALIDADE"] = (ranking["TOTAL_OBITOS"] / casos * 100).round(2)
    return ranking


def selecionar_ranking(ranking: pd.DataFrame, metrica: str, quantidade: int) -> pd.DataFrame:
    coluna = METRICAS[metrica]
    return ranking.dropna(subset=[coluna]).sort_values(coluna, ascending=False).head(quantidade)
