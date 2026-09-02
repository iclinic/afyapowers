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

## Conformidade de Design System
<!-- Incluída apenas quando o design tem `## Árvore de Componentes de DS`. Remova esta seção se não se aplicar. -->
<!-- Uma linha por nó da árvore. Confere se o código honrou o veredito que o USUÁRIO confirmou na fase design.
     Importar   → aparece como import do path registrado (NÃO como definição nova)
     Atualizar  → mudança estritamente aditiva, nenhum consumidor existente afetado
     Derivar    → wrapper importa e compõe a base, não a reimplementa
     Implementar (composto) → cada filho de "Compõe de" é importado, não re-inlinado
     Implementar (escopo reduzido, Origem externa / UI DS Component) → arquivos junto da feature (NUNCA no
     diretório global/compartilhado), variantes implementadas = exatamente a lista "Variantes a implementar"
     da C# (incluindo os estados interativos declarados, como estados CSS)
     Adiado     → NÃO aparece no diff como definição nova (o usuário decidiu implementá-lo fora do workflow)
     Um nó Importar que virou definição nova é um componente duplicado: permanente, invisível, e divergindo
     do original desde o primeiro dia. Trate como Crítico, não como observação. O mesmo vale para um nó
     Adiado implementado, e para um escopo reduzido colocado no diretório compartilhado. -->

| Nó | Veredito confirmado | Encontrado no código (arquivo:linha) | Conforme? |
|----|---------------------|--------------------------------------|-----------|

### Composição e variantes
<!-- Checagens que não são por nó: props por eixo independente (sem produto cartesiano), estados de interação
     em pseudo-classes CSS (não como props), isolamento/export por arquivo, subcomponente de terceiros
     importado do pacote em vez de recriado, e componentes rejeitados pelo usuário ausentes do diff. -->
- ...

### Anotações e estados cobertos
<!-- As anotações do Figma e os Casos de Borda & Estados que as tasks carregavam foram implementados? Liste o
     que ficou de fora — foram requisitos confirmados com o usuário na fase design. -->
- ...

## Impedimentos
<!-- Uma linha por impedimento vindo de implementation-concerns.md. Resolução = "Corrigido em <commit/arquivo>"
     ou "Aceito pelo usuário" (a partir de um marcador `[ACCEPTED BY USER: <motivo>]` na linha do impedimento
     em implementation-concerns.md, se presente). Toda linha deve estar Corrigida ou Aceita para o veredito ser
     Aprovado. Omita esta seção se nenhum impedimento foi apontado. -->

| Impedimento | Resolução |
|-------------|-----------|

## Veredito
<!-- Aprovado / Alterações Solicitadas. Aprovado exige que a Revisão de Conformidade com a Spec e a Revisão de
     Qualidade de Código passem, E que todo impedimento esteja Corrigido ou Aceito. -->
