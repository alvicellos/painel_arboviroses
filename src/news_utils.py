import matplotlib.pyplot as plt
from collections import Counter
import pandas as pd

excluir = [
    'de', 'a', 'e', 'do', 'da', 'o', 'é', 'em', 'que', 'para', 'um', 'com', 'no', 'as', 'O', 'os', 
    'uma', 'se', 'na', 'como', 'R$', 'à', 'não', 'nesta', 'ao', 'por', 'dos', 'às', 'das', 'r$'
]

def contar_palavras_news(arquivo, slice):
    with open(arquivo, "r", encoding="utf-8") as noticias:
        texto = noticias.read().lower()        
        lista_palavras = [palavra for palavra in texto.split(" ") if palavra != " " and palavra not in excluir]
        contador = Counter(lista_palavras)
    
    lista_tuplas = [(value, item) for item, value in contador.items()]
    lista_tuplas.sort(reverse=True)

    X = [x[1] for x in lista_tuplas[:slice]]   
    Y = [x[0] for x in lista_tuplas[:slice]]
    
    df_palavras = pd.DataFrame({
        "palavra" : X,
        "ocorrencia": Y
    })
    
    return X, Y, df_palavras