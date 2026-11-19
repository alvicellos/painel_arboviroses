# Project Charter — Painel de Chikungunya no Recife

## Contexto

Dados públicos de saúde ajudam a entender onde os casos de uma doença ocorrem e quais localidades precisam de maior atenção. Este projeto utiliza dados da Prefeitura do Recife para explorar a ocorrência de chikungunya por bairro e ano, com atenção às hospitalizações e aos óbitos entre os casos confirmados.

O projeto está relacionado ao **Objetivo de Desenvolvimento Sustentável 3 — Saúde e Bem-Estar**.

## Objetivo

Construir um painel interativo que ajude a identificar bairros do Recife com maior ocorrência de chikungunya e maior proporção de hospitalizações, apoiando a exploração dos dados por gestores, profissionais de saúde e demais interessados.

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
- Filtros para explorar registros por bairro e ano.
- Tabelas e indicadores para comparar localidades e períodos.
- Interação com uma LLM local para responder perguntas sobre os dados.
- Tabelas de conferência para verificar as respostas do modelo.
- Exibição de notícias da Fiocruz.
- API própria para disponibilizar consultas aos dados.

A aplicação será desenvolvida em Python, com interface em Streamlit. A interação com a LLM será executada localmente, conforme a disponibilidade do modelo e dos recursos da máquina.

## Indicadores

O painel utiliza:

- Total de casos confirmados.
- Incidência de casos por 100 mil habitantes.
- Total de hospitalizações.
- Percentual de casos confirmados com hospitalização.
- Total de óbitos pelo agravo.

Hospitalizações e óbitos ajudam a observar a gravidade dos casos registrados. O total de casos e a incidência mostram a ocorrência da doença e devem ser analisados em conjunto com os demais indicadores.

## Uso de inteligência artificial

O modelo **Qwen3-0.6B** será utilizado para responder perguntas em português sobre os dados disponíveis.

A aplicação seleciona os registros relacionados ao bairro ou ano informado e fornece esse recorte ao modelo. O usuário pode conferir a resposta nas tabelas e nos filtros da própria página.

O modelo foi escolhido a partir de testes de qualidade das respostas, tempo de execução e recursos computacionais. As respostas podem conter erros e precisam ser verificadas antes de qualquer uso em decisões.

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
- A interação com a LLM funcionar localmente e permitir a conferência dos dados utilizados.
- A avaliação dos modelos registrar qualidade das respostas, tempos e recursos utilizados.
- A documentação explicar as fontes, os critérios de tratamento, as limitações e os passos de execução.

## Riscos e limitações

- Campos ausentes ou preenchidos incorretamente podem afetar os resultados.
- A exclusão de registros pode reduzir a representatividade da análise.
- A população de 2022 é utilizada como referência para diferentes anos, o que limita a interpretação da incidência.
- As informações refletem os registros disponíveis na base, não necessariamente todos os casos ocorridos.
- A LLM pode produzir respostas incorretas, mesmo quando recebe os dados necessários.
- A execução local depende de memória disponível, instalação das bibliotecas e download dos pesos.
- Mudanças ou indisponibilidade das fontes podem prejudicar a atualização dos dados.

## Etapas de desenvolvimento

O desenvolvimento acompanha os cinco trabalhos práticos da disciplina, com entregas progressivas:

1. Definição do problema, do público e das fontes.
2. Coleta, exploração e tratamento dos dados.
3. Construção do painel, dos filtros e dos indicadores.
4. Avaliação e integração da LLM e disponibilização da API.
5. Validação final, revisão da documentação e apresentação do projeto.