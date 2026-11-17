import re
import unicodedata
import pandas as pd

def normalizar(texto):
    texto = unicodedata.normalize("NFD", texto.upper())
    return "".join(
        c for c in texto
        if unicodedata.category(c) != "Mn"
    )

def consultar_dados(df, pergunta):
    texto = normalizar(pergunta)

    bairros = df["NM_BAIRRO"].dropna().unique()

    bairro = next(
        (b for b in sorted(bairros, key=len, reverse=True)
         if re.search(rf"(?<!\w){re.escape(normalizar(b))}(?!\w)", texto)),
        None
    )

    anos_pergunta = [int(ano) for ano in re.findall(r"\b(?:19|20)\d{2}\b", texto)]
    anos_disponiveis = pd.to_numeric(df["NU_ANO"], errors="coerce")
    anos_encontrados = [
    ano for ano in anos_pergunta
    if ano in anos_disponiveis.values
    ]

    if bairro is None and not anos_encontrados:
        print("Anos na pergunta:", anos_pergunta)
        print("Anos encontrados:", anos_encontrados)
        raise ValueError("Informe um bairro ou ano na pergunta.")

    if bairro is not None:
        df = df[df["NM_BAIRRO"] == bairro]

    if anos_encontrados:
          df = df[pd.to_numeric(df["NU_ANO"], errors="coerce").isin(anos_encontrados)]

    return df