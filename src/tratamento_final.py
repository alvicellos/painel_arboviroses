from src.carga_preparacao import excluir_varios_valores, excluir_por_valor
#import streamlit as st

# ------------------------     Tratamento dos dados     ------------------------------------------  
# ---------------------------------------------------------------------------------- coluna NU_ANO 

# TODO # Passar para carga_preparacao ?
# TODO # Melhorar a docstring da função gerar_dados_analise

def gerar_dados_analise(dados, anos_exclusao):
    ''' 
    Recebe um DataFrame e chama a função exlucir_por_valor...
    Retorna um DataFrame limpo, um dicionário com os anos excluídos e a quantidade de linhas excluídas
    Melhorar essa docstring
    '''
    df_limpo_anos, valores = excluir_varios_valores(dados, "NU_ANO", anos_exclusao)
    dados_exclusao_anos = {ano : valor for ano, valor in zip(anos_exclusao, valores)}

    # ---------------------------------------------------------------------------------- coluna CLASSI_FIN (ficam apenas os casos confirmados, os demais são notificações)

    opcoes_classificacao = [1, 2, 5, 8, 10, 11, 12]
    df_limpo_classi, n_linhas_excluidas_classi, n_vazias_excluidas_classi = excluir_por_valor(
                df_limpo_anos, 
                'CLASSI_FIN', 
                opcoes_classificacao, 
                excluir_vazios=True)

    return (df_limpo_classi, 
           dados_exclusao_anos, 
           n_linhas_excluidas_classi, 
           n_vazias_excluidas_classi
    )

