# Data Summary Report

## Fontes

* A fonte de dados serão os arquivos dispoíveis em https://dados.recife.pe.gov.br/sv/dataset/casos-de-dengue-zika-e-chikungunya, que compreendem o registro de casos confirmados de chikungunya no período compreendido entre 2015 e 2025. Neste momento, a aplicação carrega por padrão os dados de 2025, salvos em csv. O usuário pode anexar um arquivo referente a outro ano da série histórica para visualizar o conteúdo a partir dos dados ali contidos.

* API para população (da prefeitura)

* Página da EBC para scraping

## Características dos dados

Os dados estão na forma de arquivos csv, são, portando estrutudados.
Para nossa análise as colunas utilizadas serão: 

* NU_NOTIFIC (Numérica, inteira, identifica o número do reporte)
* NU_ANO (Númerica, 4 dígitos, identifica o ano do reporte)
* DT_NASC (DD/MM/AAAA - data de nascimento do paciente)
* CS_SEXO (categórica - M, F - sexo do paciente)
* CS_ESCOL_N (numérica, inteiro, representa o grau de escolaridade do paciente)
* NM_BAIRRO (textual, nome do bairro de residência do paciente)
* ~~DT_OBITO (data de óbito do paciente, 5 dígitos, formato excel númerico - inteiro - para datas)~~ coluna é substituída pela coluna 'EVOLUCAO'
* CLASSI_FIN, (numérica, inteiro, representa a classificação final em relação à doença)

Para o escopo da análise são imprescindíveis as colunas NU_ANO e NM_BAIRRO. ~~e DT_OBITO~~.
A coluna NU_NOTIFIC é mantida para identificar cada registro
As demais colunas são mantidas para trazer indicadores sócio-demográficos mínimos dos pacientes. Pode ser utilizadas em próximas iterações do projeto.

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

[tabela de dados]("https://portalsinan.saude.gov.br/images/documentos/Agravos/Dengue/DIC_DADOS_ONLINE.pdf?utm_source=chatgpt.com")<br>
***https://portalsinan.saude.gov.br/images/documentos/Agravos/Dengue/DIC_DADOS_ONLINE.pdf?utm_source=chatgpt.com***

* HOSPITALIZ (Numérica, inteira, identifica se houve hospitalização / 1-Sim 2-Não 9-Ignorado)
* CLASSI_FIN (5-Descartado,
10-Dengue,
11-Dengue com sinais de alarme,
12-Dengue grave,
13-Chikungunya)


[Outro doc - SINAN ?]("https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SINAN/Dengue/dic_dados_dengue.pdf")<br>
Classificação final
‘ ‘, 0 , 9 Ignorado
1 Confirmado
2 Descartado
8 Inconclusivo