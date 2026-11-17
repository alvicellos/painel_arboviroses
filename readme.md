# 🦟 Painel de Chikungunya no Recife

Aplicação para explorar casos confirmados de chikungunya por bairro e ano, consultar indicadores, fazer perguntas a uma LLM local e acompanhar notícias da Fiocruz.

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

## 💬 Usar a LLM local

Antes de usar a página **Pergunte aos dados**, baixe o Qwen3-0.6B uma vez, com internet:

```powershell
python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='Qwen/Qwen3-0.6B', local_dir='models/qwen3_0_6b')"
```

Depois, execute o app normalmente. O modelo roda na CPU e é carregado na primeira pergunta, sem necessidade de iniciar a API.

Informe um bairro ou ano na pergunta e confira a resposta nas tabelas disponíveis. O modelo pode cometer erros.

## 🔌 Rodar a API

Com o ambiente virtual ativo, abra outro terminal na raiz do projeto:

```powershell
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

## Escolha do modelo

O **Qwen3-0.6B** apresentou o melhor resultado entre os modelos avaliados: 65% de acerto na pontuação adotada e tempo médio de resposta de 14,51 segundos. Também exigiu menos espaço para os pesos, favorecendo a execução local sem GPU. As respostas devem ser conferidas nas tabelas.  
O histórico de testes com o resumo do desempenho dos modelos testados durante a avaliação e as justificatiavs de escolha estão disponíveis na pasta resultados.

## Integração local

O modelo é carregado com Transformers e PyTorch, executado na CPU e mantido em cache pelo Streamlit.
A função `consultar_dados` filtra os registros por bairro e ano, e esse recorte é enviado à LLM como contexto.
Após o download dos pesos, as perguntas são processadas localmente, sem envio a uma API externa.