# Data Summary Report

## Fontes

* Os registros de chikungunya de 2015 a 2025 são coletados pela API de dados abertos da Prefeitura do Recife, a partir de https://dados.recife.pe.gov.br/api/action/. A coleta seleciona os recursos referentes a chikungunya e salva os dados em `data/processed/data_series.json`, utilizado no carregamento da aplicação.

* A população por bairro vem do **Censo 2022**, consultado pela API geográfica da Prefeitura do Recife. Se a consulta falhar, a aplicação usa o cache `data/processed/populacao_2022.json`. [Serviço geográfico da Prefeitura](https://esigportal2.recife.pe.gov.br/arcgis/rest/services/Hosted/Bairros_Censo2022_final/FeatureServer)

* As notícias são coletadas no site da **Fiocruz**, pela busca dos termos **dengue** e **chikungunya**. Elas complementam a apresentação do tema e não entram no cálculo dos indicadores epidemiológicos.

## Características dos dados

Os dados de casos são estruturados. Na coleta pela API, são selecionadas as colunas de interesse:

* `NU_NOTIFIC`: número da notificação.
* `NU_ANO`: ano da notificação.
* `DT_NASC`: data de nascimento do paciente.
* `CS_SEXO`: código do sexo do paciente.
* `NM_BAIRRO`: bairro de residência do paciente.
* `HOSPITALIZ`: informação sobre hospitalização.
* `EVOLUCAO`: evolução do caso, utilizada para identificar óbitos pelo agravo.
* `CLASSI_FIN`: classificação final em relação à doença.

As diferenças nos nomes das colunas dos arquivos mais antigos são padronizadas na coleta.

Para a análise por localidade, são necessários o ano e o bairro. O código `13` na classificação final identifica os casos de chikungunya.

## Transformações

* Exclusão dos anos de **2015 e 2016**, devido à quantidade de registros sem identificação do bairro, o que prejudicaria a análise.
* Exclusão de classificações vazias e dos códigos `1`, `2`, `5`, `8`, `10`, `11` e `12`, conforme o tratamento implementado para manter o recorte de chikungunya.
* Exclusão dos registros sem bairro antes das agregações por localidade.
* Contagem de hospitalizações pelo código `HOSPITALIZ == 1` e de óbitos pelo agravo pelo código `EVOLUCAO == 2`.

O período utilizado nas análises é de **2017 a 2025**. Os campos ignorados ou sem informação não são contabilizados como hospitalizações ou óbitos confirmados, mas também não comprovam a ausência desses eventos.

## Agregações

Os registros são agregados com pandas por bairro e ano, gerando:

* `TOTAL_CASOS`: quantidade de casos no recorte tratado.
* `TOTAL_HOSPITALIZACOES`: total de hospitalizações entre esses casos.
* `TOTAL_OBITOS`: total de óbitos pelo agravo entre esses casos.

### Análise com dados de população

Os dados agregados são associados à população pelo nome do bairro, com padronização de letras maiúsculas e remoção de acentos para a junção. São calculadas as colunas:

* `POPULACAO`: população do bairro no Censo 2022.
* `INCIDENCIA_100K`: `TOTAL_CASOS / POPULACAO * 100.000`.
* `PERC_CASOS_HOSP`: `TOTAL_HOSPITALIZACOES / TOTAL_CASOS * 100`.

A população de 2022 é utilizada como referência para todos os anos, o que limita a comparação da incidência ao longo do tempo. Nas próximas atualizações serão utilizadas projetos do IBGE para os demais anos.

### Indicadores e visualizações

- **Ranking de bairros.** Agrega os totais por bairro no período selecionado.
  Além dos totais e do percentual de hospitalização, apresenta incidência
  por 100 mil habitantes e **letalidade**, calculada como
  `TOTAL_OBITOS / TOTAL_CASOS * 100`. A incidência no ranking usa o total
  do período e a população de referência do bairro.
- **Mapa de calor.** Exibe os mesmos bairros do ranking e mostra a posição
  de cada um no ranking geral de cada indicador do período.
- **Evolução anual.** Exibe o total de casos e o percentual de hospitalização
  por ano. Quando há seleção de bairros, os valores representam o conjunto
  selecionado.

## Uso dos dados pelo assistente e pela API

O assistente da página **Análises** consulta os dados tratados e usa as mesmas
funções de agregação dos gráficos. A Groq recebe a pergunta, o contexto da
consulta e os resultados agregados. O painel exibe as tabelas e sugere os
filtros para reproduzir o recorte nos gráficos. [Implementação do agente](../readme.md#implementação-do-agente)

A API de dados oferece uma amostra, uma consulta por ano e uma consulta com
indicadores por bairro. A amostra e a consulta por ano leem a série bruta e
retêm registros com os campos preenchidos. A consulta de indicadores por
bairro usa a base tratada e devolve como `null` os indicadores sem dados
suficientes para cálculo.

## Coleta de notícias

A coleta é executada separadamente da interface, pelo script `src/news_orchestration.py`, com funções de `src/news_get.py`.

O processo consulta o `robots.txt`, verifica as permissões de acesso e considera o intervalo de espera informado pelo site. Requests obtém o HTML, e BeautifulSoup extrai títulos, links e textos de até **15 notícias da página de resultados consultada**, sem percorrer todas as páginas da busca.

O HTML da busca é salvo em `data/raw`. Os resultados são gravados em `data/processed/news.csv` e `data/processed/news_texto.txt`, preservando a versão anterior com o sufixo `_old`.

A página **Notícias** lê esses arquivos para apresentar matérias, links, trechos e frequência de palavras. Abrir a página não inicia uma nova coleta. Mudanças na estrutura do site podem exigir ajustes nos seletores de extração.

## Referência dos códigos

* `HOSPITALIZ`: `1` — Sim; `2` — Não; `9` — Ignorado.
* `EVOLUCAO`: `2` — Óbito pelo agravo.
* `CLASSI_FIN`: `5` — Descartado; `10` — Dengue; `11` — Dengue com sinais de alarme; `12` — Dengue grave; `13` — Chikungunya.

[Dicionário de dados do SINAN](https://portalsinan.saude.gov.br/images/documentos/Agravos/Dengue/DIC_DADOS_ONLINE.pdf).
