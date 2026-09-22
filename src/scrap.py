import pandas as pd
import requests
from bs4 import BeautifulSoup

# O tratamento de erro será incrementado nas próximas iterações

url = "https://busca.ebc.com.br/?site_id=agenciabrasil&q=dengue"

palavras_chave = [
    "arbovirose",
    "dengue",
    "chikungunya",
    "zika",
    "Aedes aegypti",
    "mosquito",
    "vetor",
    "epidemiologia",
    "incidência",
    "prevalência",
    "hospitalização",
    "mortalidade",
    "letalidade",
    "surto",
    "vigilância epidemiológica"
    "pernilongo"
    "muriçoca"
]

try:
    response = requests.get(url)
    sopa = BeautifulSoup(response.text, "html.parser")

    titulos = []
    resumos_materias = []
    horarios_origem = []

    titulos_pagina = sopa.select('h4.media-heading')
    print(f"\nTotal de elementos encontrados: {len(titulos_pagina)}")
    for i, tag in enumerate(titulos_pagina, 1):
        #print(f"Item {i}: {tag.get_text().strip()}")
        titulo = tag.get_text().strip()
        titulos.append(titulo)
        
    resumos_pagina = sopa.select('div.media-body > p')
    print(f"\nTotal de elementos encontrados: {len(resumos_pagina)}")
    for i, tag in enumerate(resumos_pagina, 1):    
        texto_resumo = tag.get_text().strip().replace('\r', ' ').replace('\n', '')
        #print(f"Item {i}: {texto_resumo}")
        resumos_materias.append(texto_resumo)
        for palavra in palavras_chave:
            if palavra in texto_resumo:
                print(palavra, texto_resumo.count(palavra))         

    horarios_publicacao = sopa.select('p.info-new')
    print(f"\nTotal de elementos encontrados: {len(horarios_publicacao)}")
    for i, tag in enumerate(horarios_publicacao, 1):
        #print(f"Item {i}: {tag.get_text().strip()}")
        horario = tag.get_text().strip()    
        horarios_origem.append(horario)
        
    df_noticias = pd.DataFrame({
        "titulo_noticia": titulos,
        "resumo_materia": resumos_materias,
        "hora_publi_origem": horarios_origem    
    })

    df_noticias.to_csv(r".\data\news.csv", index=False)

except:
    pass