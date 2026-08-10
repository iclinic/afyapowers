# Template do Relatório de Handoff (v5)

Renderize o relatório abaixo utilizando exclusivamente os dados presentes no JSON retornado pelo scanner.

## Objetivo

O relatório é destinado a Product Designers que trabalham diariamente no Figma.

Seu objetivo é facilitar a revisão do handoff antes da implementação, destacando rapidamente:

- o estado geral do arquivo;
- quais ajustes bloqueiam o início do desenvolvimento e quais são sugestões;
- quais frames concentram mais ajustes;
- quais ajustes possuem maior impacto;
- quais ações devem ser priorizadas.

Nunca invente informações.

Todo item apresentado deve existir no JSON.

Nunca estime.

Nunca complete dados ausentes.

---

# Estrutura do documento

# Handoff Review — {{fileName}}

| | |
|---|---|
| Página avaliada | {{page.name}} ({{pageIndex}} de {{pagesInFile}}) |
| Versão das regras | v{{rulesVersion}} |
| Bibliotecas do handoff | `{{config.allowedLibraries}}` |
| Frames avaliados | {{mainFrames}} |
| Ajustes bloqueantes | {{soma dos counts das categorias bloqueantes}} |
| Sugestões | {{soma dos counts das categorias de sugestão}} |
| Total de ajustes | {{soma de todos os counts}} |

Logo abaixo da tabela, escrever o veredito. Ele possui dois textos fixos; use o que corresponde à contagem e não parafraseie nenhum dos dois.

Quando houver pelo menos um ajuste bloqueante:

Este handoff tem {{ocorrências bloqueantes}} ajustes bloqueantes em {{camadas afetadas por categorias bloqueantes}} camadas. Recomenda-se alinhar com o Product Designer antes de iniciar o desenvolvimento.

Quando não houver nenhum ajuste bloqueante:

Nenhum ajuste bloqueante encontrado. Os {{total de ajustes}} ajustes listados são sugestões e não impedem o desenvolvimento.

Quando {{pagesInFile}} for maior que 1, escrever abaixo do veredito:

Esta análise cobre apenas a página {{page.name}}. As demais páginas do arquivo não foram avaliadas: {{pageNames sem a página avaliada}}.

Em seguida, sempre declarar as bibliotecas do arquivo e de onde a lista veio:

Bibliotecas adicionadas a este arquivo: {{config.allowedLibraries}} — descobertas no próprio arquivo e consideradas aprovadas para este handoff. Bibliotecas que publicam variáveis habilitadas no arquivo: {{enabledLibraries}}.

Quando houver nome em {{enabledLibraries}} que não apareça em {{config.allowedLibraries}}, declarar a divergência logo abaixo, nomeando as bibliotecas:

Divergência: {{nomes}} publica(m) variáveis habilitadas neste arquivo, mas não consta(m) entre as bibliotecas adicionadas a ele. Os tokens dessas bibliotecas aparecem como fora do handoff.

---

# Visão geral

Esta seção deve permitir identificar rapidamente onde estão concentrados os ajustes do arquivo.

| Frame | Estrutura e Auto Layout | Tokens do Design System | Organização das camadas | Documentação para desenvolvimento | Bloqueantes | Total |
|---|---:|---:|---:|---:|---:|---:|

{{uma linha por scope}}

Nome do frame deve utilizar scope.deepLink.

Caso um grupo não possua ocorrências, renderizar 0.

As quatro colunas de área de revisão somam o Total. A coluna Bloqueantes recorta o mesmo Total por criticidade e por isso não soma com as demais.

---

# Ajustes prioritários

Esta seção deve orientar o designer sobre quais correções deixam o handoff mais pronto para desenvolvimento.

Ordenar primeiro por criticidade: toda ação de categoria bloqueante vem antes de qualquer sugestão. Dentro de cada faixa, ordenar por `aggregateAffectedNodes`, utilizando `aggregate` como desempate.

Camadas afetadas medem o esforço real de ajuste. Ocorrências medem volume de propriedades e sobrepesam categorias que disparam várias vezes na mesma camada.

Na coluna Impacto, informar as camadas afetadas e, quando o número de ocorrências for diferente, também as ocorrências.

Máximo de três ações.

Omitir caso não existam pelo menos duas ações claras.

| Prioridade | Criticidade | Ação recomendada | Impacto |
|---|---|---|---|

Exemplos:

Aplicar tokens de espaçamento

Padronizar nomes das camadas

Substituir tokens de outra biblioteca

---

# Tela: {{scope.name}}

Visualizar no Figma

{{scope.deepLink}}

{{nodesScanned}} camadas verificadas

{{totalIssues}} ajustes antes do desenvolvimento, sendo {{bloqueantes}} bloqueantes

---

## Resumo

| Área de revisão | Ajustes |
|---|---:|
| Estrutura e Auto Layout | {{count}} |
| Tokens do Design System | {{count}} |
| Organização das camadas | {{count}} |
| Documentação para desenvolvimento | {{count}} |

| Criticidade | Ajustes |
|---|---:|
| Bloqueantes | {{count}} |
| Sugestões | {{count}} |

As duas tabelas recortam o mesmo conjunto de ajustes, por área de revisão e por criticidade. Os totais devem coincidir.

---

## Estrutura e Auto Layout

Renderizar somente se existirem findings.

### Organização da tela

| Camada | Criticidade | O que foi encontrado | Detalhes | Como ajustar |
|---|---|---|---|---|

{{uma linha por finding}}

---

## Tokens do Design System

Renderizar somente se existirem findings.

Agrupar por tipo.

Ordem sugerida:

### Tokens de outras bibliotecas

### Espaçamento

### Cores

### Tipografia

Cada grupo possui sua própria tabela.

| Camada | Criticidade | O que foi encontrado | Detalhes | Como ajustar |
|---|---|---|---|---|

---

## Organização das camadas

Renderizar somente se existirem findings.

| Camada | Criticidade | O que foi encontrado | Detalhes | Como ajustar |
|---|---|---|---|---|

---

## Documentação para desenvolvimento

Renderizar somente se existirem findings.

| Camada | Criticidade | O que foi encontrado | Detalhes | Como ajustar |
|---|---|---|---|---|

---

Caso truncated seja verdadeiro, escrever abaixo da tabela:

Lista parcial. Foram encontradas {{occurrences}} ocorrências desta regra em {{affectedNodes}} camadas.

Quando nodesOmitted for maior que zero, acrescentar na mesma frase:

{{nodesOmitted}} camadas não estão listadas acima.

Nunca apresentar os limites de exibição como se fossem o total encontrado.

---

# Configuração utilizada nesta análise

```text
rulesVersion
allowedLibraries
structuralLayers
iconNameSegments
ignoreLayerNames
cap
capPerNode
vectorClusterThreshold
```

---

# Agrupamento das categorias

| Grupo | Categorias |
|---|---|
| Estrutura e Auto Layout | missingStructureLayer, missingAutoLayout, gridAutoLayout, groupNode, redundantWrapper |
| Tokens do Design System | tokenOutsideHandoff, hardcodedGapOrPadding, hardcodedFillColor, illustrationVectorCluster, withoutTypographyToken, withoutTextStyle, usingLocalTextStyle |
| Organização das camadas | namingViolation, defaultLayerName |
| Documentação para desenvolvimento | missingAnnotations |

---

# Criticidade dos ajustes

Toda categoria tem exatamente uma criticidade, definida nesta tabela. Ela é a única fonte da verdade: o relatório, as contagens e a recomendação devolvida pelo agente saem daqui.

**Bloqueante** — impede uma implementação fiel do design. O desenvolvimento não deveria começar antes do ajuste.

**Sugestão** — melhora a qualidade do handoff, mas não impede o desenvolvimento da feature.

| Criticidade | Categorias |
|---|---|
| Bloqueante | missingAutoLayout, tokenOutsideHandoff, hardcodedGapOrPadding, hardcodedFillColor, withoutTypographyToken, namingViolation, defaultLayerName, missingAnnotations |
| Sugestão | missingStructureLayer, gridAutoLayout, groupNode, redundantWrapper, illustrationVectorCluster, withoutTextStyle, usingLocalTextStyle |

As duas listas cobrem exatamente as 15 categorias, sem sobreposição e sem sobra.

Algumas fronteiras não são óbvias e por isso ficam registradas:

- `gridAutoLayout` tem Auto Layout, apenas do tipo errado, e é sugestão; `missingAutoLayout` é a ausência de Auto Layout e é bloqueante.
- `withoutTypographyToken` é tipografia inteiramente definida à mão, então cai na mesma regra dos demais valores sem token e é bloqueante. `withoutTextStyle` (já tem token, falta o Text Style) e `usingLocalTextStyle` (o Text Style existe, mas é local) são sugestões.
- `missingStructureLayer` trata de como a tela foi organizada, e não de valor sem token nem de nome fora do padrão: é sugestão.

A criticidade não depende do arquivo, da quantidade de ocorrências nem do contexto do finding. Nunca reclassifique.

---

# Vocabulário do relatório

As colunas "O que foi encontrado" e "Como ajustar" devem utilizar exclusivamente os textos desta tabela.

A coluna "Detalhes" deve apenas complementar as informações utilizando os valores presentes no JSON.

A coluna "Criticidade" aceita exclusivamente os valores `Bloqueante` e `Sugestão`, conforme a tabela de criticidade. Nunca acrescentar comentário, ressalva ou grau intermediário nessa coluna.

Nunca utilizar nomes internos da API.

---

| Categoria | O que foi encontrado | Detalhes | Como ajustar |
|---|---|---|---|
| missingStructureLayer | Área obrigatória não foi separada na tela | A camada `{{missing}}` não foi encontrada entre as áreas principais da tela. | Criar a área `{{missing}}` como um Frame com Auto Layout. |
| missingAutoLayout | Frame sem Auto Layout | Informar qual Frame ou área da tela não organiza seu conteúdo com Auto Layout. | Aplicar Auto Layout (`Shift + A`) na camada indicada. |
| gridAutoLayout | Auto Layout em Grid | Informar em qual camada o Grid foi encontrado. | Alterar para Auto Layout vertical ou horizontal conforme a composição. |
| groupNode | Camada criada como Group | Groups dificultam a inspeção e a manutenção do handoff. | Converter o Group em Frame e aplicar Auto Layout quando necessário. |
| redundantWrapper | Frame intermediário sem função de layout | Informar a camada envolvida. | Remover o Frame que não contribui para a organização ou aparência da tela. |
| tokenOutsideHandoff | Token de outra biblioteca | Informar a biblioteca e as propriedades vinculadas. | Substituir pelos tokens da biblioteca aprovada para este handoff. |
| hardcodedGapOrPadding (gap) | Espaçamento sem token | Informar o Gap definido manualmente. | Aplicar um token de espaçamento do Design System. |
| hardcodedGapOrPadding (padding) | Espaçamento sem token | Informar os Paddings definidos manualmente, traduzindo os lados de `sides` para superior, direito, inferior e esquerdo. | Aplicar um token de espaçamento do Design System. |
| hardcodedFillColor | Cor sem token | Informar a cor definida manualmente. | Aplicar um token de cor do Design System. |
| illustrationVectorCluster | Ilustração composta por vetores editáveis | Informar a quantidade de vetores encontrada. | Converter a ilustração em um asset reutilizável. |
| withoutTypographyToken | Texto fora da tipografia do Design System | Informar a configuração tipográfica atual. | Aplicar o Text Style da biblioteca. |
| withoutTextStyle | Texto sem Text Style | Informar que há tokens tipográficos, mas não um Text Style aplicado. | Aplicar o Text Style correspondente. |
| usingLocalTextStyle | Text Style criado neste arquivo | Informar o nome do Text Style local. | Migrar para o Text Style da biblioteca. |
| namingViolation (english) | Nome da camada não está em inglês | Informar o nome e o contexto da camada. | Renomear a camada em inglês. |
| namingViolation (kebab) | Nome da camada fora do padrão de nomenclatura | Informar o nome e o contexto da camada. | Renomear usando kebab-case. |
| namingViolation (component) | Nome do componente fora do padrão | Informar o nome do componente. | Renomear usando o padrão Component-Variant. |
| namingViolation (semantic) | Nome da camada repete o conteúdo do texto | Explicar que o nome deve indicar a função da camada, não o texto exibido. | Renomear com um nome semântico, como `title`, `label`, `description` ou `caption`. |
| namingViolation (semantic + english) | Nome da camada repete o conteúdo do texto | Explicar que o nome deve indicar a função da camada, não o texto exibido, e que o nome atual também está em português. | Renomear com um nome semântico em inglês, como `title`, `label`, `description` ou `caption`. |
| defaultLayerName | Camada com nome padrão do Figma | A camada ainda mantém o nome gerado automaticamente. | Renomear a camada de acordo com sua função na tela. |
| defaultLayerName (import) | Camada com nome herdado da importação | O nome é um resíduo de SVG, AI, Sketch ou de um arquivo importado. | Renomear a camada ou converter o conteúdo em asset. |
| missingAnnotations | Sem anotações para desenvolvimento | Não há annotations neste Frame para orientar a implementação. | Adicionar annotations relevantes no Dev Mode. |

A linha `namingViolation (semantic + english)` é usada quando o finding possui o campo `note` indicando que o nome também está fora do inglês.

---

# Diretrizes de escrita

O relatório deve parecer produzido pelo próprio Design System.

Não deve soar como uma lista de erros.

---

Sempre descreva:

• o que foi encontrado

• onde foi encontrado

• como ajustar

---

Prefira frases completas e explique o problema observável no Figma.

Exemplo

Ruim

Espaçamento sem token

Melhor

O espaçamento entre os elementos foi definido manualmente com Gap 8, sem um token do Design System.

---

Sempre iniciar a coluna "Como ajustar" com um verbo.

Exemplos

Aplicar...

Criar...

Migrar...

Renomear...

Converter...

Adicionar...

Transformar...

---

Nunca utilizar nomes internos da API.

Exemplos

layoutMode

paddingLeft

itemSpacing

NONE

tokenOutsideHandoff

hardcodedGapOrPadding

Esses termos devem sempre ser traduzidos para linguagem do Figma.

---

Vocabulário obrigatório

Sempre utilizar:

Frame

Camada

Auto Layout

Token

Text Style

Dev Mode

Documentação para desenvolvimento

Bloqueante

Sugestão

Para a ligação de uma propriedade a uma variável do Figma, prefira “token” no texto destinado ao designer. Use “variável” apenas ao descrever uma configuração do arquivo quando essa precisão for indispensável.

Para criticidade, existem apenas os termos “bloqueante” e “sugestão”. Nunca escrever “crítico”, “grave”, “obrigatório”, “opcional”, “desejável” ou “nice to have” no lugar deles.

Nunca alternar entre sinônimos durante o relatório.

---

# Convenções obrigatórias

1. Nunca inferir informações.

2. Nunca listar findings inexistentes.

3. Todo problema deve existir no JSON.

4. Deep Links sempre pelo campo deepLink.

5. Agrupar ocorrências do mesmo nodeId.

6. Manter a ordem original dos frames.

7. Manter a ordem fixa dos grupos.

8. Quando houver truncamento, informar fora da tabela, com ocorrências, camadas afetadas e camadas omitidas.

9. O relatório deve ser completamente determinístico.

10. A linguagem deve ser consistente do início ao fim.

11. Declarar sempre a cobertura de páginas e as bibliotecas habilitadas no arquivo.

12. A criticidade de cada finding vem exclusivamente da tabela `# Criticidade dos ajustes`. Nunca classificar por julgamento próprio e nunca reclassificar em função do contexto do arquivo.

13. O veredito, as contagens do cabeçalho, o resumo por tela e a coluna Criticidade devem ser consistentes entre si. Um ajuste bloqueante contado no cabeçalho tem que aparecer marcado como Bloqueante na tabela da tela correspondente.
