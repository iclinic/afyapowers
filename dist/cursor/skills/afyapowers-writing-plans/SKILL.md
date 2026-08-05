---
name: afyapowers-writing-plans
description: Use when the current afyapowers phase is plan — creates implementation plans from tech specs
model: claude-opus-5
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste. Document everything they need to know: which files to touch for each task, step-by-step instructions, testing, docs they might need to check, how to test it. Give them the whole plan as bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume they are a skilled developer, but know almost nothing about our toolset or problem domain. Assume they don't know good test design very well.

**Announce at start:** "Estou usando a skill writing-plans para criar o plano de implementação."

## Phase Gate

If this skill was invoked by `/afyapowers:next` (you already know the active feature slug and confirmed the phase is `plan` from the conversation context above):
- Skip steps 1-3 — use the slug from context
- Read the design from `.afyapowers/features/<feature>/artifacts/design.md` as input

Otherwise (direct invocation):
1. Read `.afyapowers/features/active` to get the active feature
2. Read `.afyapowers/features/<feature>/state.yaml` — confirm `current_phase` is `plan`
3. If not in plan phase, tell the user the current phase and stop
4. Read the design from `.afyapowers/features/<feature>/artifacts/design.md` as input

**Save plans to:** `.afyapowers/features/<feature>/artifacts/plan.md`

## Scope Check

If the spec covers multiple independent subsystems, it should have been broken into sub-project specs during design. If it wasn't, suggest breaking this into separate plans — one per subsystem. Each plan should produce working, testable software on its own.

## Figma Task Layer Inference

Before defining Figma tasks, check if the design doc contains a `## Recursos do Figma` section with `### Telas` and `### Componentes`.

### Inferência por Layers

**If Figma Resources are present**, read `### Telas`, `### Componentes` and `## Árvore de Componentes de DS`, and infer task layers directly — no Figma MCP calls at planning time:

1. **Layer 0 — Esqueleto (container):** Quando o design doc tem uma seção `## Contrato de Layout`, gere uma task de esqueleto por tela (uma por entrada `T#` de `### Telas` que representa uma tela completa). Esta task é a **dona do container**: largura máxima, centralização, margens laterais e o ritmo (gap) entre seções — tudo derivado da geometria do frame nas linhas do Contrato de Layout correspondentes a essa tela. `**Depends on:** none`. Se `## Contrato de Layout` estiver ausente, não gere task de esqueleto — prossiga direto para Layer 1/Layer 2.

2. **Layer 1 — Componentes:** **a `## Árvore de Componentes de DS` decide quais componentes viram task.** Quando o design tem essa seção, ela é a autoridade sobre quais componentes precisam de task — cada nó já foi resolvido contra o código real e confirmado pelo usuário na fase design:

   | Veredito na árvore | Gera task Layer 1? | O que o plano faz |
   |---|---|---|
   | `Importar` | **NÃO** | O componente já existe. Registre o **import path** da árvore na task de tela (Layer 2) que o consome. Nunca gere task para reimplementá-lo. |
   | `Implementar` | Sim | Task `UI Component`. Se o nó tem filhos em **Depende de**, é um **composto**: a task depende deles e os compõe. |
   | `Derivar` | Sim | Task `UI Component`. Depende do nó base (primeiro item de **Depende de**). |
   | `Atualizar` | Sim | Task `UI Component` que **modifica** o componente existente de forma aditiva. Liste o arquivo do componente base em `**Files:** Modify` — sem isso o implementer bate na allowlist e reporta NEEDS_CONTEXT. |

   Nós que o usuário rejeitou na confirmação não geram task; nós cujo pai foi marcado "implementar sem a dependência" geram a task do pai com essa nota explícita.

   **Sem `## Árvore de Componentes de DS`** (layout sem componentes de DS): cada entrada `C#` de `### Componentes` com origem local vira uma task Layer 1 com seu node ID. Um `INSTANCE` externo (definição fora do arquivo) **não** vira task por padrão — na ausência da árvore você não tem como saber se ele já existe no código, e o custo de errar é assimétrico: uma task a menos é uma dependência faltando que aparece na review, enquanto uma task a mais é um componente de DS duplicado que ninguém vê. Registre-o como import a confirmar e diga isso no plano.

   Layer 1 não tem dependência do esqueleto — roda **em paralelo** com a task de Layer 0, porque componentes não são donos da geometria do container. Se nenhum nó da árvore tem task e `### Componentes` está vazio, não há tasks Layer 1.

3. **Layer 2 — Screens:** Each `T#` entry in `### Telas` becomes a Layer 2 task, taking its `Arquivo` and `Node ID` straight from that entry. Depends on the Layer 1 tasks of every `C#` listed in that `T#`'s `Conteúdo` — **e também** na task de esqueleto (Layer 0) daquela tela, quando existir. O esqueleto vem primeiro: seu Passo 1 define a geometria do container vazio (max-width, centralização, margens, sem conteúdo de seções), e as tasks de tela/montagem (Layer 2) montam seu conteúdo dentro desse container.

**Granularity rule:** If a node is typed COMPONENT/COMPONENT_SET, it MUST be its own Layer 1 task. Do not merge it into a parent section's task.

**Regra de fronteira (Layer 1 vs Layer 0):** componentes (Layer 1) são **PROIBIDOS** de setar max-width, centralização ou margens de página — essas medidas pertencem exclusivamente à task de esqueleto (Layer 0). A regra é imposta em runtime pelo implementer do componente/tela e checada pelo `code-quality-reviewer`. Quando um componente precisa de **full-bleed** legítimo (ultrapassar a margem lateral), a task do componente deve usar o hook de escape exposto pelo esqueleto — nunca redefinir max-width/centralização diretamente no componente.

**Medidas de aceite em tasks de UI:** **toda** task de UI — Layer 0, Layer 1 e Layer 2 — deve anexar, no bloco `**Figma:**`, as **Medidas de aceite** extraídas do `## Contrato de Layout`, apenas para os breakpoints relevantes a essa task.

Isso **inclui a task de esqueleto (Layer 0)**, e é justamente a que mais precisa: ela é a dona do container (max-width, centralização, margens laterais), então as medidas do Contrato de Layout são literalmente o critério de aceite dela. Descrevê-las só no corpo da task não basta — Layer 0 é `Type: UI Screen`, roteia para o `figma-design-implementer`, cujo passo de verificação de fidelidade é obrigatório, e o `figma-token-verifier` lê as medidas **do bloco `**Figma:**`**. Sem elas ali ele retorna falha de pré-flight (`FAIL`), a task queima as 2 tentativas do loop e termina com um BLOCKING garantido — na única task que não podia falhar, porque todas as tasks de tela dependem dela.

Each Figma task uses the Figma Task Structure format (see below), taking its coordinates from the `T#` entry (screens) or the `C#` entry (components) and its breakpoints from `### Breakpoints`.

#### Example

Given this design doc (assumindo `## Contrato de Layout` presente para as duas telas):

```
### Telas
#### T1 — Hero Section   → F1 `pqrs`, node `1:2`, FRAME, 1440x800
#### T2 — Pricing Section → F1 `pqrs`, node `2:1`, FRAME, 1440x600

### Componentes
#### C1 — CTA Button   → F1 `pqrs`, node `1:4`,  COMPONENT
#### C2 — Pricing Tier → F1 `pqrs`, node `2:10`, COMPONENT_SET
#### C3 — Search Field → F2 `AbC123`, node `45:12`, COMPONENT_SET  (origem: link fornecido)

## Árvore de Componentes de DS
| C1 | CTA Button   | Implementar | —  | … | `CtaButton`   | UI Component |
| C2 | Pricing Tier | Implementar | —  | … | `PricingTier` | UI Component |
| C3 | Search Field | Importar    | —  | … | `@ds/Search`  | —            |
```

Correct task output:
```
Task 1: Hero Section — Esqueleto (Layer 0) (Figma)     — T1, F1 `pqrs`, node `1:2`,  depends on: none
Task 2: Pricing Section — Esqueleto (Layer 0) (Figma)  — T2, F1 `pqrs`, node `2:1`,  depends on: none
Task 3: CTA Button (Figma)      — C1, F1 `pqrs`,   node `1:4`,  depends on: none
Task 4: Pricing Tier (Figma)    — C2, F1 `pqrs`,   node `2:10`, depends on: none
Task 5: Hero Section (Figma)    — T2… → T1, F1 `pqrs`, node `1:2`, depends on: Task 1, Task 3, Task 4
Task 6: Pricing Section (Figma) — T2, F1 `pqrs`,   node `2:1`,  depends on: Task 2, Task 4
```

↑ Note three things. **C3 has no task** — its verdict is `Importar`, so the screen task that uses it just
imports `@ds/Search`. The component tasks take their coordinates from the `C#` entries, and the screen
tasks from the `T#` entries. And had C3 needed a task, its `File Key` would be **`AbC123`** — a different
file from every other task in the plan, because that is where its original is declared. That is expected,
not an inconsistency to normalize.

Wrong output — DO NOT do this:
```
Task 1: Hero Section (Figma)       — merges CTA Button into the screen task
Task 2: Search Field (Figma)       — builds a component whose verdict was Importar
Task 3: Search Field (Figma)       — File Key `pqrs` (the screen's) instead of `AbC123` (the original's)
```
↑ The first merges a component that must be its own Layer 1 task. The second duplicates a component that
already exists in code. The third points the implementer at the screen's file, where the original is not
declared — so it would read an instance and ship only the variant that screen used.

When there are no components at all (e sem `## Contrato de Layout` aplicável neste exemplo):
```
Task 1: Hero Section (Figma)       — T1, node `1:2`, depends on: none
Task 2: Pricing Section (Figma)    — T2, node `2:1`, depends on: none
```

**Figma task validation (run before finalizing the plan):**
1. Todo nó da `## Árvore de Componentes de DS` com veredito `Implementar`/`Atualizar`/`Derivar` tem uma task Layer 1 correspondente — e **nenhum** nó `Importar` tem task (esses viram import na task de tela). Sem a árvore: cada entrada `C#` de origem local tem sua task
2. Every entry in **Telas** has a corresponding Layer 2 task with its node ID
3. No Layer 2 task includes implementation work for a component that has its own Layer 1 task
4. Layer 2 tasks depend on Layer 1 tasks whose components were originally children of that frame (extracted COMPONENT/COMPONENT_SET or INSTANCE references)
5. Se `## Contrato de Layout` está presente, existe uma task de esqueleto (Layer 0) para cada frame raiz de tela, e a task de Layer 2 correspondente depende dela (trivially passes se Contrato de Layout estiver ausente)
6. **Toda** task de UI (Layer 0, Layer 1 e Layer 2) carrega no bloco `**Figma:**` os breakpoints e as **Medidas de aceite** — Layer 0 incluída, sem exceção
7. As dependências (`**Depends on:**`) das tasks de componente reproduzem a coluna **Depende de** da árvore, na ordem folhas→raiz: nenhuma task aparece antes de algo de que ela depende. Para `derivar`, a base é a primeira dependência; para composto, todos os filhos são dependências
8. Toda task `UI Component` derivada da árvore carrega o bloco `**Design System:**` com `Veredito` preenchido, e toda task `atualizar` lista o arquivo do componente base em `**Files:** Modify`
9. Toda anotação de `### Anotações de Design` e toda linha de `## Casos de Borda & Estados` tem ao menos uma task dona. Uma anotação sem dono é um requisito confirmado com o usuário que ninguém vai implementar

**If no Figma Resources:** Skip this section entirely. Proceed with standard task generation.

## File Structure

Before defining tasks, map out which files will be created or modified and what each one is responsible for. This is where decomposition decisions get locked in.

- Design units with clear boundaries and well-defined interfaces. Each file should have one clear responsibility.
- You reason best about code you can hold in context at once, and your edits are more reliable when files are focused. Prefer smaller, focused files over large ones that do too much.
- Files that change together should live together. Split by responsibility, not by technical layer.
- In existing codebases, follow established patterns. If the codebase uses large files, don't unilaterally restructure - but if a file you're modifying has grown unwieldy, including a split in the plan is reasonable.

This structure informs the task decomposition. Each task should produce self-contained changes that make sense independently.

## No Code Snippets

Tasks must never contain code blocks with implementation code, test code, or inline code examples. Steps describe what to build, what to test, edge cases, and expected behavior — in plain language. The only acceptable code blocks are shell commands for running tests or committing.

**Styling = Figma task:** When Figma Resources are present in the design doc, any task involving styling (CSS, Tailwind, component layout/disposition, visual properties) MUST be treated as a Figma task. Always split design and logic into separate tasks. Design (Figma) tasks come first; logic tasks depend on them. Goal: 100% visual fidelity before adding behavior.

- **What counts as styling:** CSS properties, Tailwind classes, component layout, spacing, typography, colors, responsive breakpoints, content disposition
- **What stays as standard tasks:** API integration, state management, form validation, event handlers, data fetching, business logic

## Bite-Sized Task Granularity

**For standard (non-Figma) tasks,** each step is TDD-inspired with descriptive instructions (no code snippets). Each step describes what to do, why, which edge cases to cover, and expected outcomes:

- Write the failing test (describe behaviors and expected outcomes) → run test and confirm failure (specify command and expected error) → implement minimal code (describe approach, patterns, decisions) → run test and confirm pass (specify command)

Do **not** add a commit step to tasks — the orchestrator commits each task sequentially after its wave completes.

**For Figma tasks:** a single step — "Implement using the Figma implementer workflow". The subagent prompt owns the how. No implementation steps in the plan.

## Dependency Declaration

Every task MUST have a `**Depends on:**` line immediately after the `**Files:**` block.

- Use `none` if the task has no dependencies
- Use `Task N` or `Task N, Task M` (comma-separated) to declare dependencies on other tasks
- Dependencies are by task number, matching the `### Task N:` heading

**What counts as a dependency:**
- Task B modifies a file that Task A creates → Task B depends on Task A
- Task B imports a module that Task A creates → Task B depends on Task A
- Task B builds on an interface that Task A defines → Task B depends on Task A
- Task B and Task A are completely independent → no dependency needed

**Plan-time file overlap validation:**
After declaring dependencies, check that tasks which could run in parallel (no mutual dependency) don't share files in their `**Files:**` lists. If two parallel-eligible tasks touch the same file, add a dependency between them to force sequential execution.

File overlap validation is a safety net, not a substitute for thinking about task ordering. Always declare logical dependencies (imports, shared interfaces) explicitly.

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED: Use the afyapowers implementing skill to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

## Task Type & Roteamento

Toda task carrega uma linha obrigatória `**Type:**` (junto de `**Files:**`/`**Depends on:**`) com um destes valores: `UI Screen` | `UI Component` | `UI Logic` | `Backend` | `General`. O `Type` determina para qual implementer a task é despachada e como é verificada:

| Type | O que é | Dispatch | Verificação | MCP · cap |
|---|---|---|---|---|
| **UI Screen** | Página/tela/view ou esqueleto de layout de página; composição de componentes | `figma-design-implementer` | staleness vs Contrato de Layout + `figma-token-verifier` (máx 2 tentativas) | Sim · budget ~12 calls/wave |
| **UI Component** | Um componente/`COMPONENT_SET`: primitivo, genérico de DS ou derivado; todas as variantes, isolado, exportado | `figma-component-implementer` | self-review contra o screenshot/tokens já em contexto (sem re-fetch) | Sim · budget ~12 calls/wave |
| **UI Logic** | Comportamento/estado no cliente sem nova superfície visual (hooks, estado, validação, fetch/binding, rota, animação) | `tdd-implementer` | testes (TDD) | Não · sem cap |
| **Backend** | Servidor: endpoints, serviços, models, migrations, regras de negócio, integrações | `tdd-implementer` | testes (TDD) | Não · sem cap |
| **General** | Cross-cutting sem UI nem lógica de produto: config, tooling, scripts, docs, chore, refactor | `tdd-implementer` | testes quando aplicável | Não · sem cap |

**Fallback de compatibilidade:** plan sem `**Type:**` → heurístico legado (`**Figma:**` presente → `figma-design-implementer`; senão → `tdd-implementer`).

## Task Structure

````markdown
### Task N: [Nome do Componente]

**Files:**
- Create: `caminho/exato/do/arquivo.py`
- Modify: `caminho/exato/do/arquivo/existente.py:123-145`
- Test: `tests/caminho/exato/do/teste.py`
**Type:** UI Screen | UI Component | UI Logic | Backend | General
**Depends on:** none | Task X, Task Y

- [ ] **Passo 1: Escrever o teste que falha**

  Describe what behaviors to test: valid inputs, invalid inputs, edge cases.
  Explain expected outcomes for each scenario. Specify which file to write
  the test in and what module/function is being tested.

- [ ] **Passo 2: Rodar o teste e verificar que ele falha**

  Specify the exact command to run and the expected failure reason.

- [ ] **Passo 3: Implementar o código mínimo para fazer o teste passar**

  Describe what the implementation should do, key decisions (which pattern
  to follow, which existing utility to reuse), and edge cases to handle.
  Specify which file to modify.

- [ ] **Passo 4: Rodar o teste e verificar que ele passa**

  Specify the exact command to run.
````

## Figma Task Structure

Use this format for tasks that implement UI components with Figma designs. The design doc's `## Recursos do Figma` and `## Contrato de Layout` sections provide the source data for the Figma block.

**How to identify Figma tasks:** If the thing being implemented has a `T#` entry in `### Telas` or a `C#` entry in `### Componentes`, it is a Figma task. Backend tasks, API routes, data models, business logic, and other non-UI tasks use the standard task structure above.

**Design/logic split:** When Figma resources exist, tasks that involve any styling (CSS, Tailwind, layout, disposition) must be Figma tasks, even if they also have logic. Always create separate tasks: a Figma task for the visual design, then a standard task for the behavior/logic that depends on the Figma task. Example: "Contact Form Layout (Figma)" → "Contact Form Logic" (depends on layout task).

**No TDD, no code snippets.** Figma tasks describe what to achieve — the implementer subagent uses the Figma MCP tools and the Figma implementer workflow to determine how.

### Layer 0 — Esqueleto (skeleton) task structure

Gerada apenas quando `## Contrato de Layout` está presente (ver Figma Task Layer Inference acima). Uma task por frame raiz de tela.

```markdown
### Task N: [Nome da Tela] — Esqueleto (Layer 0) (Figma)

**Files:**
- Create: `caminho/exato/do/esqueleto` (o layout que envolve as seções da tela)

**Type:** UI Screen

**Depends on:** none

**Figma:**
- **File Key:** `<file_key>`
- **Node ID:** `<id>` (frame raiz da tela)
- **Breakpoints:** <breakpoint_name> (<width>px), ...
- **Skeleton:** sim (task de esqueleto/Layer 0 — o implementer faz só 2 chamadas MCP, `get_variable_defs` + `get_screenshot`, e constrói a partir das Medidas de aceite; sem `get_design_context`)
- **Medidas de aceite:** container max-width `<valor>`, margens laterais `<valor>`, gaps entre seções `<valor>`, colunas `<n>` no breakpoint `<breakpoint_name>` (do Contrato de Layout — obrigatório: é o critério de aceite do container e o input do figma-token-verifier)

> Esta task é a **dona do container**: largura máxima, centralização e margens laterais da página, mais o ritmo (gap) entre seções — tudo derivado da geometria do frame no Figma (ver Contrato de Layout do design). Tasks de tela/montagem (Layer 2) DEPENDEM desta task e não redefinem essas medidas.
>
> Componentes (Layer 1) são **PROIBIDOS** de setar max-width, centralização ou margens de página — eles vivem dentro do container que o esqueleto define. Quando um componente precisa de **full-bleed** legítimo (ex: banner que ultrapassa a margem lateral), ele usa o hook de escape exposto por este esqueleto (ex: prop/slot `fullBleed` ou classe utilitária documentada aqui) — nunca sobrescreve max-width/centralização diretamente no componente.

- [ ] Passo 1: Definir a geometria do container vazio primeiro — sem conteúdo de seções, o esqueleto já deve exibir max-width, centralização e margens laterais corretas em todos os breakpoints, conforme o Contrato de Layout do design
- [ ] Passo 2: Implementar o container — max-width, centralização, margens laterais e ritmo entre seções, conforme o Contrato de Layout do design
- [ ] Passo 3: Expor e documentar o hook de escape para full-bleed
```

O esqueleto vem primeiro: as tasks de Layer 2 montam seu conteúdo dentro do container que o esqueleto define, sem redefinir suas medidas.

### Layer 1 / Layer 2 — component and screen task structure

```markdown
### Task N: [Nome do Componente de UI] (Figma)

**Files:**
- Create: `caminho/exato/do/componente`
- Create: `caminho/exato/dos/estilos` (se aplicável)
**Assets:** `<diretório de assets do projeto>/` — implementer may download & create icon/image files here as needed (exact files unknown at plan time)
**Type:** UI Component | UI Screen
**Depends on:** none | Task X, Task Y

**Figma:**
- **File Key:** `<file_key>`
- **Node ID:** `<id>`
- **Breakpoints:** <breakpoint_name> (<width>px), ...
- **Medidas de aceite:** container max-width `<valor>`, margens laterais `<valor>`, gaps `<valor>`, colunas `<n>`, min/max de `<peça>` no breakpoint `<breakpoint_name>` (do Contrato de Layout)

**Design System:** <!-- só em tasks UI Component, quando o design tem Árvore de Componentes de DS -->
- **Veredito:** implementar | atualizar | derivar
- **Base:** `<nome no código>` (`<import path>`) — só para `derivar` (a base que o wrapper compõe) e `atualizar` (o set estendido); omita nos outros casos
- **Compõe de:** `<nome>` (`<import path>`), `<nome>` (`<import path>`) — só para composto (`implementar` com filhos em Depende de); omita quando não compõe nada
- **Variantes:** <todas as variantes/estados que o ORIGINAL declara>
- **Anotações do Figma:** <anotações do Dev Mode relevantes a este nó — estados interativos, animação, a11y, regras de conteúdo — verbatim>
- **Estados a cobrir:** <linhas de `## Casos de Borda & Estados` que este componente é dono>

- [ ] Implement using the Figma implementer workflow
```

**Building the Figma block:**
- **Type:** `UI Component` para tasks de componente (Layer 1); `UI Screen` para tasks de tela e esqueleto (Layer 0/Layer 2). Ver "Task Type & Roteamento" acima.
- **Bloco `**Design System:**`** — copie da linha correspondente da `## Árvore de Componentes de DS`: `Veredito`, `Nome no código`, `Depende de` (vira `Base` para `derivar`/`atualizar` e `Compõe de` para composto, cada filho com o import path que a árvore registrou), e todas as variantes que o original declara. **Omita o bloco inteiro** quando o design não tem a árvore — o implementer então executa o procedimento de veredito ausente, que checa a existência antes de construir qualquer coisa. Nunca escreva um veredito que a árvore não confirmou.
- **Anotações do Figma / Estados a cobrir** — recorte de `### Anotações de Design` e `## Casos de Borda & Estados` só o que pertence a este nó. Sem isso, estados interativos, animações e regras de a11y confirmadas com o usuário no design não chegam a ninguém: o implementer vê apenas o frame default. Uma anotação sem task dona é informação perdida.
- **File Key / Node ID — para tasks `UI Component`, use as coordenadas DO ORIGINAL.** A `## Árvore de Componentes de DS` dá o veredito e a `C#`; as coordenadas vêm da entrada `C#` correspondente em `### Componentes` (`Arquivo do original` + `Node ID do original`). **Nunca** o node-id de uma instância listada no `Conteúdo` de uma `T#`, e nunca o File Key da tela quando a entrada `C#` aponta para outro arquivo (o do DS, por exemplo).

  Isso é a diferença entre o implementer ler o componente e ler *uma configuração* dele. A instância mostra só a variante que aquela tela usou; o original declara todos os eixos. Apontar para a instância entrega um componente permanentemente mais pobre que o real — e como ele *funciona* na tela que originou a task, ninguém percebe.

- **File Key / Node ID — para tasks `UI Screen`** (Layer 0 e Layer 2): aí sim são os da tela, do `## Recursos do Figma`, porque o alvo é o frame.
- **Breakpoints:** Include only the breakpoints relevant to this task's component (not all breakpoints in the design)
- **Medidas de aceite:** Apenas quando `## Contrato de Layout` está presente. Copie a(s) linha(s) da tabela do Contrato de Layout relevantes ao frame/breakpoints desta task (container max-width, margens laterais, gaps, nº de colunas, min/max por peça). Se `## Contrato de Layout` estiver ausente, omita esta linha — não invente medidas.
- **Assets:** Set `<project assets dir>` to the codebase's existing asset convention when you can tell it from the design doc or project layout (e.g. `src/assets`, `public/`); otherwise leave the generic note — the implementer auto-detects and falls back to a sensible default. Never enumerate individual asset files here: which icons/images a design needs is only knowable at implement time (no Figma MCP calls at plan time). The `**Assets:**` line is a *grant + hint* that assets may be created outside the `**Files:**` list — omitting it does not block the implementer, it just loses the hint.

**Mixed plans:** Figma and non-Figma tasks coexist in the same plan with standard dependency handling. A feature might have Tasks 1-2 as data models (standard TDD), Tasks 3-5 as UI components (Figma), and Task 6 as integration (standard TDD).

## Remember
- Toda task carrega `**Type:**` (`UI Screen` | `UI Component` | `UI Logic` | `Backend` | `General`) — determina dispatch e verificação; plan sem `**Type:**` cai no heurístico legado
- Exact file paths always
- Describe behavior and edge cases completely (not just "add validation") — but never include code snippets
- Exact commands with expected output
- DRY, YAGNI, TDD-inspired (standard tasks), frequent commits
- Figma tasks: no TDD, no code snippets, single workflow step — the subagent prompt owns the how
- Figma tasks: include the `**Assets:**` grant line (project assets dir); never enumerate individual asset files — they're only knowable at implement time
- When Figma resources exist: always split design (Figma task) and logic (standard task) into separate tasks. Design first, logic depends on it
- Any task touching styling (CSS, Tailwind, layout, disposition) MUST be a Figma task when Figma resources are available
- Quando `## Contrato de Layout` está presente: gere a task de esqueleto (Layer 0) dona do container por tela — Layer 2 DEPENDE dela, Layer 1 roda em paralelo, e o esqueleto vem primeiro
- Componentes (Layer 1) são PROIBIDOS de setar max-width, centralização ou margens de página — regra imposta em runtime pelo implementer e checada pelo `code-quality-reviewer`
- **Toda** task de UI (Layer 0/Layer 1/Layer 2) carrega no bloco `**Figma:**` as Medidas de aceite (do Contrato de Layout) para os breakpoints relevantes — Layer 0 incluída
- A `## Árvore de Componentes de DS` é a autoridade sobre quais componentes precisam de task: `Importar` **não** gera task (vira import path na task de tela); `Implementar`/`Atualizar`/`Derivar` geram task `UI Component` com o bloco `**Design System:**` preenchido
- Toda task `UI Component` carrega veredito, base/compõe-de com import paths, variantes e fonte do catálogo — sem isso o implementer não sabe se deve importar, estender, derivar ou construir, e construir do zero um componente que já existe é o pior resultado possível
- Anotações do Figma e casos de borda são recortados por nó nas tasks de UI — o que não tem task dona não é implementado por ninguém

## Required Sub-Skills

**REQUIRED:** Dispatch @"plan-reviewer (agent)" after writing each plan chunk.

- Announce: "Usando o plan-reviewer para validar o plano."
- Dispatch @"plan-reviewer (agent)":
  - Paste the **full chunk content** and the **spec sections relevant to that chunk** (the requirements/telas/componentes the chunk implements) directly into the prompt
  - Instruct explicitly: "Review only from the content pasted here — do NOT re-read design.md or plan.md from disk." (Each chunk reviewer that re-ingests both full artifacts costs hundreds of KB of redundant reads.)
- If issues found: fix and re-dispatch (max 5 iterations, then surface to human)
- After approval: proceed to next chunk or completion

## Plan Review Loop

After completing each chunk of the plan:

1. Dispatch @"plan-reviewer (agent)":
   - Provide: chunk content pasted inline + the spec sections relevant to the chunk (not file paths to re-read)
2. If Issues Found:
   - Fix the issues in the chunk
   - Re-dispatch reviewer for that chunk
   - Repeat until Approved
3. If Approved: proceed to next chunk (or completion if last chunk)

**Chunk boundaries:** Use `## Chunk N: <name>` headings to delimit chunks. Each chunk should be ≤1000 lines and logically self-contained.

**Review loop guidance:**
- Same agent that wrote the plan fixes it (preserves context)
- If loop exceeds 5 iterations, surface to human for guidance
- Reviewers are advisory - explain disagreements if you believe feedback is incorrect

## Completion

After saving the plan:

1. Update `state.yaml` to add `plan.md` to the plan phase's artifacts list
2. Append `artifact_created` event to `history.yaml`
3. Tell the user: "Fase plan concluída. Rode `/afyapowers:next` para avançar para **implement**."
