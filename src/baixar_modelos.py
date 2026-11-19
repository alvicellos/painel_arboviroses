from pathlib import Path
from huggingface_hub import snapshot_download

# Diretório raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Diretório onde os modelos serão salvos
MODELS_DIR = BASE_DIR / "models"

modelos = {
    #"qwen3_1_7b": "Qwen/Qwen3-1.7B", ok
    "qwen3_0_6b": "Qwen/Qwen3-0.6B",
    #"smollm2": "HuggingFaceTB/SmolLM2-1.7B-Instruct", baixando em outro terminal
    #"tinyllama": "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
}

for nome, repo in modelos.items():
    print(f"Baixando {nome}...")

    snapshot_download(
        repo_id=repo,
        local_dir=MODELS_DIR / nome
    )

    print(f"{nome} baixado com sucesso!")