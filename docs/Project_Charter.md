# Project Charter — Painel de Chikungunya no Recife

## Contexto

Dados públicos de saúde ajudam a entender onde os casos de uma doença ocorrem e quais localidades precisam de maior atenção. Este projeto utiliza dados da Prefeitura do Recife para explorar a ocorrência de chikungunya por bairro e ano, com atenção às hospitalizações e aos óbitos entre os casos confirmados.

O projeto está relacionado ao **Objetivo de Desenvolvimento Sustentável 3 — Saúde e Bem-Estar**.

## Objetivo

Construir um painel interativo que ajude a identificar bairros do Recife com maior ocorrência de chikungunya e maior proporção de hospitalizações, apoiando a exploração dos dados por gestores, profissionais de saúde e demais interessados.

Na perspectiva de **Ciência de Dados**, os registros de chikungunya e os dados populacionais sustentam visualizações que ajudam a identificar bairros prioritários.
A IA interpreta os indicadores, e a engenharia de prompts orienta o agente a usar dados agregados e explicitar os limites da análise.
As tabelas e os filtros sugeridos permitem conferir os achados e usá-los no planejamento do enfrentamento da doença no Recife.

## Público e responsáveis

- **Público:** gestores de saúde, profissionais de saúde e pessoas interessadas nos dados.
- **Desenvolvimento e documentação:** estudante responsável pelo projeto.
- **Orientação e avaliação acadêmica:** professor da disciplina.

## Dados utilizados

- Registros de chikungunya obtidos pela API de dados abertos da Prefeitura do Recife.
- Dados populacionais por bairro referentes ao Censo 2022.
- Notícias coletadas no site da Fiocruz pelos termos “dengue” e “chikungunya”.

A análise considera os casos confirmados de chikungunya no período de **2017 a 2025**. Os anos de 2015 e 2016 são excluídos devido à quantidade de registros sem identificação do bairro. Registros sem bairro não participam das análises por localidade.

## Escopo

O projeto inclui:

- Apresentação da origem, dos conceitos e do tratamento dos dados.
- Ranking de bairros e mapa de calor com filtros compartilhados, além da evolução anual com seleção de bairros.
- Assistente na página **Análises** para consultar indicadores, esclarecer métricas ambíguas e interpretar resultados.
- Tabelas de evidências e sugestões de filtros para aplicação manual.
- Exibição de notícias da Fiocruz.
- API própria para disponibilizar consultas aos dados.

A aplicação usa Python e Streamlit. O assistente acessa o modelo pela API da Groq e executa as agregações em Python. A API própria do painel, implementada em FastAPI, disponibiliza consultas aos dados.

## Indicadores

O painel utiliza:

- Total de casos confirmados.
- Incidência de casos por 100 mil habitantes.
- Total de hospitalizações.
- Percentual de casos confirmados com hospitalização.
- Total de óbitos pelo agravo.
- Letalidade entre os casos confirmados (%).

Hospitalizações e óbitos ajudam a observar a gravidade dos casos registrados. O total de casos e a incidência mostram a ocorrência da doença e devem ser analisados em conjunto com os demais indicadores.

## Uso de inteligência artificial

O assistente da página **Análises** acessa o modelo **GPT-OSS 20B** por meio da **API da Groq**.
O agente envia as requisições ao [endpoint de chat da Groq](https://api.groq.com/openai/v1/chat/completions).
Ele consulta rankings e séries anuais, com parâmetros validados e cálculos
compartilhados com os gráficos. Quando a métrica é ambígua, o usuário pode
esclarecer qual indicador deseja consultar.

O especialista epidemiológico interpreta os agregados para profissionais
de saúde e gestores públicos. Ele distingue a prioridade inicial de
vigilância territorial, orientada pela incidência, da avaliação de
demanda assistencial, orientada pelo volume de casos e complementada
por dados de atendimento. A resposta pode incluir referências oficiais
e indica os limites do recorte.

O painel valida as referências numéricas usadas pelo modelo, apresenta as
tabelas de evidências e sugere filtros para conferir a resposta. Quando a
interpretação da Groq falha ou não passa na validação, o painel pode gerar
uma leitura a partir dos resultados disponíveis. [Implementação do agente](../readme.md#implementação-do-agente)

## Fora do escopo

O projeto não inclui:

- Diagnóstico ou orientação clínica individual.
- Previsão de surtos.
- Identificação de pacientes.
- Demonstração das causas das diferenças entre bairros.
- Substituição da avaliação de profissionais e gestores de saúde.

## Critérios de sucesso

O projeto será considerado concluído quando:

- As páginas previstas estiverem disponíveis e funcionando.
- Os filtros permitirem explorar bairros e anos e alcançar as principais comparações em até quatro interações.
- Os indicadores apresentados corresponderem aos cálculos realizados sobre a base tratada.
- O assistente responder com base nos resultados das consultas e indicar filtros que reproduzam o recorte.
- A avaliação dos modelos registrar qualidade das respostas, tempos e recursos utilizados.
- A documentação explicar as fontes, os critérios de tratamento, as limitações e os passos de execução.

## Riscos e limitações

- Campos ausentes ou preenchidos incorretamente podem afetar os resultados.
- A exclusão de registros pode reduzir a representatividade da análise.
- A população de 2022 é utilizada como referência para diferentes anos, o que limita a interpretação da incidência.
- As informações refletem os registros disponíveis na base, não necessariamente todos os casos ocorridos.
- A LLM pode produzir respostas incorretas, mesmo quando recebe os dados necessários.
- A inferência na Groq depende de conexão com a internet, chave de API e disponibilidade do serviço. A pergunta e os resultados agregados usados na interpretação são enviados à Groq.
- Mudanças ou indisponibilidade das fontes podem prejudicar a atualização dos dados.

## Etapas de desenvolvimento

O desenvolvimento acompanha os cinco trabalhos práticos da disciplina, com entregas progressivas:

1. Definição do problema, do público e das fontes.
2. Coleta, exploração e tratamento dos dados.
3. Construção do painel, dos filtros e dos indicadores.
4. Avaliação e integração da LLM e disponibilização da API.
5. Validação final, revisão da documentação e apresentação do projeto.