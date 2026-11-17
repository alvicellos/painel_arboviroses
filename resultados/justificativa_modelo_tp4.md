## Comparação dos modelos para escolha

A avaliação considerou 10 perguntas por modelo, totalizando 40 execuções, utilizando dados epidemiológicos em CSV, processamento local em CPU e precisão numérica `float32`. Os acertos foram classificados como completos (1 ponto), parciais (0,5 ponto) ou incorretos (0 ponto).

| Característica | Qwen3 0.6B | Qwen3 1.7B | SmolLM2 1.7B | TinyLlama 1.1B |
|---|---|---|---|---|
| **Arquitetura** | Transformer decoder-only, semelhante ao GPT | Transformer decoder-only, semelhante ao GPT | Transformer decoder-only, semelhante ao GPT | Transformer decoder-only, arquitetura Llama |
| **Parâmetros** | 0,6 bilhão | 1,7 bilhão | 1,7 bilhão | 1,1 bilhão |
| **Treinamento / finalidade** | Geração de texto, diálogo, instruções e raciocínio multilíngue | Geração de texto, diálogo, instruções e raciocínio multilíngue | Geração de texto e seguimento de instruções, principalmente em inglês | Geração de texto e conversação |
| **Precisão no teste** | **65%** | 60% | 0% | 20% |
| **Acertos completos** | 6 | 6 | 0 | 2 |
| **Acertos parciais** | 1 | 0 | 0 | 0 |
| **Erros** | 3 | 4 | 10 | 8 |
| **Respostas produzidas** | 10/10 | 10/10 | 10/10 | 10/10 |
| **Tempo médio por resposta** | **14,51 s** | 33,68 s | 28,49 s | 26,95 s |
| **Tempo de carregamento** | 2,32 s | 7,02 s | 7,52 s | 4,71 s |
| **Tamanho dos pesos em disco** | 1.433,66 MiB | 3.875,27 MiB | 3.264,22 MiB | 2.098,20 MiB |
| **RAM mínima estimada para inferência FP32** | 4 GB | 8 GB | 8 GB | 6 GB |
| **RAM recomendada** | 8 GB | 12–16 GB | 12–16 GB | 8 GB |
| **Execução local em CPU** | Sim | Sim | Sim | Sim |
| **Compatível com Hugging Face Transformers** | Sim | Sim | Sim | Sim |
| **Adequação ao projeto** | **Melhor relação entre precisão, velocidade e recursos** | Boa precisão, porém mais lento | Desempenho insatisfatório | Baixa confiabilidade nas consultas |

*As estimativas de RAM são aproximações práticas para inferência em CPU, não requisitos mínimos oficiais dos fabricantes. Dependem do sistema operacional, do comprimento do contexto e da implementação. Os tempos e tamanhos dos pesos são resultados medidos no experimento.*

Os quatro modelos pertencem à categoria de modelos generativos autorregressivos, semelhantes ao GPT. Todos podem ser carregados localmente com `AutoTokenizer` e `AutoModelForCausalLM`, da biblioteca Transformers da Hugging Face, sem necessidade de API externa.

O **Qwen3 0.6B foi selecionado** por apresentar o menor tempo médio de resposta (14,51 segundos), o menor tamanho de pesos e a maior pontuação de acerto (65%). Embora o Qwen3 1.7B tenha apresentado desempenho próximo em precisão (60%), seu tempo médio foi aproximadamente 2,3 vezes maior, sem benefício correspondente nas consultas avaliadas. O SmolLM2 e o TinyLlama apresentaram dificuldades significativas na interpretação dos dados, especialmente em comparações e rankings.

---

A escolha do Qwen3 0.6B é adequada para um ambiente local com recursos computacionais limitados, pois oferece maior eficiência sem exigir GPU dedicada. Entretanto, a precisão observada ainda não é suficiente para garantir respostas epidemiológicas confiáveis de forma autônoma. Recomenda-se utilizar o modelo para interpretar perguntas e formular respostas em linguagem natural, mantendo os cálculos e as agregações sob responsabilidade do Pandas.
**Integração local com a LLM**
O ambiente virtual Python foi preparado com as dependências de `requirements-llm.txt`, incluindo Streamlit, Pandas, Transformers e PyTorch.
Os pesos do Qwen3-0.6B foram baixados do Hugging Face Hub para `models/qwen3_0_6b`, com carregamento posterior exclusivamente local.
O Streamlit recebe a pergunta, e `consultar_dados` seleciona os registros enviados ao modelo como contexto CSV, acompanhado das definições das colunas.
O tokenizador e o modelo são carregados por `AutoTokenizer` e `AutoModelForCausalLM`, com cache via `st.cache_resource` para evitar recargas.
Para execução sem GPU, utiliza-se CPU com `torch.float32`, modo `eval()` e `torch.inference_mode()`, sem armazenamento de gradientes.
A geração desativa o raciocínio explícito (`enable_thinking=False`), limita a saída a 256 tokens e verifica entrada mais saída contra o limite de contexto de até 8.192 tokens.