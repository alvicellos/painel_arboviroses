# 🦟 Painel de Chikungunya no Recife

Aplicação para explorar casos confirmados de chikungunya por bairro e ano, consultar indicadores com o assistente da página **Análises** e acompanhar notícias da Fiocruz.

## ▶️ Rodar o app localmente

Na pasta raiz do projeto, crie e ative o ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências e inicie a aplicação:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Acesse **http://localhost:8501**. Mantenha os arquivos de dados na pasta `data/processed`.

## Usar o assistente de Análises

Crie uma chave na [Groq Console](https://console.groq.com/keys). Na raiz do
projeto, crie ou edite o arquivo `.env` e preencha `GROQ_API_KEY`.

```dotenv
GROQ_API_KEY=
```

O Git ignora o `.env`. Uma chave definida no ambiente tem prioridade sobre a
do arquivo. Se o ambiente virtual já existia, execute
`python -m pip install -r requirements.txt` para atualizar as dependências.

Na página **Análises**, abra **Assistente de análise**, escreva uma pergunta
e clique em **Consultar dados**. Por exemplo, “Quais são os três bairros com
maior incidência entre 2020 e 2022?”. Se a métrica for ambígua, escolha uma
das opções que o assistente apresentar. Use a tabela e os filtros sugeridos
para conferir a resposta nos gráficos. A aplicação dos filtros é manual.

## Implementação do agente

1. **Coordenação.** [`src/agente_analises.py`](src/agente_analises.py)
   usa regras locais para consultas explícitas. Nas demais, o modelo
   `openai/gpt-oss-20b` propõe ações em JSON e o Pydantic valida a estrutura.
   O coordenador valida métricas, bairros e anos antes de executar as
   consultas e consolida rankings equivalentes.
2. **Ferramentas de agregação.** [`src/metricas_analises.py`](src/metricas_analises.py)
   calcula rankings e séries anuais com Pandas. Os gráficos usam as mesmas
   funções. Os filtros sugeridos são derivados das consultas executadas
   para que o usuário possa reproduzir cada recorte.
3. **Interpretação epidemiológica.**
   [`src/especialista_epidemiologico.py`](src/especialista_epidemiologico.py)
   distingue a prioridade inicial de vigilância territorial, baseada na
   incidência, da atenção à demanda assistencial, baseada no volume de
   casos registrados. A leitura indica quando a comparação se limita aos
   bairros exibidos e referencia diretrizes oficiais quando pertinente.
4. **Verificação dos valores.** O modelo redige a leitura com marcadores
   de fatos. O Python valida os marcadores e insere os valores e suas
   unidades. Se a leitura não passar na validação após uma tentativa de
   correção ou se a Groq falhar na interpretação, o painel exibe uma
   leitura calculada a partir dos resultados disponíveis.

O [cliente da Groq](src/modelo_groq.py) é chamado pelo Streamlit. A inferência
requer internet e envia à Groq a pergunta, o contexto necessário à consulta
e os resultados agregados. Os cálculos ocorrem localmente. Para usar o
assistente, basta iniciar o Streamlit com a chave configurada.

## 🔌 Rodar a API

Com o ambiente virtual ativo, instale as dependências da API e inicie o
servidor em outro terminal na raiz do projeto.

```powershell
python -m pip install -r requirements-api.txt
python -m uvicorn api.main:app --reload
```

Acesse **http://127.0.0.1:8000/docs** para consultar e testar as rotas.

## 📰 Atualizar as notícias

A coleta busca notícias da Fiocruz pelos termos **dengue** e **chikungunya**. Para executá-la:

```powershell
python src/news_orchestration.py
```

Os resultados são salvos em `data/processed/news.csv` e `news_texto.txt`. A página **Notícias** utiliza esses arquivos.

Antes da coleta, confira se `get_corpo_fiocruz`, em `src/news_get.py`, utiliza o HTML recebido pela função, sem depender de um caminho fixo de outra máquina.

## 📊 Fontes e documentação

Os dados de casos são obtidos pela API da Prefeitura do Recife, e os indicadores populacionais utilizam o Censo 2022.

A descrição do projeto e os critérios de tratamento estão na pasta `docs`.
