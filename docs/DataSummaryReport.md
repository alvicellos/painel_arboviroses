# Data Summary Report

## Fontes

* ~~A fonte de dados serão os arquivos dispoíveis em https:\//dados.recife.pe.gov.br/sv/dataset/casos-de-dengue-zika-e-chikungunya, que compreendem o registro de casos confirmados de chikungunya no período compreendido entre 2015 e 2025. Neste momento, a aplicação carrega por padrão os dados de 2025, salvos em csv.~~ 

* Os dados estão sendo carregaos via API, a partir do endpoint https://dados.recife.pe.gov.br/api/action/, compreendendo o registro de casos confirmados de chikungunya no período compreendido entre 2015 e 2025.

* O usuário pode anexar um arquivo referente a algum ano da série histórica para realizar uma análise exclusiva a partir do conteúdo ali contido. (Sugestão é trazer dados de outras localidades, desque que no formato indicado)

* API geográfica da Prefeitura do Recife, em: https://esigportal2.recife.pe.gov.br/arcgis/rest/services/Hosted/Bairros_Censo2022_final/FeatureServer, com dados de população colhidos no censo de 2002, já agregados por bairro.

* ~~Página da EBC para scraping, https:\//busca.ebc.com.br/?site_id=agenciabrasil&q=dengue%20chikungunya, pesquisa de notícias provenientes de diferentes agências, resultado da consulta pelos termos 'dengue chikunghunya'. O robots.txt em https:\//busca.ebc.com.br não permite a coleta.~~ Página da [EBC](https://agenciabrasil.ebc.com.br/) para scraping, notícias coletadas das seções de assuntos.

## Características dos dados

~~Os dados estão na forma de arquivos csv~~ Os dados extraídos da API são estrutudados.  
Com a coleta via API, diferentemente da carga por _csv_, apenas as colunas de interesse são extraídas:

* ~~NU_NOTIFIC (Numérica, inteira, identifica o número do reporte) ?????~~
* NU_ANO (Númerica, 4 dígitos, identifica o ano do reporte)
* DT_NASC (DD/MM/AAAA - data de nascimento do paciente)
* CS_SEXO (categórica - M, F - sexo do paciente)
* CS_ESCOL_N (numérica, inteiro, representa o grau de escolaridade do paciente)
* NM_BAIRRO (textual, nome do bairro de residência do paciente)
* ~~DT_OBITO (data de óbito do paciente, 5 dígitos, formato excel númerico - inteiro - para datas)~~ coluna é substituída pela coluna 'EVOLUCAO'
* CLASSI_FIN, (numérica, inteiro, representa a classificação final em relação à doença)

Sendo necessário incluir mais colunas na análise, basta acrescentá-las na lista da função que consulta a API.Para o escopo da análise são imprescindíveis as colunas NU_ANO e NM_BAIRRO. ~~e DT_OBITO. A coluna NU_NOTIFIC é mantida para identificar cada registro.~~ A coluna **CLASSI_FIN** é estritamente necessária, pois confirma se a causa do estado do paciente realmente foi a doença: (5-Descartado
10-Dengue
11-Dengue com
sinais de alarme
12-Dengue grave
13-Chikungunya
). Para efeitos de consistência, os registros com `CLASSI_FIN = 5` são excluídos da análise, garantindo que apenas casos confirmados da doença são considerados.  
~~Avaliar ao final se vamos incluir apenas 13 ou alargar a análise incluindo comparações com resultados positivos para dengue.~~
~~As referências às demais colunas (tachadas), neste momento, são mantidas na documentação com a intenção de trazer indicadores sócio-demográficos mínimos dos pacientes em iterações futuras do projeto.~~

Agora csv é apenas o fornecido pelo usuário.

## Transformações

~~A coluna DT_OBITO é convertida de int para data na coluna (DT_OBITO_FORM).~~
<br>Agregação com pandas gerando as seguintes colunas para análise:

* TOTAL_CASOS (Numérica, inteiro, quantidade total de casos reportados e confirmados)
* TOTAL_HOSPITALIZACOES (Numérica, inteiro, total de hospitalizações entre os casos confirmados)
* TOTAL_OBITOS (Numérica, inteiro, total de óbitos entre os casos confirmados)

## Agregações

#### ANÁLISE + POPULAÇÂO (COLETADO)

A contagem do total de casos por bairro é calculada e registrada na coluna 'TOTAL_CASOS_BAIRRO'<br>
Uma tabela derivada é criada a partir da filtragem dos dados iniciais, contendo apenas as instâncias que apresentam óbito do paciente (representada pela presença de valor em DT_OBITO_FORM).<br>
A relaçaõ entre o número total de casos e o números de óbitos é calculada e registrada na coluna OBT_POR_CASOS.


Nos dados da prefeitura (chikungunya):


[Dicionário de dados:](https://portalsinan.saude.gov.br/images/documentos/Agravos/Dengue/DIC_DADOS_ONLINE.pdf)
https\://portalsinan.saude.gov.br/images/documentos/Agravos/Dengue/DIC_DADOS_ONLINE.pdf

<!-- Link quebrado para exibição correta no VSCode -->

* HOSPITALIZ (Numérica, inteira, identifica se houve hospitalização / 1-Sim 2-Não 9-Ignorado)
* CLASSI_FIN (5-Descartado,
10-Dengue,
11-Dengue com sinais de alarme,
12-Dengue grave,
13-Chikungunya)

[Outro doc - SINAN ?](https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SINAN/Dengue/dic_dados_dengue.pdf)  
Classificação final
‘ ‘, 0 , 9 Ignorado
1 Confirmado
2 Descartado
8 Inconclusivo


<!-- dá pra escrever comentários no markdown, se a gente quiser
```python
def funcao_python():
    return 2 + 2
```
-->