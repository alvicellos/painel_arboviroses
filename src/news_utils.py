#import requests
#from urllib.robotparser import RobotFileParser
#from bs4 import BeautifulSoup as bs
#from pathlib import Path
#import re
#import time
from pathlib import Path
from src.get_news import check_robots, get_snapshot, get_materias, gravar_csv_noticias

url = "https://agenciabrasil.ebc.com.br"
nome_agente = "INFNET-TESTEPB-IA/1.0 (material didatico; contato: marcelo.aalves@al.infnet.edu.br)"
terminacao = "saude"

def checar_permiss(endereco, agente, fim_url):    
    permissoes, tempo_espera = check_robots(url, nome_agente, [terminacao])    # lista    
    return permissoes, tempo_espera

def gravar_snapshot(permissoes, agente, tempo_espera):    
    get_snapshot(permissoes, agente, tempo_espera)

def coletar_news(html_bruto, url_inicio, tempo_espera):
    nome_noticia, link_noticia, texto_noticia = get_materias(html_bruto, url_inicio, tempo_espera)

pode_ou_nao, delay = checar_permiss(url, nome_agente, terminacao)

caminho_snapshot = Path("data/raw/dengue_chik_snapshot.html")
html_snap = caminho_snapshot.read_text(encoding="utf-8")

noticias = get_materias(html_snap, url, delay)
gravar_csv_noticias(noticias)