from pathlib import Path
import time
import gc
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from consultar_dados import consultar_dados

# CONFIGURAÇÕES
BASE = Path(__file__).resolve().parent.parent
MODELOS = ["qwen3_1_7b", "qwen3_0_6b", "smollm2", "tinyllama"]
RESULTADOS = BASE / "resultados"
RESULTADOS.mkdir(exist_ok=True)

MAX_TOKENS = 256
LIMITE_CONTEXTO = 8192

# TESTE INICIAL: um modelo e uma pergunta
#MODELOS = MODELOS[:1]
N_PERGUNTAS = 10


PERGUNTAS = [
    # Consultas diretas
    "Quantos casos foram registrados nos Aflitos em 2017?",
    "Quantas hospitalizações foram registradas na Tamarineira em em 2021?",
    "Quantos óbitos foram registrados em Areias em 2019?",

    # Evolução temporal
    "Como evoluiu a quantidade de casos na Imbiribeira ao longo dos anos disponíveis?",

    # Comparação entre bairros
    "Qual bairro registrou a maior quantidade de casos em 2020? Informe o bairro e a quantidade.",

    # Novas perguntas
    "Qual bairro registrou a maior quantidade de hospitalizações em 2018? Informe o bairro e a quantidade.",
    "Qual bairro apresentou a maior incidência de casos por 100 mil habitantes em 2017? Informe o bairro e a incidência.",
    "Qual foi o percentual de casos hospitalizados em Jardim Sao Paulo em 2021?",
    "Em Dois Unidos, qual ano apresentou a maior quantidade de casos? Informe o ano e a quantidade.",
    "Quais foram os três bairros com maior quantidade de óbitos em 2019? Informe os bairros e suas respectivas quantidades."
]


# CONTEXTO
#arquivos = ["dados_bairros_anos.csv", "serie_historica_cidade.csv", "acumulado_bairros.csv"]
#arquivos = ["dados_bairros_anos.csv"]
arquivos = ["serie_historica_cidade.csv"]

def preparar_contexto():
    contexto = """Dados epidemiológicos do Recife.
Colunas do arquivo 'dados_bairros_anos.csv':
NM_BAIRRO: bairro; NU_ANO: ano; TOTAL_CASOS: casos;
TOTAL_HOSPITALIZACOES: hospitalizações; TOTAL_OBITOS: óbitos;
POPULACAO: população; INCIDENCIA_100K: incidência por 100 mil;
PERC_CASOS_HOSP: percentual de casos hospitalizados.
Descrição do arquivo 'serie_historica_cidade.csv': 
cada linha principal representa a cidade do Recife em determinado ano.
Descrição do arquivo 'acumulado_bairros.csv': 
cada linha principal representa um bairro com os totais acumulados de casos, hospitalizações e óbitos na série histórica. 
Não some populações repetidas entre bairros.
Cada linha principal representa um bairro em determinado ano.
Não some populações repetidas entre anos.
Observe a concordância verbal e nominal quando informar algum valor igual a 1. 
Por exemplo, "foi registrado 1 caso", "foi regisrada 1 hospitalização", "foi registrado 1 óbito"
"""
    for arquivo in arquivos:
        df = pd.read_csv(BASE / "data" / "processed" / arquivo)
        contexto += f"\n{arquivo}:\n{df.to_csv(index=False)}"
    
    return contexto

    


# TESTES
def testar():
    df = pd.read_csv(BASE / "data" / "processed"/ "dados_bairros_anos.csv")
    registros = []

    for nome in MODELOS:
        caminho = BASE / "models" / nome
        inicio = time.perf_counter()

        tokenizer = AutoTokenizer.from_pretrained(caminho, local_files_only=True)
        model = AutoModelForCausalLM.from_pretrained(
            caminho, dtype=torch.float32, local_files_only=True
        ).to("cpu").eval()

        carga = round(time.perf_counter() - inicio, 2)
        pesos = round(sum(
            p.stat().st_size for p in caminho.rglob("*")
            if p.suffix in (".safetensors", ".bin")
        ) / 1024**2, 2)

        for numero, pergunta in enumerate(PERGUNTAS[:N_PERGUNTAS], 1):
            dados = consultar_dados(df, pergunta)
            contexto = dados.to_csv(index=False)
            mensagens = [
                {"role": "system", "content":
                 "Responda em português usando apenas os dados fornecidos. "
                 "Não invente informações. Seja objetivo."},
                {"role": "user", "content": f"{contexto}\n\nPergunta: {pergunta}"}
            ]

            args = {
                "add_generation_prompt": True,
                "tokenize": True,
                "return_dict": True,
                "return_tensors": "pt"
            }

            if nome.startswith("qwen3"):
                args["enable_thinking"] = False

            inputs = tokenizer.apply_chat_template(mensagens, **args)
            n_tokens = inputs["input_ids"].shape[1]
            
            resposta, tempo, saida, status = "", None, 0, "OK"

            if n_tokens + MAX_TOKENS > LIMITE_CONTEXTO:
                status = f"Contexto excedido: {n_tokens} tokens"
            else:
                try:
                    inicio = time.perf_counter()
                    with torch.inference_mode():
                        output = model.generate(
                            **inputs, max_new_tokens=MAX_TOKENS,
                            do_sample=False, pad_token_id=tokenizer.eos_token_id
                        )
                    tempo = round(time.perf_counter() - inicio, 2)
                    novos = output[0][n_tokens:]
                    saida = len(novos)
                    resposta = tokenizer.decode(novos, skip_special_tokens=True).strip()
                    if not resposta:
                        status = "VAZIA"
                except Exception as erro:
                    status = f"ERRO: {erro}"

            registros.append({
                "modelo": nome, "arquitetura": model.config.model_type,
                "tipo": str(model.dtype), "prompt": "definicoes_agregacoes",
                "pergunta_n": numero, "pergunta": pergunta,
                "resposta": resposta, "status": status,
                "sem_resposta": int(not resposta),
                "tempo_s": tempo, "carga_s": carga, "pesos_mib": pesos,
                "tokens_entrada": n_tokens, "tokens_saida": saida
            })

            pd.DataFrame(registros).to_csv(
                RESULTADOS / "resultados_detalhados.csv",
                index=False, encoding="utf-8-sig"
            )
            print(f"\nModelo: {nome}")
            print(f"Pergunta {numero}: {pergunta}")
            print(f"Resposta: {resposta}")
            print(f"Status: {status}")
            print(f"Tempo: {tempo}s")
            print("-" * 60)

        del model, tokenizer
        gc.collect()

    return pd.DataFrame(registros)

# RESUMO
def gerar_resumo(df):
    resumo = df.groupby(["modelo", "arquitetura", "tipo", "prompt"], as_index=False).agg(
        perguntas=("pergunta_n", "count"),
        sem_resposta=("sem_resposta", "sum"),
        tempo_medio_s=("tempo_s", "mean"),
        carga_s=("carga_s", "first"),
        pesos_mib=("pesos_mib", "first"),
        tokens_entrada=("tokens_entrada", "mean"),
        tokens_saida=("tokens_saida", "mean")
    ).round(2)

    resumo.to_csv(
        RESULTADOS / "resumo_comparativo.csv",
        index=False, encoding="utf-8-sig"
    )
    print("\n", resumo.to_string(index=False))

if __name__ == "__main__":
    gerar_resumo(testar())
