import requests
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup as bs
from pathlib import Path
import pandas as pd
import re
import time
import os

def check_robots(site, agente, terminacoes):
    # 1. Definir o site e um User-Agent transparente com identificação e contato
    SITE = site
    AGENTE = agente

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


def get_snapshot_html(sites_permissoes, agente, espera):
    ''' Verifica as permissões do site, salva o snapshot do html e retorna o html para extração das notícias
        Retorna um dicionário: {url : html}
    '''
    
    url_html = {}
    
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
            # destino = Path("data/raw/dengue_chik_snapshot.html")
            destino = Path(f"data/raw/{site.split("/")[-1]}.html")
            destino.parent.mkdir(parents=True, exist_ok=True)

            destino.write_text(resposta.text, encoding="utf-8")                                 
            print(f"Snapshot salvo com sucesso em: {destino}")
        
            time.sleep(espera)
            
            url_html[site] = resposta.text 
            
    return url_html

def get_corpo_materias(pagina_coletada_html, espera):
    
    # Adicionar WAITs
    
    '''
    
    Lê o html salvo do snapshop e coleta:
        -os títulos
        -links e
        -textos;
        
        de cada matéria (entra no link de cada matéria)
    
    '''    
    sopa = bs(pagina_coletada_html, "html.parser")
    
    news = []
    #horarios_origem = []

    noticias = sopa.select('a.titulo-noticia')
    print(f"\nTotal de noticias encontradas: {len(noticias)}")
    for i, tag in enumerate(noticias, 1):    
        titulo = tag.get_text().strip()
        link = r'https://agenciabrasil.ebc.com.br' + tag['href']
        
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

def gravar_csv_noticias(dicionario_materias, arquivo_destino):                                          
    df_news = pd.DataFrame(dicionario_materias)    
    arquivo_old = r".\data\processed\news_old.csv"
    if os.path.exists(arquivo_old):
        os.remove(arquivo_old)
    if os.path.exists(arquivo_destino):
        os.rename(arquivo_destino, arquivo_old)    
    df_news.to_csv(
        arquivo_destino, index=False
        )
    print("CSV salvo !")

def gravar_txt_noticias(news_dici_or_csv, arquivo_destino, from_dici=True):    
    ''' 
    Recebe o dicionario de get_corpo_materias ou trabalha com um DataFrame lendo do csv de notícias salvo
    Exemplo de chamada por csv: gravar_txt_noticias(r".\data\processed\news_novo.csv", r".\data\processed\news_texto.txt", from_dici=False)
    '''
    if from_dici:
        df_news = pd.DataFrame(news_dici_or_csv)
    else:
        df_news = pd.read_csv(news_dici_or_csv)
        print("Dicionário não foi passado, lendo a partir do csv salvo em '.\data\processed\news.csv'")
        
    arquivo_old = r".\data\processed\news_texto_old.txt"
    if os.path.exists(arquivo_old):
        os.remove(arquivo_old)
    if os.path.exists(arquivo_destino):
        os.rename(arquivo_destino, arquivo_old)       
        
    with open(arquivo_destino, "w", encoding="utf-8") as file_news:   
        for index, row in df_news.iterrows():            
            file_news.write(row['titulo'] + '\n' + row['texto_materia'])
            if index != len(df_news) - 1:
                file_news.write("\n")
    if from_dici:
        print("Notícias gravadas a partir da última coleta ('agora')")
    else:
        print("Notícias gravadas a partir do arquivo csv salvo em '.\data\processed\news.csv'")