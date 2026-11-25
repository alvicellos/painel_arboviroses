from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from src.modelo_qwen import gerar_texto


class ContextoAnalises(BaseModel):
    metricas: list[str] = Field(min_length=1)
    anos: list[int] = Field(min_length=1)
    bairros: list[str]


class PlanoAnalise(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    secao: Literal["evolucao", "ranking", "esclarecer"]
    bairros: list[str] | None = None
    metrica: str | None = None
    periodo: tuple[int, int] | None = None
    qtd_bairros: Annotated[int, Field(ge=1, le=20)] | None = None
    esclarecimento: str | None = Field(default=None, max_length=400)


class PlanoInvalido(ValueError):
    pass


def validar_plano(plano: PlanoAnalise, contexto: ContextoAnalises) -> None:
    campos = plano.model_dump(exclude_none=True).keys() - {"secao"}

    if plano.secao == "esclarecer":
        if campos != {"esclarecimento"} or not (plano.esclarecimento or "").strip():
            raise PlanoInvalido("O plano deve conter apenas um esclarecimento.")
        return

    if plano.secao == "evolucao":
        if campos != {"bairros"} or not set(plano.bairros or []).issubset(
            contexto.bairros
        ):
            raise PlanoInvalido("A seleção de bairros da evolução é inválida.")
        return

    if not campos or campos - {"metrica", "periodo", "qtd_bairros"}:
        raise PlanoInvalido("O plano contém campos incompatíveis com o ranking.")

    if plano.metrica is not None and plano.metrica not in contexto.metricas:
        raise PlanoInvalido("A métrica sugerida não existe no painel.")

    if plano.periodo is not None:
        inicio, fim = plano.periodo
        if inicio > fim or inicio not in contexto.anos or fim not in contexto.anos:
            raise PlanoInvalido("O período sugerido é inválido.")


def gerar_plano(pergunta: str, contexto: ContextoAnalises) -> PlanoAnalise:
    mensagens = [
        {
            "role": "system",      
            "content": (
                "Responda apenas com um objeto JSON. Leia a pergunta e inclua TODOS "
                "os filtros que ela solicita. Use os nomes exatos do catalogo. "
                "Ranking ordena bairros por uma metrica; evolucao mostra uma serie anual. "
                "O mapa de calor usa ranking. Uma lista vazia em bairros significa todos. "
                "Exemplo: 'Quero os 3 bairros com mais casos confirmados' -> "
                '{"secao":"ranking","metrica":"Casos confirmados","qtd_bairros":3}. '
                "Use periodo como [ano inicial, ano final] se solicitado. "
                "Exemplo de evolucao: "
                '{"secao":"evolucao","bairros":["Boa Viagem"]}. '
                "Se a pergunta nao puder ser atendida, use "
                '{"secao":"esclarecer","esclarecimento":"Qual recorte deseja consultar?"}.'
            ),
        },
        {
            "role": "user",
            "content": (
                f"Catálogo do painel:\n{contexto.model_dump_json()}\n\n"
                f"Pergunta:\n{pergunta}"
            ),
        },
    ]

    texto = gerar_texto(mensagens, max_novos_tokens=256).strip()
    linhas = texto.splitlines()

    if (
        len(linhas) >= 3
        and linhas[0].strip().lower() in {"```json", "```"}
        and linhas[-1].strip() == "```"
    ):
        texto = "\n".join(linhas[1:-1]).strip()

    try:
        plano = PlanoAnalise.model_validate_json(texto)
    except ValidationError as exc:
        raise PlanoInvalido("A saída do modelo não segue o formato do plano.") from exc

    validar_plano(plano, contexto)
    return plano