import json
import re
import unicodedata
from typing import Annotated, Literal

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError

from src.especialista_epidemiologico import (
    formatar_achados,
    formatar_leitura,
    interpretar_resultados,
    leitura_dos_dados,
)
from src.modelo_groq import ErroGroq, gerar_texto
from src.metricas_analises import METRICAS, agregar_evolucao, agregar_ranking, selecionar_ranking


class ConsultaInvalida(ValueError):
    pass


class Ranking(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    acao: Literal["ranking"]
    metrica: str
    comparativa: str | None = None
    inicio: int | None = None
    fim: int | None = None
    quantidade: int = Field(default=10, ge=1, le=20)


class Evolucao(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    acao: Literal["evolucao"]
    bairros: list[str] | None = None


class Encerrar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    acao: Literal["responder", "esclarecer"]
    mensagem: str = Field(default="", max_length=400)


ACAO = TypeAdapter(Annotated[Ranking | Evolucao | Encerrar, Field(discriminator="acao")])
MAX_CONSULTAS = 3


def normalizar(texto: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", texto.casefold())
        if not unicodedata.combining(c)
    )


def executar_consulta(consulta, dados: pd.DataFrame, catalogo: dict, filtros: dict):
    if isinstance(consulta, Ranking):
        if consulta.metrica not in METRICAS or (
            consulta.comparativa is not None
            and (consulta.comparativa not in METRICAS or consulta.comparativa == consulta.metrica)
        ):
            raise ConsultaInvalida("Escolha métricas distintas do catálogo.")
        inicio_atual, fim_atual = filtros["periodo"]
        inicio = consulta.inicio if consulta.inicio is not None else consulta.fim
        fim = consulta.fim if consulta.fim is not None else consulta.inicio
        if inicio is None:
            inicio, fim = inicio_atual, fim_atual
        anos = catalogo["anos"]
        if inicio not in anos or fim not in anos or inicio > fim:
            raise ConsultaInvalida("Escolha um período ordenado com anos do catálogo.")

        ranking = selecionar_ranking(
            agregar_ranking(dados, inicio, fim), consulta.metrica, consulta.quantidade
        )
        metricas = [consulta.metrica]
        if consulta.comparativa:
            metricas.append(consulta.comparativa)
        valores = ranking[["NM_BAIRRO", *(METRICAS[m] for m in metricas)]]
        valores = valores.rename(columns={"NM_BAIRRO": "Bairro", **{METRICAS[m]: m for m in metricas}})
        recorte = {
            "inicio": inicio, "fim": fim, "metrica": consulta.metrica,
            "comparativa": consulta.comparativa or "Nenhuma", "quantidade": consulta.quantidade,
        }
        resultado = {
            "grafico": "Ranking de bairros", "filtros": recorte,
            "anos_com_registros_no_periodo": [ano for ano in anos if inicio <= ano <= fim],
            "bairros_exibidos": json.loads(valores.to_json(orient="records", force_ascii=False)),
            "notas": (
                "Ranking decrescente pela métrica principal e limitado à quantidade solicitada. "
                "A comparativa se refere aos mesmos bairros exibidos. "
                "A incidência usa o total de casos do período por 100 mil habitantes."
            ),
        }
        sugestao = (
            f"**Ranking de bairros.** Período {inicio} a {fim}. "
            f"Métrica do ranking **{consulta.metrica}**. "
            f"Métrica comparativa **{recorte['comparativa']}**. "
            f"Quantidade de bairros **{consulta.quantidade}**. Clique em **Aplicar filtros**. "
            "O mapa de calor acompanha esse recorte."
        )
    else:
        bairros_por_nome = {normalizar(b): b for b in catalogo["bairros"]}
        solicitados = catalogo["bairros_atuais"] if consulta.bairros is None else consulta.bairros
        bairros = []
        for nome in solicitados:
            bairro = bairros_por_nome.get(normalizar(nome.strip()))
            if bairro is None:
                raise ConsultaInvalida(f"Bairro fora do catálogo: {nome}.")
            if bairro not in bairros:
                bairros.append(bairro)
        serie = agregar_evolucao(dados, bairros).rename(columns={
            "NU_ANO": "Ano",
            "TOTAL_CASOS": "Casos confirmados",
            "TOTAL_HOSPITALIZACOES": "Hospitalizações",
            "perc_casos_hosp": "Casos hospitalizados (%)",
        })
        resultado = {
            "grafico": "Evolução anual", "bairros": bairros or "Todos os bairros",
            "serie_anual": json.loads(serie.round(2).to_json(orient="records", force_ascii=False)),
            "notas": "A série agrega os bairros selecionados e mostra todos os anos disponíveis no recorte.",
        }
        selecao = f"Selecione **{', '.join(bairros)}**." if bairros else "Limpe a seleção para ver todos os bairros."
        sugestao = f"**Evolução anual.** {selecao}"
    return resultado, sugestao


def opcoes_metrica(pergunta: str) -> tuple[str, ...]:
    texto = normalizar(pergunta)
    menciona_hospitalizacao = re.search(r"\b(?:hospitalizacao|hospitalizacoes)\b", texto)
    medida_explicitada = re.search(
        r"\b(?:percentual|porcentagem|proporcao|total|numero|quantidade)\b", texto
    ) or "%" in texto
    if menciona_hospitalizacao and not medida_explicitada and re.search(
        r"\b(?:indice|taxa|maior hospitalizacao)\b", texto
    ):
        return ("Casos hospitalizados (%)", "Hospitalizações")
    if re.search(r"\bmais afetad[oa]s?\b", texto) and not re.search(
        r"\b(?:casos|incidencia|hospitalizacao|hospitalizacoes|obitos|mortalidade|letalidade)\b",
        texto,
    ):
        return ("Incidência / 100 mil", "Casos confirmados")
    return ()


def consulta_explicita(pergunta: str, bairros: list[str], metrica_confirmada: str | None = None):
    """Recupera pedidos explícitos quando o coordenador não consegue iniciar."""
    termos = {
        "incidencia": "Incidência / 100 mil",
        "letalidade": "Letalidade (%)",
        "casos hospitalizados": "Casos hospitalizados (%)",
        "hospitalizacoes": "Hospitalizações",
        "obitos": "Óbitos",
        "casos": "Casos confirmados",
    }
    if re.search(r"\b(ranking|maiores|maior|mais afetad[oa]s?)\b", pergunta):
        encontrados = sorted(
            (match.start(), metrica)
            for termo, metrica in termos.items()
            if (match := re.search(rf"\b{termo}\b", pergunta))
            and not (termo == "casos" and "casos hospitalizados" in pergunta)
        )
        if metrica_confirmada:
            encontrados = [(-1, metrica_confirmada)]
        elif re.search(r"\b(?:percentual|porcentagem|proporcao) de hospitalizac", pergunta):
            encontrados = [(-1, "Casos hospitalizados (%)")]
        elif re.search(r"\b(?:total|numero|quantidade) de hospitalizacao\b", pergunta):
            encontrados = [(-1, "Hospitalizações")]
        if encontrados:
            numeros = {"um": 1, "dois": 2, "tres": 3, "quatro": 4, "cinco": 5, "dez": 10}
            limite = re.search(r"\b(\d+|um|dois|tres|quatro|cinco|dez)\s+bairros?\b", pergunta)
            quantidade = 10
            if limite:
                palavra = limite[1]
                quantidade = int(palavra) if palavra.isdecimal() else numeros[palavra]
            if not 1 <= quantidade <= 20:
                return None
            anos = [int(ano) for ano in re.findall(r"\b(?:19|20)\d{2}\b", pergunta)]
            if len(anos) > 2:
                return None
            return Ranking(
                acao="ranking",
                metrica=encontrados[0][1],
                comparativa=encontrados[1][1] if len(encontrados) > 1 else None,
                inicio=anos[0] if anos else None,
                fim=anos[-1] if anos else None,
                quantidade=quantidade,
            )

    if bairros and re.search(r"\b(evolucao|evoluiram|serie anual|trajetoria)\b", pergunta):
        if len(bairros) == 1:
            return Evolucao(acao="evolucao", bairros=bairros)
    return None


def resumo_dos_resultados(resultados: list[dict]) -> str:
    frases = []
    for resultado in resultados:
        if resultado["grafico"] == "Ranking de bairros":
            registros = resultado["bairros_exibidos"]
            metricas = [resultado["filtros"]["metrica"], resultado["filtros"]["comparativa"]]
            for metrica in metricas:
                validos = [r for r in registros if r.get(metrica) is not None]
                if validos:
                    maior = max(r[metrica] for r in validos)
                    lideres = ", ".join(r["Bairro"] for r in validos if r[metrica] == maior)
                    frases.append(f"Em **{metrica}**, o maior valor entre os bairros exibidos aparece em **{lideres}**.")
        elif resultado["serie_anual"]:
            serie = resultado["serie_anual"]
            pico = max(linha["Casos confirmados"] for linha in serie)
            anos_do_pico = ", ".join(str(linha["Ano"]) for linha in serie if linha["Casos confirmados"] == pico)
            frases.append(f"Na evolução anual, o maior total de casos do recorte aparece em **{anos_do_pico}**.")
    return "\n\n".join(frases) or "As consultas não retornaram valores disponíveis para interpretar."


def indice_ranking_equivalente(resultado: dict, anteriores: list[dict]) -> int | None:
    if resultado["grafico"] != "Ranking de bairros":
        return None
    campos = ("inicio", "fim", "metrica", "comparativa")
    filtros = resultado["filtros"]
    return next(
        (
            indice for indice, anterior in enumerate(anteriores)
            if anterior["grafico"] == resultado["grafico"]
            and all(anterior["filtros"][campo] == filtros[campo] for campo in campos)
        ),
        None,
    )


def responder_analises(
    pergunta: str,
    dados: pd.DataFrame,
    filtros_ranking: dict,
    bairros_atuais: list[str],
    *,
    metrica_confirmada: str | None = None,
):
    if metrica_confirmada is not None and metrica_confirmada not in opcoes_metrica(pergunta):
        raise ConsultaInvalida("Escolha uma das métricas oferecidas para a pergunta.")

    bairros = sorted(dados["NM_BAIRRO"].dropna().unique().tolist())
    pergunta_normalizada = normalizar(pergunta)
    if re.search(
        r"\b(?:mortalidade\b|obitos\s*(?:/|por)\s*100\s*(?:k|mil\b|000\b))",
        pergunta_normalizada,
    ):
        return (
            "O painel não oferece mortalidade por 100 mil habitantes. "
            "Você pode consultar o total de óbitos ou a letalidade entre os casos confirmados.",
            [], [], None,
        )
    bairros_mencionados = [nome for nome in bairros if normalizar(nome) in pergunta_normalizada]
    catalogo = {
        "anos": sorted(int(ano) for ano in dados["NU_ANO"].dropna().unique()),
        "bairros": bairros,
        "bairros_atuais": bairros_atuais,
    }
    contexto = {
        "pergunta": pergunta, "metricas": list(METRICAS), "anos": catalogo["anos"],
        "bairros_mencionados_validos": bairros_mencionados, "bairros_atuais": bairros_atuais,
        "filtros_atuais_ranking": filtros_ranking,
        "metrica_confirmada_pelo_usuario": metrica_confirmada,
    }
    instrucoes = (
        "Escolha e execute consultas sobre chikungunya no Recife. Responda com um objeto JSON. "
        "Para maiores, mais afetados e comparações no período, use ranking. "
        "Exemplo: 'Quais os 3 bairros com maior incidência em 2023? Compare com os casos': "
        '{"acao":"ranking","metrica":"Incidência / 100 mil","comparativa":"Casos confirmados",'
        '"inicio":2023,"fim":2023,"quantidade":3}. '
        "Use métricas e anos do catálogo. Para toda a série histórica, use o primeiro e o último ano do catálogo. "
        "Se o período não for mencionado, omita início e fim. "
        "Se a pergunta pedir os líderes gerais em indicadores distintos, consulte um ranking "
        "por indicador. A comparativa mostra apenas os bairros selecionados pela métrica principal. "
        "Para série, tendência ou evolução, use evolucao. Exemplo: 'Como evoluíram os casos no Ibura?': "
        '{"acao":"evolucao","bairros":["Ibura"]}. Use [] para todos os bairros. '
        "A série agrega os bairros e mostra todos os anos disponíveis. Consulte os bairros "
        "separadamente para comparar trajetórias."
    )

    resultados = []
    sugestoes = []
    consulta_confirmada = (
        consulta_explicita(pergunta_normalizada, bairros_mencionados, metrica_confirmada)
        if metrica_confirmada else None
    )
    if consulta_confirmada is None and re.fullmatch(
        r"quais (?:sao )?os (?:[0-9]+|um|dois|tres|quatro|cinco|dez) bairros com maior "
        r"[^?.,;]+ entre (?:19|20)[0-9]{2} e (?:19|20)[0-9]{2}\s*\??",
        pergunta_normalizada.strip(),
    ) and not opcoes_metrica(pergunta):
        consulta_confirmada = consulta_explicita(pergunta_normalizada, bairros_mencionados)

    if consulta_confirmada is None and re.fullmatch(
        r"qual (?:foi o )?bairro (?:apresentou|registrou|teve|com) "
        r"(?:o )?maior (?:numero|total) de casos(?: confirmados)? "
        r"(?:em|durante|ao longo de) toda a serie historica\s*\??",
        pergunta_normalizada.strip(),
    ) and catalogo["anos"]:
        consulta_confirmada = Ranking(
            acao="ranking",
            metrica="Casos confirmados",
            inicio=catalogo["anos"][0],
            fim=catalogo["anos"][-1],
            quantidade=1,
        )

    recorte_prioridade = re.fullmatch(
        r"entre os ([0-9]+) bairros com maior (?:indice|incidencia) por 100\s*(?:k|mil) "
        r"em ((?:19|20)[0-9]{2}),? quais (?:bairros )?merecem (?:maior|mais) atencao\s*\??",
        pergunta_normalizada.strip(),
    )
    if consulta_confirmada is None and recorte_prioridade:
        quantidade, ano = map(int, recorte_prioridade.groups())
        if 1 <= quantidade <= 20:
            consulta_confirmada = Ranking(
                acao="ranking",
                metrica="Incidência / 100 mil",
                comparativa="Casos confirmados",
                inicio=ano,
                fim=ano,
                quantidade=quantidade,
            )

    if isinstance(consulta_confirmada, Ranking):
        resultado, sugestao = executar_consulta(consulta_confirmada, dados, catalogo, filtros_ranking)
        resultados.append(resultado)
        sugestoes.append(sugestao)

    erro = None
    erros = 0
    for _ in range(0 if resultados else MAX_CONSULTAS + 2):
        texto = gerar_texto([
            {"role": "system", "content": instrucoes + (
                ' Se os resultados já respondem à pergunta, retorne {"acao":"responder"}. Não repita o mesmo ranking mudando apenas o limite de bairros.'
                if resultados else
                ' Execute uma consulta quando a pergunta mencionar um gráfico, indicador ou período.'
                ' Só peça esclarecimento se não puder escolher a consulta: '
                '{"acao":"esclarecer","mensagem":"Qual recorte você quer consultar?"}.'
            )},
            {"role": "user", "content": json.dumps({
                **contexto, "resultados": resultados, "erro_da_ultima_acao": erro,
            }, ensure_ascii=False)},
        ], max_novos_tokens=170, modo_json=True).strip()
        linhas = texto.splitlines()
        if len(linhas) >= 3 and linhas[0].strip().lower() in {"```json", "```"} and linhas[-1].strip() == "```":
            texto = "\n".join(linhas[1:-1])
        try:
            acao = ACAO.validate_json(texto)
            if isinstance(acao, Encerrar):
                if resultados:
                    break
                alternativa = consulta_explicita(pergunta_normalizada, bairros_mencionados)
                if alternativa is not None:
                    acao = alternativa
                elif acao.acao == "esclarecer":
                    return acao.mensagem.strip() or "Informe o bairro, o período ou o indicador desejado.", [], [], None
                else:
                    raise ConsultaInvalida("Execute uma consulta antes de responder.")
            resultado, sugestao = executar_consulta(acao, dados, catalogo, filtros_ranking)
            if resultado in resultados:
                break
            equivalente = indice_ranking_equivalente(resultado, resultados)
            if equivalente is not None:
                if resultado["filtros"]["quantidade"] > resultados[equivalente]["filtros"]["quantidade"]:
                    resultados[equivalente] = resultado
                    sugestoes[equivalente] = sugestao
                erro = None
                continue
            resultados.append(resultado)
            sugestoes.append(sugestao)
            erro = None
            if len(resultados) == MAX_CONSULTAS:
                break
        except (ValidationError, ConsultaInvalida) as exc:
            erros += 1
            erro = "Ação JSON inválida. Siga um dos exemplos." if isinstance(exc, ValidationError) else str(exc)
            if erros >= 2:
                if resultados:
                    break
                alternativa = consulta_explicita(pergunta_normalizada, bairros_mencionados)
                if alternativa is not None:
                    resultado, sugestao = executar_consulta(alternativa, dados, catalogo, filtros_ranking)
                    resultados.append(resultado)
                    sugestoes.append(sugestao)
                    break
                raise ConsultaInvalida("Não consegui montar uma consulta válida. Reformule a pergunta.") from exc

    if not resultados:
        raise ConsultaInvalida("Não consegui consultar os dados para essa pergunta.")
    aviso = None
    try:
        resposta = interpretar_resultados(pergunta, resultados, metrica_confirmada, gerar_texto)
    except ErroGroq as exc:
        resposta = "\n\n".join(filter(None, (
            formatar_achados(resultados),
            formatar_leitura(leitura_dos_dados(resultados)),
        )))
        aviso = f"{exc} O resumo acima foi calculado pelo painel."
    if not resposta:
        resposta = resumo_dos_resultados(resultados)
    return resposta, sugestoes, resultados, aviso
