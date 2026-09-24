import requests
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from pathlib import Path
import time

url = "https://duckduckgo.com/"
nome_agente = "INFNET-TESTEPB-IA/1.0 (material didatico; contato: marcelo.aalves@al.infnet.edu.br)"
terminacao = "?ia=news&origin=funnel_home_google&t=h_&q=dengue+chikungunya&iar=news"

def check_robots(site, agente, terminacoes):
    # 1. Definir o site e um User-Agent transparente com identificação e contato
    SITE = site
    AGENTE = nome_agente

    # 2. Obter o robots.txt do site
    url_robots = f"{SITE}/robots.txt"
    resposta = requests.get(url_robots, headers={"User-Agent": AGENTE})

    # 3. Instanciar o RobotFileParser e carregar as regras
    regras = RobotFileParser()
    regras.parse(resposta.text.splitlines())

    # 4. Checar permissão para rotas específicas
    
    urls_permissoes = {}
    
    for terminacao in terminacoes:
        url_checar = f"{SITE}/{terminacao}"
        print(url_checar, regras.can_fetch(AGENTE, url_checar))
        urls_permissoes[url_checar] = regras.can_fetch(AGENTE, url_checar)
        
    delay = regras.crawl_delay(AGENTE)
        
    return urls_permissoes, delay


def get_snapshot(sites_permissoes, agente, espera):
    
    for site in sites_permissoes:
        if sites_permissoes[site] == True:
            print(site)
            resposta = requests.get(site, headers={"User-Agent": agente}, timeout=30)               
            
            # 3. OBRIGATÓRIO: Verificar se a página respondeu com sucesso (200 OK)
            # Se houver erro 403, 404 ou 500, a exceção é levantada AQUI antes de salvar
            resposta.raise_for_status()

            # 4. Ajustar a codificação de caracteres
            resposta.encoding = resposta.apparent_encoding or "utf-8"

            # 5. Criar o caminho do arquivo em data/raw/ e gravar o texto do HTML
            destino = Path("data/raw/dengue_chik_snapshot.html")
            destino.parent.mkdir(parents=True, exist_ok=True)

            # Grava o HTML bruto no arquivo de texto/html
            with open(destino, "w", encoding="utf-8") as arquivo:
                arquivo.write(resposta.text)              
            
            #destino.write_text(resposta.text, encoding="utf-8")

            print(f"Snapshot salvo com sucesso em: {destino}")
        
            time.sleep(espera)       


url = "https://agenciabrasil.ebc.com.br"
nome_agente = "INFNET-TESTEPB-IA/1.0 (material didatico; contato: marcelo.aalves@al.infnet.edu.br)"
terminacao = "saude"

permissoes, delay = check_robots(url, nome_agente, ["saude"])
answer = get_snapshot(permissoes, nome_agente, delay)