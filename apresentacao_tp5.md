### Painel de Chikungunya no Recife

O painel transforma **dados reais de chikungunya** em visualizações que ajudam profissionais de saúde e gestores a identificar quais bairros merecem atenção e por quê. O ranking, o mapa de calor e a evolução anual permitem comparar territórios, acompanhar mudanças e orientar a investigação epidemiológica.

- **Coleta.** Os registros de casos vêm da Prefeitura do Recife, e a população por bairro do Censo 2022 fornece a referência para calcular a incidência por 100 mil habitantes.
- **Limpeza e integração.** A padronização dos nomes dos bairros permite cruzar as bases. O tratamento dos registros incompletos ajuda a definir quais comparações são possíveis e a explicitar suas limitações.
- **Modelagem.** As agregações por bairro e ano produzem indicadores de casos, incidência, hospitalização e letalidade. O bairro com mais casos pode ser diferente daquele com maior incidência.
- **Desenvolvimento de Agentes Inteligentes para Tomada de Decisão.** Essa foi a opção escolhida para a solução final. Diante de uma pergunta complexa, o agente pode escolher e combinar ferramentas de ranking e evolução anual ou pedir esclarecimento sobre a métrica. Por exemplo, ao perguntar quais bairros merecem mais atenção, o gestor pode descobrir que um bairro se destaca pela incidência e merece investigação territorial, enquanto outro concentra mais casos e merece atenção no planejamento assistencial.
- **IA e engenharia de prompts.** O agente usa o **GPT-OSS 20B pela API da Groq** para interpretar os resultados agregados. Os prompts orientam a leitura por indicador e a explicitação dos limites da análise. Os valores são calculados em Python e vinculados às evidências.
- **Apresentação e verificação.** O painel exibe gráficos, tabelas e sugestões de filtros para que o usuário possa reproduzir o recorte e conferir os achados.

A solução se alinha ao **ODS 3 — Saúde e Bem-Estar** ao apoiar a vigilância e o planejamento em saúde pública. Nas práticas de **ESG**, contribui para a dimensão social ao evidenciar diferenças entre territórios e para a governança ao tornar verificáveis os critérios usados para avaliar prioridades e orientar a alocação sustentável de recursos públicos.
