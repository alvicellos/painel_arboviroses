from pathlib import Path

import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


BASE = Path(__file__).resolve().parent.parent
CAMINHO_MODELO = BASE / "models" / "qwen3_0_6b"

MAX_TOKENS = 256
LIMITE_CONTEXTO = 8192


@st.cache_resource
def carregar_modelo():
    tokenizer = AutoTokenizer.from_pretrained(
        CAMINHO_MODELO,
        local_files_only=True,
    )

    modelo = AutoModelForCausalLM.from_pretrained(
        CAMINHO_MODELO,
        dtype=torch.float32,
        local_files_only=True,
    ).to("cpu").eval()

    return tokenizer, modelo


def gerar_resposta(pergunta, dados):
    tokenizer, modelo = carregar_modelo()

    contexto = preparar_contexto(dados)

    mensagens = [
        {
            "role": "system",
            "content": (
                "Responda em português usando apenas os dados fornecidos. "
                "Não invente informações. Seja objetivo."
            ),
        },
        {
            "role": "user",
            "content": f"{contexto}\n\nPergunta: {pergunta}",
        },
    ]

    entrada = tokenizer.apply_chat_template(
        mensagens,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
        enable_thinking=False,
    )

    n_tokens = entrada["input_ids"].shape[1]
    limite = min(
        LIMITE_CONTEXTO,
        modelo.config.max_position_embeddings,
    )

    if n_tokens + MAX_TOKENS > limite:
        raise ValueError(
            "A consulta contém dados demais. "
            "Informe um bairro e um ano para reduzir o recorte."
        )

    with torch.inference_mode():
        saida = modelo.generate(
            **entrada,
            max_new_tokens=MAX_TOKENS,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )

    resposta = tokenizer.decode(
        saida[0][n_tokens:],
        skip_special_tokens=True,
    ).strip()

    if not resposta:
        raise ValueError("O modelo não produziu uma resposta.")

    return resposta


def preparar_contexto(dados):
    contexto = """
Dados epidemiológicos do Recife. Cada registro é um caso confirmado de chikungunya.
Os dados não incluem outras doenças, como dengue ou zika.
Colunas do arquivo 'dados_bairros_anos.csv':
NM_BAIRRO: bairro; NU_ANO: ano; TOTAL_CASOS: casos;
TOTAL_HOSPITALIZACOES: hospitalizações; TOTAL_OBITOS: óbitos;
POPULACAO: população; INCIDENCIA_100K: incidência por 100 mil;
PERC_CASOS_HOSP: percentual de casos hospitalizados.
Não some populações repetidas entre bairros ou entre anos.
Observe a concordância verbal e nominal quando informar valores iguais a 1;
Por exemplo: "foi registrado 1 caso", "foi registrada 1 hospitalização",
"foi registrado 1 óbito".
Os dados fornecidos abaixo são um recorte de 'dados_bairros_anos.csv'.
"""

    return contexto + "\nDados disponíveis:\n" + dados.to_csv(index=False)