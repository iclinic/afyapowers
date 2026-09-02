# Plano de Implementação: {{feature_name}}

> **Para workers agênticos:** OBRIGATÓRIO: Use a skill de implementação do afyapowers-dev para implementar este plano. Os passos usam sintaxe de checkbox (`- [ ]`) para rastreamento.

**Objetivo:** [Uma frase descrevendo o que isto constrói]

**Arquitetura:** [2-3 frases sobre a abordagem]

**Tech Stack:** [Principais tecnologias/bibliotecas]

---

### Task 1: [Nome do Componente]

**Files:**
- Create: `caminho/exato/do/arquivo`
- Modify: `caminho/exato/do/arquivo/existente:linhas`
- Test: `tests/caminho/exato/do/teste`

**Type:** Backend

**Depends on:** none

- [ ] Passo 1: Escrever o teste que falha — descreva os comportamentos a testar e os resultados esperados
- [ ] Passo 2: Rodar o teste e confirmar que ele falha
- [ ] Passo 3: Implementar — descreva o que construir e as decisões-chave
- [ ] Passo 4: Rodar o teste e confirmar que ele passa

> O commit é feito pelo orquestrador após a conclusão da tarefa — não adicione um passo de commit.

### Task N: [Nome do Componente de UI] (Figma)

**Files:**
- Create: `caminho/exato/do/componente`
<!-- Para veredito `atualizar`, liste também o componente base como Modify — sem isso o implementer bate na allowlist e reporta NEEDS_CONTEXT: -->
<!-- - Modify: `caminho/do/componente/base` -->
<!-- Para Type UI DS Component, os Create ficam JUNTO do código da feature — nunca no diretório
     global/compartilhado de componentes: é uma cópia local de escopo reduzido, não um componente global. -->

**Assets:** `<diretório de assets do projeto>/` — o implementador pode baixar & criar arquivos de ícone/imagem aqui conforme necessário (arquivos exatos desconhecidos no momento do plano)

**Type:** UI Team Component | UI DS Component
<!-- Copiado da coluna Task Type da Árvore de Componentes de DS (derivado da Origem da C#:
     local → UI Team Component; externa → UI DS Component). Nunca reclassifique aqui. -->

**Depends on:** none | Task X
<!-- Reproduz a coluna "Depende de" da Árvore de Componentes de DS. Para `derivar`, a base é a primeira
     dependência. Para composto, todos os filhos são dependências. Ordem folhas→raiz. -->

**Figma:**
<!-- ATENÇÃO: em task de componente, File Key e Node ID são os DO ORIGINAL — colunas "Arquivo do original" e
     "Node ID do original" da entrada C# em ### Componentes. NUNCA os de uma instância, e o File Key
     pode ser de OUTRO arquivo (o do DS). A instância mostra só a variante que aquela tela usou; o original
     declara todos os eixos. Apontar para a instância entrega um componente mais pobre que o real — e como
     ele funciona na tela que originou a task, ninguém percebe. -->
- **File Key:** `<file_key_do_original>`
- **Node ID:** `<node_id_do_original>`
- **Breakpoints:** <breakpoint_name> (<width>px), ...
- **Medidas de aceite:** container max-width `<valor>`, margens laterais `<valor>`, gaps `<valor>`, colunas `<n>`, min/max de `<peça>` no breakpoint `<breakpoint_name>` (do Contrato de Layout)
- **Tokens do Figma:** `.afyapowers/features/<feature>/artifacts/figma-tokens.md`
<!-- Caminho do artefato de valores de token no tema das telas. Obrigatório em UI DS Component (é a única
     fonte de VALOR — o arquivo do DS resolve no modo default); cross-check em UI Team Component.
     Sempre o CAMINHO — nunca cole a tabela na task. -->

**Design System:**
<!-- Copiado da linha deste nó na `## Árvore de Componentes de DS` do design. Omita o bloco INTEIRO se o
     design não tem a árvore — nunca escreva um veredito que a árvore não confirmou. Sem o bloco, o
     implementer roda o procedimento de veredito ausente (checa existência antes de construir). -->
- **Veredito:** implementar | atualizar | derivar
- **Base:** `<Nome>` (`<import path>`) <!-- só para derivar (base que o wrapper compõe) e atualizar (set estendido) -->
- **Compõe de:** `<Nome>` (`<import path>`), `<Nome>` (`<import path>`) <!-- só para composto; cada filho já existe no código -->
- **Variantes:** <as variantes que ESTA task implementa>
<!-- UI Team Component: TODAS as variantes/estados que o original declara.
     UI DS Component: a linha "Variantes a implementar" da entrada C# — variantes semânticas usadas pelas
     telas + TODOS os estados interativos que o original declara (hovered, pressed, selected, …). -->
- **Anotações do Figma:** <anotações do Dev Mode deste nó, verbatim — estados interativos, animação, a11y, regras de conteúdo>
- **Estados a cobrir:** <linhas de `## Casos de Borda & Estados` que este componente é dono>

- [ ] Implementar usando o workflow do implementador Figma

> O commit é feito pelo orquestrador após a conclusão da tarefa — não adicione um passo de commit.

### Task N: [Nome da Tela] (Figma)

**Files:**
- Create: `caminho/exato/da/tela`
<!-- Se a task reusa um layout de página existente e precisa ajustá-lo, liste-o como Modify: -->
<!-- - Modify: `caminho/do/layout/existente` -->

**Assets:** `<diretório de assets do projeto>/` — o implementador pode baixar & criar arquivos de ícone/imagem aqui conforme necessário (arquivos exatos desconhecidos no momento do plano)

**Type:** UI Screen

**Depends on:** Task X, Task Y
<!-- As tasks de componente (UI Team Component / UI DS Component) de todo C# listado no Conteúdo desta T#. -->

**Figma:**
<!-- Em task UI Screen, File Key e Node ID são os DA TELA (entrada T# em ### Telas) — o alvo é o frame. -->
- **File Key:** `<file_key>`
- **Node ID:** `<id>` (frame raiz da tela)
- **Breakpoints:** <breakpoint_name> (<width>px), ...
- **Medidas de aceite:** container max-width `<valor>`, margens laterais `<valor>`, gaps entre seções `<valor>`, colunas `<n>` no breakpoint `<breakpoint_name>` (do Contrato de Layout — input do figma-token-verifier)
- **Tokens do Figma:** `.afyapowers/features/<feature>/artifacts/figma-tokens.md`
<!-- Caminho do artefato de valores de token no tema das telas — cross-check dos valores; sempre o CAMINHO, nunca o conteúdo. -->

**Layout de página:**
<!-- NÃO existe task separada de container/esqueleto. O layout de página é desta task, e a regra é reusar
     o que o projeto já tem — o mesmo wrapper/layout que as outras telas usam. Escreva `nenhum` só quando o
     projeto realmente não tiver nenhum; aí esta task cria o mínimo necessário seguindo a convenção do
     projeto, sem props/slots de escape criados "por precaução". -->
- **Reusar:** `<caminho do layout de página existente>` | nenhum (o projeto não tem — esta task cria seguindo a convenção do projeto)

- **Anotações do Figma:** <anotações do Dev Mode desta tela, verbatim>
- **Estados a cobrir:** <linhas de `## Casos de Borda & Estados` que esta tela é dona>

> Componentes são **PROIBIDOS** de setar max-width de página, centralização de página ou margens laterais de página — essas medidas são do layout de página desta tela. Conteúdo full-bleed usa o mecanismo que o projeto já tem para isso.

- [ ] Implementar usando o workflow do implementador Figma
