import json
import re
import unicodedata


PREVENCAO_MS = (
    "https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/c/chikungunya/prevencao/prevencao"
)

DIRETRIZES_MS = (
    "https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/svsa/chikungunya/"
    "diretrizes-para-a-organizacao-dos-servicos-de-atencao-a-saude-em-situacao-de-aumento-"
    "de-casos-ou-de-epidemia-por-arboviroses"
)
INCIDENCIA = "Incidência / 100 mil"
CASOS = "Casos confirmados"

INTERPRETACOES = {
    "Casos confirmados": "O total de casos indica o volume de casos confirmados registrados.",
    "Hospitalizações": "O total de hospitalizações indica o volume de internações registradas.",
    "Incidência / 100 mil": "A incidência relaciona os casos confirmados à população do bairro.",
    "Casos hospitalizados (%)": (
        "O percentual de hospitalização usa os casos confirmados como denominador. "
        "Poucos casos podem produzir percentuais altos."
    ),
    "Letalidade (%)": "A letalidade usa os casos confirmados como denominador e é sensível a contagens pequenas.",
    "Óbitos": "O total de óbitos representa os óbitos registrados no recorte.",
}


def achados_prioritarios(resultados: list[dict]) -> list[str]:
    achados = []
    for resultado in resultados:
        if resultado["grafico"] != "Ranking de bairros":
            continue

        filtros = resultado["filtros"]
        inicio, fim = filtros["inicio"], filtros["fim"]
        escopo = f"Em {inicio}" if inicio == fim else f"De {inicio} a {fim}"
        bairros = resultado["bairros_exibidos"]
        liderancas = {}
        maximos = {}
        for metrica in (filtros["metrica"], filtros["comparativa"]):
            validos = [linha for linha in bairros if linha.get(metrica) is not None]
            if validos:
                maior = max(linha[metrica] for linha in validos)
                maximos[metrica] = maior
                liderancas[metrica] = [
                    linha["Bairro"] for linha in validos if linha[metrica] == maior
                ]

        principal = filtros["metrica"]
        if principal not in liderancas:
            achados.append(f"{escopo}, faltam valores para indicar bairros em **{principal}**.")
            continue

        nomes = ", ".join(liderancas[principal])
        achados.append(
            f"{escopo}, em **{principal}**, merecem atenção entre os bairros exibidos: **{nomes}**."
        )
        comparativa = filtros["comparativa"]
        if comparativa in liderancas:
            outros = ", ".join(liderancas[comparativa])
            coincidem = set(liderancas[principal]) == set(liderancas[comparativa])
            leitura = "O destaque coincide" if coincidem else "Os destaques diferem conforme o indicador"
            achados.append(
                f"{leitura}. Na comparação por **{comparativa}**, "
                f"entre esses mesmos bairros, o maior valor é de **{outros}**."
            )
        elif comparativa != "Nenhuma":
            achados.append(f"Faltam valores de **{comparativa}** para comparar os bairros exibidos.")

        if maximos.get(INCIDENCIA, 0) > 0:
            territorios = ", ".join(liderancas[INCIDENCIA])
            achados.append(
                f"**Prioridade inicial para vigilância territorial — {territorios}.** "
                "A maior incidência registrada entre os bairros exibidos orienta onde começar "
                "a investigação. Antes de definir a intervenção, verifique a contagem de casos, "
                "a população usada no cálculo, a evolução recente e os dados de vigilância do vetor."
            )
        if maximos.get(CASOS, 0) > 0:
            territorios = ", ".join(liderancas[CASOS])
            achados.append(
                f"**Atenção à demanda assistencial — {territorios}.** "
                "O maior volume de casos registrados entre os bairros exibidos indica onde "
                "avaliar primeiro a demanda. Confira também a procura por atendimento e as "
                "hospitalizações antes de dimensionar a resposta."
            )
        if maximos.get(INCIDENCIA, 0) > 0 or maximos.get(CASOS, 0) > 0:
            achados.append(
                f"[Ministério da Saúde — Diretrizes para a organização dos serviços de saúde "
                f"em situações de aumento de arboviroses]({DIRETRIZES_MS})"
            )

        achados.extend(INTERPRETACOES[metrica] for metrica in liderancas if metrica in INTERPRETACOES)

    return list(dict.fromkeys(achados))


def formatar_achados(resultados: list[dict]) -> str:
    achados = achados_prioritarios(resultados)
    return "**Bairros que merecem atenção no recorte**\n\n" + "\n\n".join(achados) if achados else ""


def leitura_dos_dados(resultados: list[dict]) -> str:
    leituras = []
    for resultado in resultados:
        if resultado["grafico"] == "Evolução anual":
            serie = resultado["serie_anual"]
            if serie:
                pico = max(linha[CASOS] for linha in serie)
                anos = ", ".join(str(linha["Ano"]) for linha in serie if linha[CASOS] == pico)
                leituras.append(
                    f"O maior total anual da série exibida foi de **{pico} casos confirmados**, "
                    f"em **{anos}**. Uma série agregada descreve o conjunto selecionado."
                )
            continue

        bairros = resultado["bairros_exibidos"]
        comparaveis = [
            bairro for bairro in bairros
            if bairro.get(INCIDENCIA) is not None and bairro.get(CASOS) is not None
        ]
        if comparaveis:
            maior_incidencia = max(bairro[INCIDENCIA] for bairro in comparaveis)
            maior_total = max(bairro[CASOS] for bairro in comparaveis)
            destaques = [
                f"**{bairro['Bairro']}** ({bairro[CASOS]} casos confirmados)"
                for bairro in comparaveis if bairro[INCIDENCIA] == maior_incidencia
            ]
            lideres_volume = [
                f"**{bairro['Bairro']}**"
                for bairro in comparaveis if bairro[CASOS] == maior_total
            ]
            taxa = f"{maior_incidencia:.2f}".replace(".", ",")
            leituras.append(
                f"Entre os bairros com os dois indicadores disponíveis, a maior incidência foi "
                f"de {taxa} por 100 mil habitantes, em {', '.join(destaques)}. "
                f"O maior volume de casos foi de **{maior_total}**, em {', '.join(lideres_volume)}. "
                "A estabilidade da taxa depende da população e da contagem de casos."
            )
            continue

        metrica = resultado["filtros"]["metrica"]
        if any(bairro.get(metrica) is not None for bairro in bairros):
            leituras.append(INTERPRETACOES.get(metrica, "A leitura se limita ao indicador e ao período consultados."))

    return "\n\n".join(dict.fromkeys(leituras)) or "O recorte consultado tem dados insuficientes para interpretação."


def formatar_leitura(texto: str) -> str:
    return "**Leitura epidemiológica**\n\n" + texto


REFERENCIA_FATO = re.compile(r"\[\[(F[1-9]\d*)\]\]")
UNIDADES = {
    CASOS: " casos confirmados",
    "Hospitalizações": " hospitalizações",
    "Óbitos": " óbitos",
    INCIDENCIA: " casos por 100 mil habitantes",
    "Casos hospitalizados (%)": "%",
    "Letalidade (%)": "%",
}


def fatos_numericos(resultados: list[dict]) -> dict[str, dict]:
    fatos = {}
    for resultado in resultados:
        if resultado["grafico"] == "Ranking de bairros":
            linhas = resultado["bairros_exibidos"]
            filtros = resultado["filtros"]
            periodo = [filtros["inicio"], filtros["fim"]]
            recorte = None
        else:
            linhas = resultado["serie_anual"]
            periodo = None
            recorte = resultado.get("bairros")

        for linha in linhas:
            for metrica, unidade in UNIDADES.items():
                numero = linha.get(metrica)
                if numero is None:
                    continue
                valor = f"{numero:.2f}".rstrip("0").rstrip(".").replace(".", ",")
                fatos[f"F{len(fatos) + 1}"] = {
                    "bairro_ou_recorte": linha.get("Bairro", recorte),
                    "periodo": periodo or [linha["Ano"], linha["Ano"]],
                    "indicador": metrica,
                    "valor_e_unidade": valor + unidade,
                }
    return fatos


def inserir_fatos(texto: str, fatos: dict[str, dict]) -> str | None:
    referencias = REFERENCIA_FATO.findall(texto)
    restante = REFERENCIA_FATO.sub("", texto)
    if (
        not texto.strip()
        or (fatos and not referencias)
        or any(ref not in fatos for ref in referencias)
        or re.search(r"[0-9%]|\[\[|\]\]", restante)
    ):
        return None
    return REFERENCIA_FATO.sub(
        lambda match: fatos[match[1]]["valor_e_unidade"], texto
    )


def interpretar_resultados(pergunta: str, resultados: list[dict], metrica_confirmada, gerar_texto) -> str:
    achados = formatar_achados(resultados)
    fatos = fatos_numericos(resultados)
    mensagens = [
        {"role": "system", "content": (
            "Você é o especialista em epidemiologia do painel de chikungunya do Recife. "
            "Dirija-se a profissionais de saúde e gestores públicos. Em até três frases, "
            "interprete o recorte usando apenas os resultados agregados fornecidos. "
            "Distinga volume de casos, incidência pela população e proporção de internações "
            "entre os casos confirmados. Liderar em um indicador não implica liderar em outro. "
            "A métrica comparativa só inclui os bairros que aparecem no ranking principal. "
            "Leia proporções com cautela quando há poucos casos. "
            "Uma série que soma vários bairros não permite apontar líderes individuais. "
            "A aplicação destaca as prioridades por finalidade. Contextualize as limitações.  Não atribua causas, não declare surtos, "
            "não recomende condutas clínicas e não invente dados ou fontes. "
            "Escreva somente a interpretação, sem cabeçalho. Cite os valores com os marcadores "
            "em fatos_numericos. Exemplo: 'O bairro A registrou [[F1]], enquanto o bairro B "
            "teve a maior incidência, de [[F2]].' Cada marcador já inclui valor e unidade. "
            "Não escreva números ou unidades logo ao lado do marcador. "
            "Se houver fatos disponíveis, use pelo menos um marcador."
        )},
        {"role": "user", "content": json.dumps({
            "pergunta": pergunta,
            "resultados": resultados,
            "fatos_numericos": {f"[[{id_fato}]]": fato for id_fato, fato in fatos.items()},
            "metrica_confirmada_pelo_usuario": metrica_confirmada,
        }, ensure_ascii=False)},
    ]
    rascunho = gerar_texto(mensagens, max_novos_tokens=190).strip()
    texto = inserir_fatos(rascunho, fatos)
    if texto is None:
        mensagens.append({
            "role": "user",
            "content": (
                "Reescreva a interpretação em até três frases. Substitua todos os valores "
                "numéricos pelos marcadores exatos dos fatos fornecidos, como [[F1]]. "
                "Escreva somente a interpretação e use apenas os fatos do recorte."
            ),
        })
        rascunho = gerar_texto(mensagens, max_novos_tokens=190).strip()
        texto = inserir_fatos(rascunho, fatos)

    blocos = []
    if achados:
        blocos.append(achados)
    if texto is None:
        texto = leitura_dos_dados(resultados)
    blocos.append(formatar_leitura(texto))

    pergunta_simples = "".join(
        char for char in unicodedata.normalize("NFKD", pergunta.casefold())
        if not unicodedata.combining(char)
    )
    if re.search(r"\b(?:enfrentamento|prevencao|prevenir|intervencoes|medidas|acoes|o que fazer)\b", pergunta_simples):
        blocos.append(
            "**Vigilância e prevenção**\n\n"
            "Use o recorte para orientar a investigação com a vigilância municipal e confira a "
            "completude dos registros antes de definir prioridades. Como medida geral de prevenção, "
            "reforce a eliminação de criadouros do mosquito em domicílios e na vizinhança. "
            f"[Ministério da Saúde — Prevenção da chikungunya]({PREVENCAO_MS})"
        )
    return "\n\n".join(blocos)
