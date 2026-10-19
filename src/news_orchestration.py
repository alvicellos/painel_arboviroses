from news_get import check_robots, get_snapshot_html, get_corpo_materias, gravar_csv_noticias, gravar_txt_noticias

url = "https://agenciabrasil.ebc.com.br"
nome_agente = "INFNET-TESTEPB-IA/1.0 (material didatico; contato: marcelo.aalves@al.infnet.edu.br)"
terminacao = ["educacao", "saude", "geral"]

def collect_news(url, nome_agente, terminacoes: list) -> dict:     
    toda_coleta_noticias = []
    #for terminacao in terminacoes:        
    permissoes, tempo_espera = check_robots(url, nome_agente, terminacoes)       # check_robots contém loop                
    url_html = get_snapshot_html(permissoes, nome_agente, tempo_espera)          
    for url, html in url_html.items():
        print(f"Assunto (terminação): ")        
        noticias = get_corpo_materias(html, tempo_espera)                        # falta imprimir o título # tem que baixar a página se não retorna código 500 a partir da 5ª matéria
        print("Notícias:\n", noticias)
        for noticia in noticias:
            toda_coleta_noticias.append(noticia)                
    
    return toda_coleta_noticias

news = collect_news(url, nome_agente, terminacao)                                 # Retorna o dicionário contendo titulo_noticia,resumo_materia,hora_publi_origem
if news:                                                                          # Se a coleta não retornar vazia
    gravar_csv_noticias(news, r'data\processed\news.csv')                         # Grava em csv
    gravar_txt_noticias(news, r'data\processed\news_texto.txt')                   # Grava em txt
else:
    print("A coleta de notícias retornou vazia. Verifique o pipeline.")
    