# Revisão de Código: {{feature_name}}

## Revisão de Conformidade com a Spec
<!-- A implementação corresponde à spec de design? -->

### Constatações

| Severidade | Constatação | Resolução |
|------------|-------------|-----------|

## Revisão de Qualidade de Código
<!-- Padrões de código, patterns, casos de borda -->

### Constatações

| Severidade | Constatação | Resolução |
|------------|-------------|-----------|

## Revisão de Fidelidade Visual
<!-- Seção condicional: incluir somente quando `verificacao_visual: aplicável`. Se `verificacao_visual: não-aplicável`,
     omitir esta seção inteira. -->
<!-- Evidências visuais (screenshots + medições) ficam em artifacts/visual-checks/, seguindo a convenção
     <task>-<breakpoint>-<estado>-<fase>.png. Referencie os arquivos relevantes por breakpoint/estado abaixo. -->

### Constatações

| Severidade | Constatação | Resolução |
|------------|-------------|-----------|

### Evidências

<!-- Uma linha por task/breakpoint/estado verificado, com o caminho para a evidência correspondente. -->

| Task | Breakpoint | Estado | Evidência (artifacts/visual-checks/) |
|------|------------|--------|---------------------------------------|

<!-- Tasks de UI com override code-only aceito (marcador `[ACCEPTED BY USER: <motivo>]` em
     implementation-concerns.md) não possuem evidência visual e são listadas como PULADAS na tabela acima,
     em vez de reprovadas. -->

**Veredito da Fidelidade Visual:** <!-- Aprovado / Alterações Solicitadas -->

## Impedimentos
<!-- Uma linha por impedimento vindo de implementation-concerns.md. Resolução = "Corrigido em <commit/arquivo>"
     ou "Aceito pelo usuário" (a partir de um marcador `[ACCEPTED BY USER: <motivo>]` na linha do impedimento
     em implementation-concerns.md, se presente). Toda linha deve estar Corrigida ou Aceita para o veredito ser
     Aprovado. Omita esta seção se nenhum impedimento foi apontado. -->

| Impedimento | Resolução |
|-------------|-----------|

## Veredito
<!-- Aprovado / Alterações Solicitadas. Aprovado exige que a Revisão de Conformidade com a Spec e a Revisão de
     Qualidade de Código passem, que a Revisão de Fidelidade Visual esteja aprovada quando aplicável (respeitando
     tasks com override code-only aceito, listadas como PULADAS), E que todo impedimento esteja Corrigido ou
     Aceito. -->
