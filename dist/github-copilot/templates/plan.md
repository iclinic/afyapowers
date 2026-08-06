# Plano de Implementação: {{feature_name}}

> **Para workers agênticos:** OBRIGATÓRIO: Use a skill de implementação do afyapowers para implementar este plano. Os passos usam sintaxe de checkbox (`- [ ]`) para rastreamento.

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

### Task 2: [Nome da Tela] — Esqueleto (Layer 0) (Figma)

**Files:**
- Create: `caminho/exato/do/esqueleto` (o layout que envolve as seções da tela)

**Type:** UI Screen

**Depends on:** none

**Figma:**
- **File Key:** `<file_key>`
- **Node ID:** `<id>` (frame raiz da tela)
- **Breakpoints:** <breakpoint_name> (<width>px), ...
- **Skeleton:** sim (o implementer faz só 2 chamadas MCP e constrói a partir das Medidas de aceite)
- **Medidas de aceite:** container max-width `<valor>`, margens laterais `<valor>`, gaps entre seções `<valor>`, colunas `<n>` no breakpoint `<breakpoint_name>` (do Contrato de Layout — obrigatório, é o critério de aceite do container e o input do figma-token-verifier)

> Task **dona do container** (max-width, centralização, margens laterais, ritmo entre seções — do Contrato de Layout). Layer 2 depende dela e não redefine essas medidas; componentes (Layer 1) não setam layout de página e usam o hook de escape para full-bleed legítimo (regra completa na skill writing-plans, "Regra de fronteira").

- [ ] Passo 1: Definir a geometria do container vazio primeiro — sem conteúdo de seções, o esqueleto já deve exibir max-width, centralização e margens laterais corretas em todos os breakpoints, conforme o Contrato de Layout do design
- [ ] Passo 2: Implementar o container — max-width, centralização, margens laterais e ritmo entre seções, conforme o Contrato de Layout do design
- [ ] Passo 3: Expor e documentar o hook de escape para full-bleed

> O commit é feito pelo orquestrador após a conclusão da tarefa — não adicione um passo de commit.

### Task N: [Nome do Componente de UI] (Figma)

**Files:**
- Create: `caminho/exato/do/componente`
<!-- Para veredito `atualizar`, liste também o componente base como Modify — sem isso o implementer bate na allowlist e reporta NEEDS_CONTEXT: -->
<!-- - Modify: `caminho/do/componente/base` -->

**Assets:** `<diretório de assets do projeto>/` — o implementador pode baixar & criar arquivos de ícone/imagem aqui conforme necessário (arquivos exatos desconhecidos no momento do plano)

**Type:** UI Component

**Depends on:** none | Task X
<!-- Reproduz a coluna "Depende de" da Árvore de Componentes de DS. Para `derivar`, a base é a primeira
     dependência. Para composto, todos os filhos são dependências. Ordem folhas→raiz. -->

**Figma:**
<!-- ATENÇÃO: em task UI Component, File Key e Node ID são os DO ORIGINAL — colunas "Arquivo do original" e
     "Node ID do original" da entrada C# em ### Componentes. NUNCA os de uma instância, e o File Key
     pode ser de OUTRO arquivo (o do DS). A instância mostra só a variante que aquela tela usou; o original
     declara todos os eixos. Apontar para a instância entrega um componente mais pobre que o real — e como
     ele funciona na tela que originou a task, ninguém percebe. -->
- **File Key:** `<file_key_do_original>`
- **Node ID:** `<node_id_do_original>`
- **Breakpoints:** <breakpoint_name> (<width>px), ...
- **Medidas de aceite:** container max-width `<valor>`, margens laterais `<valor>`, gaps `<valor>`, colunas `<n>`, min/max de `<peça>` no breakpoint `<breakpoint_name>` (do Contrato de Layout)
- **Estratégia de ícones:** <cadeia de preferência copiada de `## Estratégia de Ícones` do design; omita se o design não tem a seção>

**Design System:**
<!-- Copiado da linha deste nó na `## Árvore de Componentes de DS` do design. Omita o bloco INTEIRO se o
     design não tem a árvore — nunca escreva um veredito que a árvore não confirmou. Sem o bloco, o
     implementer roda o procedimento de veredito ausente (checa existência antes de construir). -->
- **Veredito:** implementar | atualizar | derivar
- **Base:** `<Nome>` (`<import path>`) <!-- só para derivar (base que o wrapper compõe) e atualizar (set estendido) -->
- **Compõe de:** `<Nome>` (`<import path>`), `<Nome>` (`<import path>`) <!-- só para composto; cada filho já existe no código -->
- **Variantes:** <todas as variantes/estados que o ORIGINAL declara>
- **Anotações do Figma:** nós `<node_ids>` — ver `### Anotações de Design` do design.md <!-- referência, não cópia: o orquestrador expande o texto verbatim no prompt do implementer -->
- **Estados a cobrir:** <IDs/títulos das linhas de `## Casos de Borda & Estados` que este componente é dono> <!-- referência; o orquestrador expande no prompt -->

- [ ] Implementar usando o workflow do implementador Figma
