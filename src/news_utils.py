import matplotlib.pyplot as plt
from collections import Counter
import unicodedata
import pandas as pd
import re

EXCLUIR = frozenset("""
a as o os um uma uns umas de do da dos das em no na nos nas por para per com sem sob sobre
ao aos à às e ou mas que se quando onde como qual quais quanto quantos porque pois
ele ela eles elas eu tu nos vos me te lhe lhes seu sua seus suas meu minha dele dela
este esta estes estas esse essa esses essas isso isto aquele aquela aquilo
ser sao é foi era sera seja sendo estar esta estao estava ter tem tinha havia ha
mais menos muito muitos pouco pouca todo toda todos todas outro outra outros outras
ja nao sim tambem entre ate apos antes durante desde cada mesmo mesma assim ainda
segundo disse afirmou destacou ressaltou explicou acordo caso ano anos dia dias
pelo pela pelos pelas pode podem podera deve devem havera fica ficam vai vao
grande grandes parte partes forma vezes apenas cerca ainda entao logo trata-se
""".split())

excluir = [
    'de', 'a', 'e', 'do', 'da', 'o', 'é', 'em', 'que', 'para', 'um', 'com', 'no', 'as', 'O', 'os', 
    'uma', 'se', 'na', 'como', 'R$', 'à', 'não', 'nesta', 'ao', 'por', 'dos', 'às', 'das', 'r$'
]

# --------------------------------------------------------------------------------------------------------------- Funções para limpeza do texto
def palavras(texto: str) -> list[str]:
    return re.findall(r"\w+(?:-\w+)?", texto.lower(), flags=re.UNICODE)

def reconhecer_acento(palavra: str) -> bool:
    decomposta = unicodedata.normalize("NFD", palavra)
    return any(unicodedata.category(c) == "Mn"
        for c in decomposta
    )

def sem_acento(palavra: str) -> str:    
    decomposta = unicodedata.normalize("NFD", palavra.lower())
    return "".join(c for c in decomposta if unicodedata.category(c) != "Mn")

# --------------------------------------------------------------------------------------------------------------- Contagem de palavras
def contar_palavras_news(arquivo, qtd_palavras_selecionadas):
    with open(arquivo, "r", encoding="utf-8") as noticias:
        texto = noticias.read().lower()
        total_caracteres = len(texto)
        palavras_texto = palavras(texto)  # extrai as palavras com os acentos, ç, ~, etc
        total_palavras = len(palavras_texto)
                
    # Contar as palavras normalizando por todas as palavras sem os acentos, ç, ~, etc
    # e guardar a referência para retornar a palavra original
    
    lista_palavras = [] # para contagem
    equivalencia = {}

    for palavra in palavras_texto:
        palavra_sem_acento = sem_acento(palavra)
        if not palavra_sem_acento.isdigit() and palavra_sem_acento not in EXCLUIR and len(palavra_sem_acento) >= 4:
            # se a palavra tem acentos, ç, ~, etc retorna True
            # guardar equivalencia, sem repetições de grafias já guardadas
            if reconhecer_acento(palavra) and len(equivalencia.get(palavra_sem_acento, [])) == 0:
                equivalencia[palavra_sem_acento] = equivalencia.get(palavra_sem_acento, []) + [palavra]
            else:                                                                                  # guarda na lista palavras sem ç, ~, etc no original
                if equivalencia.get(palavra_sem_acento, 0) == 0:
                    equivalencia[palavra] = palavra        
            lista_palavras.append(palavra_sem_acento)    
    
    #lista_palavras = [palavra for palavra in equivalencia]    
    
    #lista_palavras = [sem_acento(palavra) for palavra in texto.split(" ") if palavra != " " and not palavra.isdigit() and palavra not in EXCLUIR]
    
    contador = Counter(lista_palavras)
    
    lista_quatidade_palavra = [(value, item) for item, value in contador.items()]
    lista_quatidade_palavra.sort(reverse=True)
    
    palavras_sem_repeticao = len(lista_quatidade_palavra)
    
    palavra_x = [x[1] for x in lista_quatidade_palavra[:qtd_palavras_selecionadas]]
    
    # Retornar às grafias acentuadas das palavras    
    palavra_x = [
        equivalencia[palavra][0] if isinstance(equivalencia[palavra], list) 
        else equivalencia[palavra]
        for palavra in palavra_x
    ]
    
    quantidade_y = [x[0] for x in lista_quatidade_palavra[:qtd_palavras_selecionadas]]
    
    df_palavras = pd.DataFrame({
        "palavra" : palavra_x,
        "ocorrencias": quantidade_y,
    })
    
    #return palavra_x, quantidade_y, df_palavras
    return df_palavras, total_palavras, palavras_sem_repeticao, total_caracteres