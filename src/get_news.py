import requests
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup as bs
from pathlib import Path
import pandas as pd
import re
import time

url = "https://agenciabrasil.ebc.com.br"
nome_agente = "INFNET-TESTEPB-IA/1.0 (material didatico; contato: marcelo.aalves@al.infnet.edu.br)"
terminacao = "saude"

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
    print(f"O tempo de espera 'crawl_delay' deve ser de {delay} segundos.")
                
    return urls_permissoes, delay


def get_snapshot(sites_permissoes, agente, espera):
    ''' Verifica as permissões do site, e salva o snapshot do html'''
    
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

            destino.write_text(resposta.text, encoding="utf-8")                                 
            print(f"Snapshot salvo com sucesso em: {destino}")
        
            time.sleep(espera)

#permissoes, tempo_espera = check_robots(url, nome_agente, ["saude"])
#get_snapshot(permissoes, nome_agente, tempo_espera)
#time.sleep(tempo_espera)

def get_materias(pagina_coletada_html, url_base, espera):
    '''
    Lê o html salvo do snapshop e coleta:
    -os títulos
    -links e
    -textos
    de cada matéria
    '''    
    sopa = bs(pagina_coletada_html, "html.parser")
    
    news = []
    
    titulos = []
    links = []    
    materias = []
    horarios_origem = []

    noticias = sopa.select('a.titulo-noticia')
    print(f"\nTotal de noticias encontrados: {len(noticias)}")
    for i, tag in enumerate(noticias, 1):
        titulo = tag.get_text().strip()
        link = r'https://agenciabrasil.ebc.com.br' + tag['href']
        #titulos.append(titulo)
        #links.append(link)               
        
        #for index, noticia in enumerate(links):        
        print(f'{i} - Consultando matéria: "{titulo}"\n  {link}...') 
        resposta_link = requests.get(link)              
        
        if 200 <= resposta_link.status_code < 300:            
            sopa_news = bs(resposta_link.text, "html.parser")                      
            titulo_materia = sopa_news.select('h1.titulo-materia')
            for i, tag in enumerate(titulo_materia, 1):
                    titulo = tag.get_text().strip()        
                    
            texto_materia = sopa_news.select("div.conteudo-noticia p")       
            
            materia_corrida = []
            for i, tag in enumerate(texto_materia, 1):                        
                corpo_bruto = tag.get_text().strip()
                #corpo_limpo = corpo_bruto.strip().replace('\r', ' ').replace('\n', '')
                corpo_limpo = re.sub(r"\s+", " ", corpo_bruto.replace("\xa0", " ")).strip()
                materia_corrida.append(corpo_limpo)
                
            texto_materia = " ".join(materia_corrida)
            dados_news = {'titulo': titulo, 'link': link, 'texto_materia' : texto_materia}
            news.append(dados_news)            
            time.sleep(espera)        
        else:
            print(f"Status code: {resposta_link.status_code}")
            if tag != noticias[-1]:
                print("Seguindo para a matéria seguinte...")
            time.sleep(espera)
            continue
    
    return news

def gravar_csv_noticias(materias_composto):
    """ df_news = pd.DataFrame({
        "titulo_noticia": headers,
        "link_materia": enderecos,
        "texto_materia": textos
    }) """
    
    df_news = pd.DataFrame(materias_composto)
    
    df_news.to_csv(
        r".\data\processed\news_novo.csv", index=False
        )

def gravar_txt_noticias(header, endereco, texto):
    #titulo_noticia,resumo_materia,hora_publi_origem
    "oi"
    
""" caminho_snapshot = Path("data/raw/dengue_chik_snapshot.html")
html_bruto = caminho_snapshot.read_text(encoding="utf-8")

url_inicio = 'https://agenciabrasil.ebc.com.br/'
nome_noticia, link_noticia, texto_noticia = get_materias(html_bruto, url_inicio, tempo_espera)

gravar_csv_noticias(nome_noticia, link_noticia, texto_noticia) """