---
name: afyapowers-writing-plans
description: Use when the current afyapowers phase is plan — creates implementation plans from tech specs
model: claude-4-6-opus
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

Before defining Figma tasks, check if the design doc contains a `## Recursos do Figma` section with a `### Node Map`.

### Fonte de verdade dos componentes: Árvore de Componentes de DS

Antes de aplicar a inference legada (Layers 0/1/2), verifique se o design doc contém uma seção `## Árvore de Componentes de DS`.

**Quando a Árvore de DS está presente, ela é a fonte de verdade das tasks de componente** (substitui a derivação de Layer 1 a partir de **Componentes Reutilizáveis**). Cada linha da árvore carrega um **Veredito** e um **Tipo Figma**; transforme cada linha em uma task com o veredito embutido:

- **Implementar** — componente genérico construído do zero, com **todas as variantes** (`COMPONENT_SET` completo), isolado e exportado. Gera uma task de componente.
- **Importar** — o componente já existe no código e está completo (paridade "só conteúdo"). **Não gera task de implementação** — vira uma **nota** no plano (ex: sob o cabeçalho de notas ou como observação na task da tela que o consome), registrando o nome no código a reusar. Nenhum implementer é despachado para ele.
- **Atualizar** — extensão **aditiva** de um componente existente (nova variante/prop que não quebra o contrato atual). Gera uma task de componente sobre o componente existente.
- **Derivar** — **wrapper** sobre um genérico base (a instância diverge do original além de conteúdo — layout/estrutura/estilo fora de token). Gera uma task de componente que compõe o genérico base por baixo, carregando o **nome proposto** e o **genérico base como dependência**.

**Ordenação folhas→raiz:** ordene as tasks usando a coluna **Depende de** — um nó só pode virar task depois que todos os nós listados em seu "Depende de" já tiverem task (ou nota, no caso de Importar). Para um **Derivar**, o **primeiro item de "Depende de" é o genérico base**: a task do derivado depende da task/nota do genérico base antes de qualquer outra dependência.

**Mapeamento veredito/tipo de nó → `Type` de task:**

- Nó de componente ou `COMPONENT_SET` da árvore (verdicts Implementar / Atualizar / Derivar) → task **`UI Component`**. A task carrega o veredito; para **Derivar**, carrega o nome proposto (coluna "Nome no código (proposto)") e o genérico base como `**Depends on:**`.
- Composição da tela (frame raiz — as entradas de **Telas** do Node Map) → task **`UI Screen`**.
- Lógica de dados/estado sem nova superfície visual (fetch/binding, estado, validação, rota, animação) → task **`UI Logic`**.

A coluna **Task Type** da própria árvore (quando preenchida) já indica o `Type` da task — use-a; na ausência dela, derive o `Type` pelo Tipo Figma/veredito conforme o mapeamento acima.

**Validação Figma da Árvore de DS (rode antes de finalizar o plano, quando a árvore está presente):**
1. Cada nó da árvore com veredito **Implementar / Atualizar / Derivar** tem sua própria task `UI Component` (nós **Importar** viram nota, não task de implementação)
2. Nenhuma task de tela (`UI Screen`) reimplementa um componente que já tem task própria — a tela apenas compõe/consome os componentes
3. Toda task com veredito **Derivar** declara o genérico base como primeira dependência em `**Depends on:**`
4. A ordenação das tasks respeita a coluna "Depende de" (folhas→raiz): nenhuma task roda antes das tasks dos nós dos quais depende

**Legado (sem Árvore de DS):** quando o design doc **não** tem a seção `## Árvore de Componentes de DS`, mantenha o comportamento legado da inference — derive as tasks de componente a partir de **Componentes Reutilizáveis** como Layers 0/1/2 (abaixo). A árvore, quando presente, é a fonte de verdade das tasks de componente; as regras de Layer 0 (esqueleto) e Layer 2 (telas) continuam valendo em conjunto com ela.

### Inference legada por Layers (Node Map)

**If Figma Resources are present**, read the Node Map and infer task layers directly — no Figma MCP calls at planning time:

1. **Layer 0 — Esqueleto (container):** Quando o design doc tem uma seção `## Contrato de Layout`, gere uma task de esqueleto por frame raiz de tela no Node Map (uma por entrada de **Telas** que representa uma tela completa). Esta task é a **dona do container**: largura máxima, centralização, margens laterais e o ritmo (gap) entre seções — tudo derivado da geometria do frame nas linhas do Contrato de Layout correspondentes a essa tela. `**Depends on:** none`. Se `## Contrato de Layout` estiver ausente, não gere task de esqueleto — prossiga direto para Layer 1/Layer 2.

2. **Layer 1 — Reusable components:** Each entry in the Node Map's **Componentes Reutilizáveis** subsection becomes a Layer 1 task with its single node ID. No dependencies — Layer 1 tasks run **em paralelo** com a task de esqueleto (Layer 0): componentes não são donos da geometria do container, então não precisam esperar o esqueleto existir. INSTANCE nodes with `×N` count only become Layer 1 tasks when their COMPONENT definition is NOT present in the same file (external component) — otherwise the COMPONENT node itself is the Layer 1 task and the INSTANCEs are usages handled by their parent section's Layer 2 task. If **Componentes Reutilizáveis** is empty or says "(nenhum)", there are no Layer 1 tasks.

3. **Layer 2 — Screens:** Each entry in the Node Map's **Telas** subsection becomes a Layer 2 task with its single node ID. Depends on any Layer 1 tasks whose components were originally children of that frame (either as COMPONENT/COMPONENT_SET nodes extracted to Reusable Components, or as INSTANCE nodes referencing a Reusable Component) — **e também** na task de esqueleto (Layer 0) daquela tela, quando existir. O esqueleto vem primeiro: seu Passo 1 define a geometria do container vazio (max-width, centralização, margens, sem conteúdo de seções), e as tasks de tela/montagem (Layer 2) montam seu conteúdo dentro desse container.

**Granularity rule:** If a node is typed COMPONENT/COMPONENT_SET, it MUST be its own Layer 1 task. Do not merge it into a parent section's task.

**Regra de fronteira (Layer 1 vs Layer 0):** componentes (Layer 1) são **PROIBIDOS** de setar max-width, centralização ou margens de página — essas medidas pertencem exclusivamente à task de esqueleto (Layer 0). A regra é imposta em runtime pelo implementer do componente/tela e checada pelo `code-quality-reviewer`. Quando um componente precisa de **full-bleed** legítimo (ultrapassar a margem lateral), a task do componente deve usar o hook de escape exposto pelo esqueleto — nunca redefinir max-width/centralização diretamente no componente.

**Medidas de aceite em tasks de UI:** toda task de UI (Layer 1 e Layer 2) inferida a partir do Node Map deve anexar, no bloco `**Figma:**`, as **Medidas de aceite** (extraídas do `## Contrato de Layout`, apenas para os breakpoints relevantes a essa task/componente). A task de esqueleto (Layer 0) não carrega esse campo — suas medidas já estão descritas no corpo da task (ver Figma Task Structure abaixo).

Each Figma task uses the Figma Task Structure format (see below) with a single node ID and breakpoints from the design doc's `## Recursos do Figma` section.

#### Example

Given this Node Map from the design doc (assumindo que `## Contrato de Layout` está presente para as duas telas):
```
**Componentes Reutilizáveis:**
- CTA Button (node `1:4`, COMPONENT)
- Pricing Tier (node `2:10`, COMPONENT_SET)

**Telas:**
- **Hero Section** (node `1:2`, FRAME, 1440x800)
  - Card (node `1:5`, INSTANCE, componentId: `2:10`) ×3
  - Hero Title (node `1:3`, TEXT)
- **Pricing Section** (node `2:1`, FRAME, 1440x600)
  - Pricing Tier (node `2:12`, INSTANCE, componentId: `2:10`) ×1
  - Section Title (node `2:11`, TEXT)
```

Correct task output:
```
Task 1: Hero Section — Esqueleto (Layer 0) (Figma)     — Layer 0, node `1:2`, depends on: none
Task 2: Pricing Section — Esqueleto (Layer 0) (Figma)  — Layer 0, node `2:1`, depends on: none
Task 3: CTA Button (Figma)         — Layer 1, node `1:4`, depends on: none
Task 4: Pricing Tier (Figma)       — Layer 1, node `2:10`, depends on: none
Task 5: Hero Section (Figma)       — Layer 2, node `1:2`, depends on: Task 1, Task 3, Task 4
Task 6: Pricing Section (Figma)    — Layer 2, node `2:1`, depends on: Task 2, Task 4
```
↑ Tasks 1-2 (esqueleto) não têm dependências e rodam em paralelo com Tasks 3-4 (componentes). Tasks 5-6 (telas) DEPENDEM tanto do esqueleto da sua tela quanto dos componentes que contêm.

Wrong output — DO NOT do this:
```
Task 1: Hero Section (Figma)       — merges CTA Button into screen task
Task 2: Pricing Section (Figma)    — merges Pricing Tier into screen task
```
↑ Components must be their own Layer 1 tasks. Never merge them into screen tasks.

When **Componentes Reutilizáveis** is empty (e sem `## Contrato de Layout` aplicável neste exemplo):
```
Task 1: Hero Section (Figma)       — Layer 2, node `1:2`, depends on: none
Task 2: Pricing Section (Figma)    — Layer 2, node `2:1`, depends on: none
```

**Figma task validation (run before finalizing the plan):**
1. Every entry in **Componentes Reutilizáveis** has a corresponding Layer 1 task with its node ID (trivially passes if Reusable Components is empty)
2. Every entry in **Telas** has a corresponding Layer 2 task with its node ID
3. No Layer 2 task includes implementation work for a component that has its own Layer 1 task
4. Layer 2 tasks depend on Layer 1 tasks whose components were originally children of that frame (extracted COMPONENT/COMPONENT_SET or INSTANCE references)
5. Se `## Contrato de Layout` está presente, existe uma task de esqueleto (Layer 0) para cada frame raiz de tela, e a task de Layer 2 correspondente depende dela (trivially passes se Contrato de Layout estiver ausente)
6. Cada task de UI (Layer 1 e Layer 2) carrega no bloco `**Figma:**` os breakpoints e as **Medidas de aceite** (a task de esqueleto Layer 0 é isenta desse último campo — ver Figma Task Structure)

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
| **UI Screen** | Página/tela/view ou esqueleto de layout de página; composição de componentes | `figma-design-implementer` | staleness vs Contrato de Layout + `figma-token-verifier` | Sim · 4/wave |
| **UI Component** | Um componente/`COMPONENT_SET`: primitivo, genérico de DS ou derivado; todas as variantes, isolado, exportado | `figma-component-implementer` | auto-review por screenshot (+ token-verifier opcional) | Sim · 4/wave |
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

**How to identify Figma tasks:** If the component being implemented has corresponding nodes in the design doc's `## Recursos do Figma` Node Map, it is a Figma task. Backend tasks, API routes, data models, business logic, and other non-UI tasks use the standard task structure above.

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

- [ ] Implement using the Figma implementer workflow
```

**Building the Figma block:**
- **Type:** `UI Component` para tasks de componente (Layer 1, ou nós Implementar/Atualizar/Derivar da Árvore de DS); `UI Screen` para tasks de tela e esqueleto (Layer 0/Layer 2). Ver "Task Type & Roteamento" acima.
- **File Key:** Copy from the design doc's `## Recursos do Figma` section
- **Node ID:** The single node ID for this task's component from the Node Map
- **Breakpoints:** Include only the breakpoints relevant to this task's component (not all breakpoints in the design)
- **Medidas de aceite:** Apenas quando `## Contrato de Layout` está presente. Copie a(s) linha(s) da tabela do Contrato de Layout relevantes ao frame/breakpoints desta task (container max-width, margens laterais, gaps, nº de colunas, min/max por peça). Se `## Contrato de Layout` estiver ausente, omita esta linha — não invente medidas.
- **Assets:** Set `<project assets dir>` to the codebase's existing asset convention when you can tell it from the design doc or project layout (e.g. `src/assets`, `public/`); otherwise leave the generic note — the implementer auto-detects and falls back to a sensible default. Never enumerate individual asset files here: which icons/images a design needs is only knowable at implement time (no Figma MCP calls at plan time). The `**Assets:**` line is a *grant + hint* that assets may be created outside the `**Files:**` list — omitting it does not block the implementer, it just loses the hint.

**Mixed plans:** Figma and non-Figma tasks coexist in the same plan with standard dependency handling. A feature might have Tasks 1-2 as data models (standard TDD), Tasks 3-5 as UI components (Figma), and Task 6 as integration (standard TDD).

## Remember
- Toda task carrega `**Type:**` (`UI Screen` | `UI Component` | `UI Logic` | `Backend` | `General`) — determina dispatch e verificação; plan sem `**Type:**` cai no heurístico legado
- Quando `## Árvore de Componentes de DS` está presente, ela é a fonte de verdade das tasks de componente: Implementar/Atualizar/Derivar → task `UI Component`; Importar → nota (sem task); ordene folhas→raiz pela coluna "Depende de"; para Derivar, o genérico base é a primeira dependência
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
- Toda task de UI (Layer 1/Layer 2) carrega no bloco `**Figma:**` as Medidas de aceite (do Contrato de Layout) para os breakpoints relevantes

## Required Sub-Skills

**REQUIRED:** Dispatch @"plan-reviewer (agent)" after writing each plan chunk.

- Announce: "Usando o plan-reviewer para validar o plano."
- Dispatch @"plan-reviewer (agent)":
  - Provide the plan chunk content and the spec file path
- If issues found: fix and re-dispatch (max 5 iterations, then surface to human)
- After approval: proceed to next chunk or completion

## Plan Review Loop

After completing each chunk of the plan:

1. Dispatch @"plan-reviewer (agent)":
   - Provide: chunk content, path to spec document
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
