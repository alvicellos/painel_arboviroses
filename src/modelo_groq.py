import os
from pathlib import Path

import requests
from dotenv import dotenv_values


ARQUIVO_ENV = Path(__file__).resolve().parents[1] / ".env"
MODELO_GROQ = "openai/gpt-oss-20b"
URL_GROQ = "https://api.groq.com/openai/v1/chat/completions"

ERROS_HTTP = {
    401: "A Groq rejeitou a chave. Confira a variável GROQ_API_KEY.",
    403: "A chave da Groq não tem permissão para usar o modelo configurado.",
    404: "O modelo configurado não está disponível na Groq.",
    429: "Limite de requisições da Groq atingido. Aguarde e tente novamente.",
}


class ErroGroq(RuntimeError):
    pass


class RequisicaoGroqRejeitada(ErroGroq):
    pass


def detalhes_erro(resposta):
    try:
        erro = resposta.json().get("error")
    except (ValueError, AttributeError):
        return None, None

    if not isinstance(erro, dict):
        return None, None

    # Exiba apenas nomes de parâmetros conhecidos, sem replicar a mensagem da API.
    mensagem = erro.get("message")
    parametro = erro.get("param")
    for campo in ("response_format", "reasoning_effort", "max_completion_tokens", "temperature", "model"):
        if parametro == campo or (isinstance(mensagem, str) and f"'{campo}'" in mensagem):
            return erro.get("code"), campo
    return erro.get("code"), None


def enviar_requisicao(payload, chave):
    try:
        return requests.post(
            URL_GROQ,
            headers={"Authorization": f"Bearer {chave}"},
            json=payload,
            timeout=(5, 30),
        )
    except requests.exceptions.Timeout:
        raise ErroGroq("A Groq demorou mais que o esperado. Tente novamente.") from None
    except requests.exceptions.RequestException:
        raise ErroGroq("Não foi possível conectar à Groq. Verifique sua conexão.") from None


def gerar_texto(
    mensagens: list[dict[str, str]],
    *,
    max_novos_tokens: int = 256,
    modo_json: bool = False,
) -> str:
    chave = os.environ.get("GROQ_API_KEY", "").strip()
    if not chave:
        try:
            configuracao = dotenv_values(ARQUIVO_ENV, encoding="utf-8-sig", interpolate=False)
        except (OSError, UnicodeError):
            raise ErroGroq("Não foi possível ler o arquivo .env da raiz do projeto.") from None
        chave = (configuracao.get("GROQ_API_KEY") or "").strip()
    if not chave:
        raise ErroGroq("Preencha GROQ_API_KEY no arquivo .env da raiz do projeto.")

    payload = {
        "model": MODELO_GROQ,
        "messages": mensagens,
        "max_completion_tokens": max_novos_tokens + 1536,
        "reasoning_effort": "low",
    }
    if modo_json:
        payload["response_format"] = {"type": "json_object"}

    resposta = enviar_requisicao(payload, chave)
    if resposta.status_code == 400:
        codigo, parametro = detalhes_erro(resposta)
        if modo_json and codigo != "context_length_exceeded" and parametro in (None, "response_format"):
            # O coordenador também valida o JSON com Pydantic nesta alternativa.
            payload.pop("response_format")
            resposta = enviar_requisicao(payload, chave)

    if resposta.status_code == 400:
        codigo, parametro = detalhes_erro(resposta)
        etapa = "seleção das consultas" if modo_json else "interpretação dos resultados"
        detalhe = f" Parâmetro informado pela API: {parametro}." if parametro else ""
        if codigo == "context_length_exceeded":
            detalhe = " O contexto ultrapassou o limite do modelo."
        elif codigo == "json_validate_failed":
            detalhe = " A resposta não passou na validação JSON da Groq."
        raise RequisicaoGroqRejeitada(f"A Groq rejeitou a requisição durante a {etapa} (HTTP 400).{detalhe}")

    if not resposta.ok:
        mensagem = ERROS_HTTP.get(resposta.status_code, "A Groq está temporariamente indisponível.")
        raise ErroGroq(mensagem)

    try:
        escolha = resposta.json()["choices"][0]
        texto = escolha["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError):
        raise ErroGroq("A Groq devolveu uma resposta em formato inesperado.") from None

    if escolha.get("finish_reason") == "length":
        raise ErroGroq("A Groq atingiu o limite de geração antes de concluir a resposta.")
    if not isinstance(texto, str) or not texto.strip():
        raise ErroGroq("A Groq não retornou uma resposta de texto. Tente novamente.")
    return texto.strip()
