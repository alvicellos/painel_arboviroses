from datetime import datetime
from typing import Literal

from fastapi import Body, FastAPI, HTTPException, Path, Query

from src.carga_preparacao import (
    agregacao_bairros,
    carregar_dados_fonte,
    carregar_dados_populacao,
    criar_analise,
)
from src.tratamento_final import ANOS_EXCLUIDOS_ANALISE, gerar_dados_analise


dados = carregar_dados_fonte()
df_populacao, _ = carregar_dados_populacao()
dados_tratados, *_ = gerar_dados_analise(dados, ANOS_EXCLUIDOS_ANALISE)
_, _, df_bairro_ano = agregacao_bairros(dados_tratados.dropna(subset=["NM_BAIRRO"]))
bairros = df_bairro_ano["NM_BAIRRO"].unique().tolist()
validacao_bairros = Literal[tuple(bairros)]

app = FastAPI(
    title="API Painel de Arboviroses - Cidade do Recife",    
    description=(
        "Dados coletados da API da prefs + dados de população do IBGE"
        "e algumas análises da ocorrência dos casos da doença por bairros"
    ),
)

@app.get("/amostradados", tags=["dados completos"])
def serie_casos_arboviroses(
    quantidade: int = Query(
        default=50,
        ge=1,
        description="Quantidade de registros da amostra"
    )
):
    """
    Retorna uma amostra da série histórica com as
    colunas utilizadas na aplicação.
    """
    dados = carregar_dados_fonte()
    dados = dados.dropna()
    dados = dados.head(quantidade)

    dicionario_retorno = dados.to_dict(orient="records")

    return {
        "total_registros": len(dados),
        "dados": dicionario_retorno
    }


@app.get("/dadoscompletos/{ano}", tags=["dados completos"])
def dados_completos_por_ano(
    ano: int = Path(ge=2015, le=2025, description="Ano dos registros")
):
    """
    Retorna todos os registros da série histórica
    correspondentes ao ano informado.
    """
    dados = carregar_dados_fonte()
    dados = dados.dropna()

    # Filtrar pelo ano informado
    dados = dados[dados["NU_ANO"] == ano]

    return {
        "ano": ano,
        "total_registros": len(dados),
        "dados": dados.to_dict(orient="records")
    }

@app.get("/dadosenriquecidos/{bairro}", tags=["dados completos"])
def analisar_bairro(
    bairro: validacao_bairros
    ):
    """Retorna os indicadores do bairro com os critérios da página Análises."""
    df_analise = criar_analise(df_bairro_ano, df_populacao.copy())
    df_analise = df_analise[df_analise["NM_BAIRRO"] == bairro]
    registros = df_analise.astype(object).where(df_analise.notna(), None).to_dict(orient="records")

    return {
        "bairro": bairro,
        "total_registros": len(df_analise),
        "dados": registros
    }


@app.post("/analisar-dados", tags=["Análise"], description="Considere CLASSI_FIN == 5: registro descartado; HOSPITALIZ == 1: houve hospitalização; EVOLUCAO == 2: óbito pelo agravo.")
def analisar_dados(registros: list[dict] = Body(...)):

    colunas_obrigatorias = {
        "NU_NOTIFIC", "NU_ANO", "DT_NASC",
        "CS_SEXO", "CS_ESCOL_N", "NM_BAIRRO",
        "HOSPITALIZ", "EVOLUCAO", "CLASSI_FIN"
    }

    if not registros:
        raise HTTPException(
            status_code=422,
            detail="A lista de registros está vazia."
        )

    for i, registro in enumerate(registros):

        # Verificar colunas obrigatórias
        faltantes = colunas_obrigatorias - registro.keys()

        if faltantes:
            raise HTTPException(
                status_code=422,
                detail=f"Registro {i}: faltam {sorted(faltantes)}"
            )

        # Validar número da notificação
        if type(registro["NU_NOTIFIC"]) is not int:
            raise HTTPException(
                status_code=422,
                detail=f"Registro {i}: notificação inválida."
            )

        # Validar ano
        if type(registro["NU_ANO"]) is not int or not (
            2000 <= registro["NU_ANO"] <= 2100
        ):
            raise HTTPException(
                status_code=422,
                detail=f"Registro {i}: ano inválido."
            )

        # Validar data de nascimento
        try:
            datetime.strptime(registro["DT_NASC"], "%d/%m/%Y")
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=422,
                detail=f"Registro {i}: data de nascimento inválida."
            )

        # Validar sexo
        if registro["CS_SEXO"] not in ["M", "F", "I"]:
            raise HTTPException(
                status_code=422,
                detail=f"Registro {i}: sexo inválido."
            )

        # Validar escolaridade
        if type(registro["CS_ESCOL_N"]) is not int:
            raise HTTPException(
                status_code=422,
                detail=f"Registro {i}: escolaridade inválida."
            )

        # Validar bairro
        if not isinstance(registro["NM_BAIRRO"], str) or not registro["NM_BAIRRO"].strip():
            raise HTTPException(
                status_code=422,
                detail=f"Registro {i}: bairro inválido."
            )

        # Validar códigos numéricos
        for campo in ["HOSPITALIZ", "EVOLUCAO", "CLASSI_FIN"]:
            if type(registro[campo]) is not int:
                raise HTTPException(
                    status_code=422,
                    detail=f"Registro {i}: {campo} inválido."
                )

    # Processamento dos dados
    confirmados = [
        r for r in registros if r["CLASSI_FIN"] != 5
    ]

    hospitalizacoes = sum(
        r["HOSPITALIZ"] == 1 for r in confirmados
    )

    obitos = sum(
        r["EVOLUCAO"] == 2 for r in confirmados
    )

    return {
        "registros_recebidos": len(registros),
        "registros_nao_descartados": len(confirmados),
        "hospitalizacoes": hospitalizacoes,
        "obitos": obitos
    }
