from pathlib import Path
from src.get_news import check_robots, get_snapshot_html, get_corpo_materias, gravar_csv_noticias, gravar_txt_noticias
import matplotlib.pyplot as plt

def contar_palavras_news():
    exemplo = "teste casa teste casa rua outro dia dia outro fila norte"
    contagem = {}

    lista_palavras = exemplo.split()

    for palavra in lista_palavras:
        contagem[palavra] = contagem.get(palavra, 0) + 1

    lista_tuplas = [(value, item) for item, value in contagem.items()]
    lista_tuplas.sort(reverse=True)

    Y = [x[0] for x in lista_tuplas]
    X = [x[1] for x in lista_tuplas]

    # O prof usa uma função Count nativa do python

    print(lista_tuplas)
    print(contagem)

    print(f"X: {X} Y: {Y}")

    plt.bar(X, Y)
    plt.show()