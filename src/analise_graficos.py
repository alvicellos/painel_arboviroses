import json
from itertools import combinations
from typing import Annotated, Literal

from pydantic import BaseModel, Field, FiniteFloat, ConfigDict

from src.modelo_qwen import gerar_texto


class BairroRanking(BaseModel):
    bairro: str
    principal: FiniteFloat
    comparativa: FiniteFloat | None = None


class ResumoRanking(BaseModel):
    metrica: str
    metrica_comparativa: str | None = None
    periodo: tuple[int, int]
    bairros: Annotated[list[BairroRanking], Field(min_length=1, max_length=20)]


class GraficoRanking(ResumoRanking):
    tipo: Literal["ranking"]


class PontoEvolucao(BaseModel):
    ano: int
    casos_confirmados: int
    percentual_hospitalizados: FiniteFloat | None


class GraficoEvolucao(BaseModel):
    tipo: Literal["evolucao"]
    bairros_selecionados: list[str]
    pontos: list[PontoEvolucao] = Field(min_length=1)


class CelulaMapa(BaseModel):
    indicador: str
    posicao: Annotated[int, Field(ge=1)] | None


class GraficoMapa(BaseModel):
    tipo: Literal["mapa_calor"]
    periodo: tuple[int, int]
    bairro: str
    indicadores: list[CelulaMapa] = Field(min_length=1)


class PedidoResumoGrafico(BaseModel):
    grafico: Annotated[
        GraficoRanking | GraficoEvolucao | GraficoMapa,
        Field(discriminator="tipo"),
    ]


def variacoes_evolucao(grafico: GraficoEvolucao) -> list[dict]:
    pontos = sorted(grafico.pontos, key=lambda ponto: ponto.ano)
    variacoes = []

    for anterior, atual in zip(pontos, pontos[1:]):
        if atual.ano != anterior.ano + 1:
            continue

        diferenca = atual.casos_confirmados - anterior.casos_confirmados
        variacoes.append({
            "ano_inicial": anterior.ano,
            "ano_final": atual.ano,
            "casos_iniciais": anterior.casos_confirmados,
            "casos_finais": atual.casos_confirmados,
            "variacao_em_casos": diferenca,
        })

    return variacoes


def resumir_evolucao(grafico: GraficoEvolucao) -> dict:
    pontos = grafico.pontos
    variacoes = variacoes_evolucao(grafico)
    aumentos = [v for v in variacoes if v["variacao_em_casos"] > 0]
    quedas = [v for v in variacoes if v["variacao_em_casos"] < 0]
    percentuais = [p for p in pontos if p.percentual_hospitalizados is not None]

    return {
        "grafico": "Evolução anual",
        "periodo": [min(p.ano for p in pontos), max(p.ano for p in pontos)],
        "recorte": (
            grafico.bairros_selecionados
            if 0 < len(grafico.bairros_selecionados) <= 5
            else f"{len(grafico.bairros_selecionados)} bairros selecionados"
            if grafico.bairros_selecionados else "Todos os bairros"
        ),
        "escopo_da_conclusao": (
            "A série mostra apenas o bairro selecionado. Não há comparação entre bairros."
            if len(grafico.bairros_selecionados) == 1
            else "A série agrega os bairros do recorte e não identifica líderes por bairro."
        ),
        "pico_de_casos": max(pontos, key=lambda p: p.casos_confirmados).model_dump(),
        "pico_percentual_hospitalizados": (
            max(percentuais, key=lambda p: p.percentual_hospitalizados).model_dump()
            if percentuais else None
        ),
        "pares_de_anos_consecutivos": len(variacoes),
        "maiores_variacoes_em_casos": sorted(
            aumentos + quedas,
            key=lambda v: abs(v["variacao_em_casos"]),
            reverse=True,
        )[:3],
        "maior_aumento": max(
            aumentos, key=lambda v: v["variacao_em_casos"], default=None
        ),
        "maior_queda": min(
            quedas, key=lambda v: v["variacao_em_casos"], default=None
        ),
    }


def resumir_ranking(grafico: GraficoRanking) -> dict:
    bairros = grafico.bairros
    comparaveis = [b for b in bairros if b.comparativa is not None]
    contrastes = [
        [primeiro.model_dump(), segundo.model_dump()]
        for primeiro, segundo in combinations(comparaveis, 2)
        if primeiro.principal > segundo.principal
        and primeiro.comparativa < segundo.comparativa
    ] if grafico.metrica_comparativa else []
    maior_principal = max(b.principal for b in bairros)
    maior_comparativa = (
        max((b.comparativa for b in comparaveis), default=None)
        if grafico.metrica_comparativa else None
    )
    return {
        "grafico": "Ranking de bairros",
        "periodo": grafico.periodo,
        "metrica_principal": grafico.metrica,
        "metrica_comparativa": grafico.metrica_comparativa,
        "lideres_na_metrica_principal": {
            "valor": maior_principal,
            "bairros": [b.bairro for b in bairros if b.principal == maior_principal],
        },
        "lideres_na_metrica_comparativa": (
            {
                "valor": maior_comparativa,
                "bairros": [b.bairro for b in comparaveis if b.comparativa == maior_comparativa],
            }
            if maior_comparativa is not None else None
        ),
        "primeiros_colocados": [b.model_dump() for b in bairros[:3]],
        "diferenca_na_metrica_principal_entre_os_dois_primeiros": (
            round(bairros[0].principal - bairros[1].principal, 2)
            if len(bairros) > 1 else None
        ),
        "exemplos_de_ordem_invertida_entre_metricas": contrastes[:2],
    }


def resumir_mapa(grafico: GraficoMapa) -> dict:
    com_posicao = [celula for celula in grafico.indicadores if celula.posicao is not None]
    return {
        "grafico": "Mapa de calor",
        "bairro": grafico.bairro,
        "periodo": grafico.periodo,
        "posicoes_em_ordem_crescente": [
            celula.model_dump()
            for celula in sorted(com_posicao, key=lambda celula: celula.posicao)
        ],
        "indicadores_sem_posicao": [
            celula.indicador for celula in grafico.indicadores if celula.posicao is None
        ],
    }


def formatar_lista(itens: list[str]) -> str:
    return " e ".join(filter(None, (", ".join(itens[:-1]), itens[-1])))


def concluir_ranking(resultados: dict) -> str:
    lideres = resultados["lideres_na_metrica_principal"]["bairros"]
    metrica = resultados["metrica_principal"]
    nomes = formatar_lista(lideres)
    if len(lideres) == 1:
        conclusao = f"{nomes} merece mais atenção entre os bairros exibidos pelo indicador {metrica}."
    else:
        conclusao = (
            f"{nomes} merecem mais atenção entre os bairros exibidos "
            f"porque empatam na liderança em {metrica}."
        )

    comparativa = resultados["lideres_na_metrica_comparativa"]
    if comparativa is None:
        return conclusao

    metrica_comparativa = resultados["metrica_comparativa"]
    outros_lideres = comparativa["bairros"]
    if set(lideres) == set(outros_lideres):
        return conclusao + f" A liderança coincide em {metrica_comparativa}."

    nomes_comparativa = formatar_lista(outros_lideres)
    verbo = "lidera" if len(outros_lideres) == 1 else "empatam na liderança"
    return conclusao + f" Em {metrica_comparativa}, {nomes_comparativa} {verbo}."


def concluir_mapa(resultados: dict) -> str:
    posicoes = resultados["posicoes_em_ordem_crescente"]
    if not posicoes:
        return "O recorte não tem posições disponíveis para apontar um indicador de destaque."

    posicao_destaque = posicoes[0]["posicao"]
    indicadores = formatar_lista([
        item["indicador"] for item in posicoes if item["posicao"] == posicao_destaque
    ])
    return (
        f"Para {resultados['bairro']}, vale olhar primeiro para {indicadores}, "
        f"onde o bairro tem sua posição mais alta no ranking geral do recorte ({posicao_destaque}ª)."
    )


def formatar_posicoes_mapa(resultados: dict) -> str:
    bairro = resultados["bairro"]
    inicio, fim = resultados["periodo"]
    colocacoes = [
        f'{celula["posicao"]}ª posição em {celula["indicador"]}'
        for celula in resultados["posicoes_em_ordem_crescente"]
    ]
    if colocacoes:
        lista = formatar_lista(colocacoes)
        texto = f"De {inicio} a {fim}, o bairro {bairro} ocupa a {lista}."
    else:
        texto = f"De {inicio} a {fim}, o bairro {bairro} não tem posições disponíveis."

    sem_posicao = resultados["indicadores_sem_posicao"]
    if sem_posicao and colocacoes:
        texto += " Sem posição no recorte: " + ", ".join(sem_posicao) + "."
    return texto


def gerar_resumo_grafico(pedido: PedidoResumoGrafico) -> str:
    grafico = pedido.grafico
    if isinstance(grafico, GraficoEvolucao):
        resultados = resumir_evolucao(grafico)
    elif isinstance(grafico, GraficoRanking):
        resultados = resumir_ranking(grafico)
    else:
        resultados = resumir_mapa(grafico)

    conclusao = ""
    if isinstance(grafico, GraficoMapa):
        conclusao = concluir_mapa(resultados)
        instrucao = (
            "Reproduza exatamente a frase do campo texto_de_referencia, "
            "preservando todas as posições, os empates e a ordem apresentada."
        )
    elif isinstance(grafico, GraficoRanking):
        conclusao = concluir_ranking(resultados)
        instrucao = (
            "Descreva em português, em até duas frases, os valores do ranking. "
            "Nomeie a métrica principal e distinga a comparativa, quando disponível. "
            "Use somente os dados recebidos, preserve as unidades e evite atribuir causas. "
            "A aplicação acrescentará a conclusão sobre os bairros de destaque."
        )
    else:
        instrucao = (
            "Resuma em português, em até três frases, o que o gráfico mostra no recorte. "
            "Na conclusão, cite os bairros líderes entre os exibidos e nomeie o indicador "
            "que sustenta a conclusão. Preserve empates. Se houver métrica comparativa, "
            "diga se os líderes coincidem ou mudam. Na evolução, respeite o escopo da "
            "conclusão informado. Use somente o resumo, preserve as unidades e não faça "
            "cálculos. Não atribua causas nem apresente sugestões."
        )

    if isinstance(grafico, GraficoMapa):
        resultados["texto_de_referencia"] = formatar_posicoes_mapa(resultados)

    mensagens = [
        {
            "role": "system",
            "content": instrucao,
        },
        {
            "role": "user",
            "content": json.dumps(
                resultados,
                ensure_ascii=False,
                allow_nan=False,
            ),
        },
    ]
    texto = gerar_texto(mensagens, max_novos_tokens=160).strip()
    if isinstance(grafico, GraficoMapa):
        referencia = resultados["texto_de_referencia"]
        if texto != referencia:
            texto = referencia

    if texto and conclusao:
        return f"{texto}\n\n**Conclusão.** {conclusao}".strip()
    return texto
