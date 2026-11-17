import streamlit as st
from comum import anos_exclusao
from src.carga_preparacao import tratamento_dados, mostrar_preenchimento,preparar_metricas_graficos_dados, excluir_por_valor, excluir_varios_valores
import pandas as pd
import numpy as np

total_registros, registros_sem_linha_vazia, df_sem_linhas_vazias = tratamento_dados(st.session_state.dados_api)

# --------------------------------------------------------------------------------------------------------------------- Inclusão de variáveis no estado
if "bairros_selecao" not in st.session_state:    
    st.session_state.bairros_selecao = []
    
if "quantos_anos" not in st.session_state:    
    st.session_state.quantos_anos = []

# --------------------------------------------------------------------------------------------------------------------- Configuração da página
st.set_page_config(layout="wide")

#'''# E os dados... 🎲🎲🎲 ?'''
# --------------------------------------------------------------------------------------------------------------------- Exibição dos dados brutos coletados da API
# --------------------------------------------------------------------------------------------------------------------- Exibição dos dados de população
#'''### Dados populacionais, utilizados na agregação:'''
#st.write(st.session_state.dados_populacao)

st.header("Dados da API da Prefeitura da Cidade do Recife ⭐🦁")
st.subheader(''' Explore os dados originais e entenda as colunas''')
# ----------------------------------------------------------------------------- Sobre os dados

#colunas_analise = ['HOSPITALIZ', 'EVOLUCAO', 'CLASSI_FIN']
colunas_analise = {'HOSPITALIZ': 'quantidade hospitalizacoes' , 'EVOLUCAO': 'como paciente evoluiu', 'CLASSI_FIN': 'confirmação diagnóstico'}
    
lista_bairros = list(st.session_state.dados_api["NM_BAIRRO"].unique())

remover_vazio = np.nan if np.nan in lista_bairros else None
if remover_vazio in lista_bairros:
    lista_bairros.remove(remover_vazio)
lista_bairros.sort()

lista_anos = list(st.session_state.dados_api["NU_ANO"].unique())
lista_anos.sort()

''' ## 🔎 Filtros '''
''' ##### Ao definir os filtros, serão exibidos os dados orignais filtrados pelas suas escolhas. Sem definição dos filtros você segue para o box sobre o tratamento dos dados.'''
''' ###### Esta seção é para que você conheça os dados. Filtrar os dados fica de fato mais interessante na página _Análises_.'''
''' ###### Para exibir os dados completos, selecione o período interiro, marque a opção exibir registros vazios e selecione todos os bairros com Select_all.'''

# Recupera a seleção ao entrar na página
if not "_bairros_selecao" in st.session_state:
    st.session_state["_bairros_selecao"] = st.session_state.bairros_selecao.copy()
    
def aplicar_filtros():
    st.session_state.bairros_selecao = (
        st.session_state["_bairros_selecao"].copy()
    )
    
with st.form("form_filtros"):

    col1, col2 = st.columns([2, 1])

    with col1:
        bairros_selecao = st.multiselect(
            f"Selecione os bairros:",
            options=lista_bairros,
            key="_bairros_selecao",
            #default=st.session_state.bairros_selecao,
        )
        
        bairros_vazios_check = st.checkbox("Exibir registros sem preenchimento para a coluna 'NM_BAIRRO'")

    with col2:
        st.session_state.quantos_anos = st.slider(
            "Selecione o período (em anos):",
            min_value=2015,
            max_value=2025,
            value=(2015, 2025)
        )

    aplicar = st.form_submit_button(
        "Aplicar filtros",
        type="primary",
        on_click=aplicar_filtros
        )

col1, col2 = st.columns(2)
with col1:
    st.write('''###### ⚠️ Atenção: onde o campo exibe _'None'_, o dado não foi preenchido''')
with col2:
    if st.session_state.bairros_selecao == []:
        pass    
    elif bairros_vazios_check and st.session_state.bairros_selecao != []:
        '''**Exibindo** os registros sem preenchimento na coluna NM_BAIRRO.'''
    else:
        '''**NÃO** exibindo os registros sem preenchimento na coluna NM_BAIRRO.'''

anos_selecao = [ano for ano in range(st.session_state.quantos_anos[0], st.session_state.quantos_anos[1] + 1)]

if anos_selecao != []:
    anos = anos_selecao

#st.session_state.dados_api
#filtrado = st.session_state.dados_api[st.session_state.dados_api['NM_BAIRRO'].isin(st.session_state.bairros_selecao)].sort_values(by=["NU_ANO", "NM_BAIRRO"])

if bairros_vazios_check:
    filtrado = st.session_state.dados_api[st.session_state.dados_api['NM_BAIRRO'].isin(st.session_state.bairros_selecao) | st.session_state.dados_api['NM_BAIRRO'].isna()].sort_values(by=["NU_ANO", "NM_BAIRRO"])
else:
    filtrado = st.session_state.dados_api[st.session_state.dados_api['NM_BAIRRO'].isin(st.session_state.bairros_selecao)].sort_values(by=["NU_ANO", "NM_BAIRRO"])
    
#filtrado['NM_BAIRRO'] = filtrado['NM_BAIRRO'].fillna("Não preenchido")

#fig, ax = plt.subplots()
#ax.bar(X, Y)

#'''# Fig.'''
#st.pyplot(fig)

if st.session_state.quantos_anos != [] and st.session_state.bairros_selecao != []:
    filtrado = filtrado[filtrado['NU_ANO'].isin(anos)].sort_values(by=["NU_ANO", "NM_BAIRRO"])  

if not filtrado.empty and st.session_state.bairros_selecao != []:
    col1, col2 = st.columns(2)

    with col1:
        with st.container():
            if st.session_state.bairros_selecao == []:
                '''### Exibindo todos os bairros'''
            else:
                f'''### Bairros selecionados:                
        {", ".join(st.session_state.bairros_selecao)} 
        '''

    with col2:
        #f'''### Intervalo de anos:
        #{min(anos)} a {max(anos)}'''
        
        f'''### Período selecionado:
        {min(anos)} a {max(anos)}'''

    # ----------------------------------------------------------------------------- Exibição do dataframe de dados originais após aplicação do filtro pelo usuário (ou completo na primeria exibição)
    
    
    st.dataframe(filtrado)
        
    # for bairro in st.session_state.bairros_selecao:
    #     st.write(f"Registros para o bairro {bairro}: {len(filtrado[filtrado['NM_BAIRRO'] == bairro])}")
    
    quantidade_de_casos = [
        len(filtrado[filtrado['NM_BAIRRO'] == bairro])
        for bairro in st.session_state.bairros_selecao
    ]
        
    '''### Registros por bairro:'''
    df_contagem = pd.DataFrame({
            'bairros': st.session_state.bairros_selecao,
            'quantidade_de_casos': quantidade_de_casos
        })
    
    #df_contagem
    
    st.bar_chart(df_contagem,
                 x="bairros",
                 y="quantidade_de_casos",
                 y_label="casos")
    
    numeros_preenchimento = mostrar_preenchimento(filtrado, colunas_analise)
    print(numeros_preenchimento)
    
    total_exibidos = len(filtrado)
    linhas_com_vazio = filtrado.isna().any(axis=1).sum()
    bairro_vazio = filtrado['NM_BAIRRO'].isna().sum()
    
    '''
    ##### >> O que cada coluna mostra ?
    '''
        
    numeros_preenchimento = mostrar_preenchimento(filtrado, colunas_analise)
    
    # Gráficos
    preparar_metricas_graficos_dados(numeros_preenchimento, colunas_analise)


    with st.expander("Sobre os dados filtrados (clique na ⬇️ para fechar este quadro):", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            f'''##### Total de registros nos dados originais: {total_registros}'''    
            st.caption("(equivalente à contagem de notificações - coluna 'NU_NOTIFIC')")
        with col2:
            f'''##### Total de registros exibidos: {len(filtrado)}  
        - Registros com alguma coluna sem preenchimento: {linhas_com_vazio} ({(linhas_com_vazio/len(filtrado)) * 100:.2f}%).  
        - Registros com a coluna nome do bairro (NM_BAIRRO) vazia: {bairro_vazio} ({(bairro_vazio/len(filtrado)) * 100:.2f}%).
    '''
elif filtrado.empty or st.session_state.bairros_selecao == []:
    '''**Filtros não selecionados:** selecione acima os filtros que deseja aplicar.'''
else:
    '''Os filtros selecionados não retornaram resultados.'''

# ------------------------     Tratamento dos dados     ------------------------------------------  

# ---------------------------------------------------------------------------------- coluna NU_ANO 

df_limpo_classi = st.session_state.dados_tratados
dados_exclusao_anos = st.session_state.dados_exclusao_anos
n_linhas_excluidas_classi = st.session_state.n_linhas_excluidas_classi
n_vazias_excluidas_classi = st.session_state.n_vazias_excluidas_classi

# ------------------------  Fim Tratamento dos dados     ------------------------------------------


# ---------------------------------------------------------------------------------- Entendimento sobre o tratamento dos dados de acordo com os valores
st.divider()
st.header("📊 A respeito do tratamento dos dados:")

bairro_vazio_tratamento = df_sem_linhas_vazias['NM_BAIRRO'].isna().sum()
with st.expander("Critérios para tratamento dos dados (clique na ⬇️ para fechar este quadro):", expanded=True):
    
    f'''#####  As chaves de leitura (códigos preenchimento):

            cod_class_fin = 
            "5" : "Descartado",
            "10": "Dengue",
            "11": "Dengue com sinais de alarme",
            "12": "Dengue grave",
            "13": "Chikungunya"
            
            cod_hospitalizacao = 
            '1': "Sim",
            '2': "Não",
            '9': "Ignorado"

            cod_evolucao = 
            "1": "cura",
            "2": "óbito pelo agravo",
            "3": "óbito por outras causas",
            "4": "óbito em investigação",
            "9": "ignorado"       

##### Que registros (linhas) estão sendo excluídos e porque ?

- Os anos **2015 e 2016**, completos:  
Observe que tem muitos e muitos registros com a coluna 'NM_BAIRRO' sem dados. Isso prejudica a análise, que parte do ponto de vista das localidades (bairros).

- Todos os registros a coluna classi_fin vazia diferente de 13, incluindo as vazias.  
Queremos manter apenas os casos confirmados de chikungunya. Podemos considerar os demais registros apenas como notificações.

##### Após as exclusões, o que permanece inalterado e porque ?
- A coluna 'HOSPITALIZ'  
      - Mas para o cálculo da gravidade da doença serão considerados apenas registros com código:  
      1 - 'hospitalização confirmada'

- A colunas 'EVOLUCAO'. Como teremos apenas casos confirmados da doença, todos os valores permanecem.  
        - Mas para o cálculo da gravidade da doença serão considerados apenas registros com código:  
      2 - 'óbito pelo agravo'


##### Total de registros nos dados originais: {total_registros}  
##### Quantidade de registros excluídos: 
ano de 2015: {dados_exclusao_anos.get(2015, 0)}  
ano de 2016: {dados_exclusao_anos.get(2016, 0)}  
casos sem confirmação da doença: {n_linhas_excluidas_classi + n_vazias_excluidas_classi}  
##### Total de registros após tratamento dos dados: **{len(df_limpo_classi)}**  
Uma perda significativa, porém necessária para a consistência da análise.'''


# ---------------------------------------------------------------------------------- Exibição dos dados tratados
st.divider()
st.header("🏁 Dados tratados: ")
'''##### É sobre esses dados que fala a página _análises_:'''

df_limpo_classi

'''
##### >> O que cada coluna mostra agora?
'''

# Gráficos
numeros_preenchimento = mostrar_preenchimento(df_limpo_classi, colunas_analise)   
preparar_metricas_graficos_dados(numeros_preenchimento, colunas_analise)

st.write('''_O leão 🦁 e a estrela ⭐🦁 são referências à [bandeira da cidade](https://pt.wikipedia.org/wiki/Bandeira_do_Recife)._''')
