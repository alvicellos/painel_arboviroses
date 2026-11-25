from pathlib import Path
from threading import Lock

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

CAMINHO_MODELO = Path(__file__).resolve().parents[1] / "models" / "qwen3_0_6b"

_modelo_carregado = None
_lock_carregamento = Lock()
_lock_geracao = Lock()


class ModeloIndisponivel(RuntimeError):
    pass


def carregar_modelo():
    global _modelo_carregado

    with _lock_carregamento:
        if _modelo_carregado is None:
            try:
                tokenizer = AutoTokenizer.from_pretrained(
                    CAMINHO_MODELO, local_files_only=True
                )
                modelo = AutoModelForCausalLM.from_pretrained(
                    CAMINHO_MODELO,
                    dtype=torch.float32,
                    local_files_only=True,
                ).to("cpu").eval()
            except (OSError, ValueError, RuntimeError) as exc:
                raise ModeloIndisponivel(
                    "Não foi possível carregar o Qwen3 0.6B em "
                    "models/qwen3_0_6b."
                ) from exc

            _modelo_carregado = tokenizer, modelo

        return _modelo_carregado


def gerar_texto(mensagens, *, max_novos_tokens=256, limite_contexto=8192):
    tokenizer, modelo = carregar_modelo()

    entrada = tokenizer.apply_chat_template(
        mensagens,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
        enable_thinking=False,
    )
    tamanho_entrada = entrada["input_ids"].shape[1]
    limite = min(limite_contexto, modelo.config.max_position_embeddings)

    if tamanho_entrada + max_novos_tokens > limite:
        raise ValueError("A entrada excede o limite de contexto do modelo.")

    with _lock_geracao, torch.inference_mode():
        saida = modelo.generate(
            **entrada,
            max_new_tokens=max_novos_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )

    return tokenizer.decode(
        saida[0, tamanho_entrada:],
        skip_special_tokens=True,
    ).strip()