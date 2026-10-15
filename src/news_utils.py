# Montar o pipeline para baixar várias matérias: É isso

#import requests
#from urllib.robotparser import RobotFileParser
#from bs4 import BeautifulSoup as bs
#from pathlib import Path
#import re
#import time
from pathlib import Path
from src.get_news import check_robots, get_snapshot_html, get_corpo_materias, gravar_csv_noticias, gravar_txt_noticias
import matplotlib.pyplot as plt

url = "https://agenciabrasil.ebc.com.br"
nome_agente = "INFNET-TESTEPB-IA/1.0 (material didatico; contato: marcelo.aalves@al.infnet.edu.br)"
terminacao = "saude"

def checar_permiss(endereco, agente, fim_url):    
    permissoes, tempo_espera = check_robots(url, nome_agente, [terminacao])    # lista    
    return permissoes, tempo_espera

#def gravar_snapshot(permissoes, agente, tempo_espera):    
#    get_snapshot_html(permissoes, agente, tempo_espera)

#def coletar_news(html_bruto, url_inicio, tempo_espera):
#    nome_noticia, link_noticia, texto_noticia = get_corpo_materias(html_bruto, url_inicio, tempo_espera)
    
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


# Só que tudo isso vira um loop pra baixar as notícias todas

# Faltou montar o pipelina para várias matérias

pode_ou_nao, delay = checar_permiss(url, nome_agente, terminacao)
caminho_snapshot = Path("data/raw/dengue_chik_snapshot.html")
html_snap = caminho_snapshot.read_text(encoding="utf-8")

noticias = get_corpo_materias(html_snap, url, delay)

# E vai salvando as matérias para exibir em DataFrame e contar as palavras
arquivo_destino_csv = r".\data\processed\news.csv"
arquivo_destino_txt = r".\data\processed\news_texto.txt"

gravar_csv_noticias(noticias, arquivo_destino_csv)                                                          # Salva as notícias em csv
gravar_txt_noticias(noticias, arquivo_destino_txt)                                                          # Parâmetros: news_dici_or_csv, arquivo_destino, from_dici=True
# Rebece o dicionario de get_corpo_materias ou trabalha com um DataFrame lendo do csv de notícias salvo
# Exemplo de chamada por csv: gravar_txt_noticias(r".\data\processed\news_novo.csv", r".\data\processed\news_texto.txt", from_dici=False)


# Alterar nome do arquivo para news_agg (agregar)
# def txt_news_from(noticias=None):    
#     try:        
#         # Gravar a partir do dicionario retornado pela função coletar_news
#         gravar_txt_noticias(noticias)
    
#     except:        
#         # Gravar o txt a partir do csv
#         print("Dicionário não foi passado, lendo a partir do csv em '.\data\processed\news_novo.cs'")
#         gravar_txt_noticias(r".\data\processed\news_novo.csv", r".\data\processed\news_texto.txt", from_dici=False)