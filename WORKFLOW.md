# WORKFLOW.md - Documentacao Completa do afyapowers

> **afyapowers** e um plugin de workflow deterministico e baseado em fases (phase-gated) para IDEs com IA (Claude Code, Cursor, Gemini, GitHub Copilot). Ele impoe um fluxo de desenvolvimento estruturado em 5 fases com estado persistente em YAML, artefatos em Markdown e auditoria completa.

---

## Sumario

- [1. Visao Geral do Sistema](#1-visao-geral-do-sistema)
- [2. As 5 Fases do Workflow](#2-as-5-fases-do-workflow)
  - [2.1 Fase 1: Design](#21-fase-1-design)
  - [2.2 Fase 2: Plan](#22-fase-2-plan)
  - [2.3 Fase 3: Implement](#23-fase-3-implement)
  - [2.4 Fase 4: Review](#24-fase-4-review)
  - [2.5 Fase 5: Complete](#25-fase-5-complete)
- [3. Diagrama de Transicao de Fases](#3-diagrama-de-transicao-de-fases)
- [4. Sistema de Estado](#4-sistema-de-estado)
- [5. Comandos](#5-comandos)
- [6. Hook de Sessao](#6-hook-de-sessao)
- [7. Templates de Artefatos](#7-templates-de-artefatos)
- [8. Integracoes Externas](#8-integracoes-externas)
- [9. Skills Standalone (Cross-Cutting)](#9-skills-standalone-cross-cutting)
- [10. Padroes de Subagentes](#10-padroes-de-subagentes)
- [11. Distribuicao Multi-IDE](#11-distribuicao-multi-ide)

---

## 1. Visao Geral do Sistema

O afyapowers transforma o desenvolvimento assistido por IA em um processo **deterministico e auditavel**. Ao inves de permitir que o agente de IA escreva codigo livremente, o plugin impoe uma progressao sequencial obrigatoria:

```
Design --> Plan --> Implement --> Review --> Complete
```

### Principios Fundamentais

1. **Progressao Deterministica** — As fases sao sequenciais e obrigatorias. Nao e possivel pular fases nem retroceder.
2. **Artefatos Persistentes** — Cada fase produz um artefato obrigatorio (arquivo Markdown) que deve existir antes de avancar para a proxima fase.
3. **Auditoria Completa** — Todos os eventos sao registrados em `history.yaml` com timestamp e contexto.
4. **Gates de Transicao** — O comando `/afyapowers:next` valida se a fase atual foi concluida antes de permitir o avanco.
5. **Execucao Paralela em Ondas** — A fase de implementacao usa ordenacao topologica para despachar tarefas independentes em ondas paralelas.
6. **Auto-Revisao** — Subagentes realizam auto-revisao durante a implementacao; preocupacoes sao coletadas para a fase de review.
7. **Continuidade de Sessao** — Um hook de sessao restaura o contexto automaticamente ao iniciar uma nova sessao.

### Estrutura de Diretorios (Runtime)

Quando uma feature e criada, o seguinte diretorio e inicializado no projeto:

```
.afyapowers/
  .gitignore                          # Criado automaticamente; ignora: features/active
  features/
    active                            # Slug da feature ativa (gitignored)
    <AAAA-MM-DD>-<slug>/
      state.yaml                      # Estado da feature (mutavel durante o workflow)
      history.yaml                    # Timeline de eventos (imutavel, append-only)
      artifacts/
        design.md                     # Saida da Fase 1
        plan.md                       # Saida da Fase 2
        implementation-concerns.md    # Saida opcional da Fase 3
        review.md                     # Saida da Fase 4
        completion.md                 # Saida da Fase 5
```

---

## 2. As 5 Fases do Workflow

### 2.1 Fase 1: Design

**Skill:** `design` (`src/skills/design/SKILL.md`)
**Objetivo:** Transformar ideias em especificacoes tecnicas completas atraves de dialogo colaborativo.

#### Gate de Entrada

1. Ler `.afyapowers/features/active` para obter a feature ativa
2. Ler `.afyapowers/features/<feature>/state.yaml` e confirmar que `current_phase` e `design`

#### Processo Detalhado

**Passo 1 — Explorar Contexto do Projeto**
- Verificar arquivos, documentacao, commits recentes para entender o codebase

**Passo 2 — Descoberta JIRA (Opcional, Baseada em Oferta)**
- Oferecer ao usuario a opcao de fornecer uma chave de issue JIRA (ex: `PROJ-123`)
- Se fornecida: buscar via `mcp__claude_ai_Atlassian__getJiraIssue()`
- Extrair: resumo, tipo de issue, descricao, criterios de aceitacao, issues vinculadas, labels/componentes
- Apresentar resumo para confirmacao do usuario

**Passo 3 — Descoberta Figma (Opcional, Baseada em Gatilho)**
- Verificar se a solicitacao do usuario contem palavras-chave de UI: "page", "landing page", "screen", "view", "layout", "header", "footer", "navbar", "sidebar", "UI component", "form", "modal", "dialog", "card", "hero", "section", "banner", "responsive", "breakpoint", "mobile", "desktop", "dashboard", "panel", "widget"
- Se detectado: perguntar "Essa feature possui designs no Figma? Se sim, compartilhe a(s) URL(s)."
- Se URLs fornecidas:
  - Extrair file key e node ID da URL
  - Chamar `get_metadata()` no no raiz (unica chamada MCP permitida nesta fase)
  - Construir Node Map (profundidade 0: Page, profundidade 1: Screens/Sections, profundidade 2: Components/Elements)
  - Classificar nos em: **Componentes Reutilizaveis** (COMPONENT/COMPONENT_SET) e **Telas** (FRAMES com filhos)
  - Inferir breakpoints a partir dos nomes e dimensoes dos frames de nivel superior

**Passo 4 — Perguntas de Esclarecimento**
- Se dados JIRA/Figma disponiveis: perguntas no estilo confirmacao (confirmar, corrigir ou estender requisitos)
- Caso contrario: perguntas de esclarecimento uma por vez
- Foco: proposito, restricoes, criterios de sucesso

**Passo 5 — Propor 2-3 Abordagens**
- Apresentar com trade-offs e recomendacao

**Passo 6 — Apresentar Design Completo**
- Requisitos e restricoes
- Abordagem escolhida e arquitetura
- Fluxo de dados, interfaces, tratamento de erros
- Estrategia de testes, dependencias
- Incluir `## JIRA Context` se JIRA foi consultado
- Incluir `## Figma Resources` se designs Figma foram fornecidos

**Passo 7 — Loop de Revisao da Especificacao**
- Despachar subagente `spec-document-reviewer` (ate 5 iteracoes)
- Se problemas encontrados: corrigir e re-despachar
- Se loop exceder 5 iteracoes: escalar para o usuario

**Passo 8 — Gate de Aprovacao do Usuario**
- Solicitar ao usuario que revise a especificacao escrita antes de prosseguir

#### Artefato Produzido

`.afyapowers/features/<feature>/artifacts/design.md`

#### Criterios de Conclusao

- Especificacao de design escrita e revisada pelo subagente spec-reviewer
- Usuario aprova a especificacao escrita
- `design.md` salvo em artifacts
- `state.yaml` atualizado: `phases.design.artifacts` inclui `design.md`
- Evento registrado: `artifact_created` em `history.yaml`

---

### 2.2 Fase 2: Plan

**Skill:** `writing-plans` (`src/skills/writing-plans/SKILL.md`)
**Objetivo:** Decompor o design em tarefas de implementacao com grafos de dependencia e precisao a nivel de arquivo.

#### Gate de Entrada

1. Ler `.afyapowers/features/active` para obter a feature ativa
2. Confirmar que `current_phase` e `plan`
3. Ler o design de `.afyapowers/features/<feature>/artifacts/design.md`

#### Processo Detalhado

**Passo 1 — Verificacao de Escopo**
- Se a especificacao cobre multiplos subsistemas independentes, quebrar em planos separados

**Passo 2 — Definicao de Estrutura de Arquivos**
- Mapear arquivos que serao criados ou modificados com suas responsabilidades

**Passo 3 — Inferencia de Tarefas Figma (se design contem `## Figma Resources`)**

Nenhuma chamada MCP e feita nesta fase — tudo e inferido a partir do Node Map do design.

- **Camada 1 — Componentes Reutilizaveis:** Cada COMPONENT/COMPONENT_SET no Node Map se torna uma tarefa
  - Unico node ID por tarefa
  - Sem dependencias
  - Formato: "Nome do Componente (Figma)"
- **Camada 2 — Telas:** Cada FRAME no Node Map se torna uma tarefa
  - Unico node ID por tarefa
  - Depende das tarefas da Camada 1 cujos componentes sao filhos daquele frame
  - Formato: "Nome da Tela (Figma)"
- Validacao: Cada COMPONENT/COMPONENT_SET deve ter sua propria tarefa da Camada 1 (nunca mesclar em tarefa de tela)

**Passo 4 — Criacao de Tarefas Padrao (nao-Figma)**
- Inspiradas em TDD com passos (Red, Green, Refactor)
- Sem trechos de codigo; descrever comportamento em linguagem natural
- Cada passo: teste falhando -> verificacao da falha -> implementacao -> verificacao do teste passando -> commit

**Passo 5 — Declaracao de Dependencias**
- Toda tarefa deve ter linha `**Depends on:**`
- Usar `none` ou `Task N, Task M` (separados por virgula)
- Validacao: sem sobreposicao de arquivos entre tarefas parallelizaveis

**Passo 6 — Estrutura do Documento do Plano**
- Cabecalho com: nome da feature, objetivo (uma frase), arquitetura (2-3 frases), tech stack
- Blocos de tarefa com:
  - `### Task N: [nome]`
  - `**Files:**` (Create/Modify/Test com caminhos exatos)
  - `**Depends on:**`
  - Para Figma: bloco `**Figma:**` com file key, node ID, breakpoints
  - Passos (checkboxes: `- [ ]`)

**Passo 7 — Loop de Revisao do Plano**
- Despachar subagente `plan-document-reviewer` para cada chunk (ate 1000 linhas)
- Maximo de 5 iteracoes; escalar para o usuario se excedido

#### Artefato Produzido

`.afyapowers/features/<feature>/artifacts/plan.md`

#### Criterios de Conclusao

- Todas as tarefas definidas com arquivos e dependencias
- Plano revisado e aprovado pelo subagente plan-document-reviewer
- `plan.md` salvo em artifacts
- `state.yaml` atualizado: `phases.plan.artifacts` inclui `plan.md`
- Evento registrado: `artifact_created` em `history.yaml`

---

### 2.3 Fase 3: Implement

**Skill:** `implementing` (`src/skills/implementing/SKILL.md`)
**Sub-Skill:** `subagent-driven-development` (`src/skills/subagent-driven-development/SKILL.md`)
**Objetivo:** Executar o plano de implementacao via despacho de subagentes em ondas com auto-revisao e coleta de preocupacoes.

#### Gate de Entrada

1. Ler `.afyapowers/features/active`
2. Confirmar que `current_phase` e `implement`
3. Ler plano de `.afyapowers/features/<feature>/artifacts/plan.md`
4. Ler design de `.afyapowers/features/<feature>/artifacts/design.md` para contexto
5. Validar: se todas as tarefas ja estao completas, sugerir `/afyapowers:next`

#### Algoritmo de Execucao em Ondas (Wave Execution)

A implementacao usa o skill `subagent-driven-development` que implementa o seguinte algoritmo:

**1. Parsear Tarefas do Plano**
- Extrair numero da tarefa, dependencias, lista de arquivos, status (`pending`, `in-flight`, `completed`, `needs-retry`)

**2. Verificar Dependencias Circulares**
- Reportar e parar se ciclo detectado

**3. Computar Conjunto Pronto (Ready Set)**
- Uma tarefa esta pronta se: status e `pending`/`needs-retry` E todas as dependencias estao `completed`

**4. Validar Sobreposicao de Arquivos**
- Verificar pares de tarefas prontas
- Se duas tarefas compartilham arquivos, remover uma do conjunto pronto (mover para espera)

**5. Despachar (com Rate-Limiting Figma)**
- Classificar tarefas: Figma (contem secao `**Figma:**`) vs Nao-Figma
- Despachar todas as tarefas nao-Figma
- Despachar ate **4 tarefas Figma por onda** (Figma limita a 15 req/min; 4 tarefas x 3 chamadas = 12)
- Usar template de prompt correto:
  - Tarefa Figma: `skills/implementing/implement-figma-design.md`
  - Tarefa padrao: `skills/implementing/implementer-prompt.md`

**6. Processar Resultados**
- **DONE:** Marcar `completed`, atualizar checkbox para `- [x]`
- **DONE_WITH_CONCERNS:** Armazenar lista de preocupacoes, marcar `completed` (exceto se preocupacao indica tarefa quebrada -> tratar como BLOCKED)
- **NEEDS_CONTEXT:** Apresentar pergunta ao usuario, marcar `needs-retry`, continuar com outras tarefas
- **BLOCKED:** Avaliar (mais contexto, modelo mais capaz, quebrar tarefa, ou escalar), marcar `needs-retry`

**7. Repetir**
- Voltar ao Passo 3, recomputar conjunto pronto, continuar ate todas as tarefas `completed`

#### Coleta de Preocupacoes (Concerns)

Apos todas as tarefas completarem, se houve algum resultado `DONE_WITH_CONCERNS`, as preocupacoes sao escritas em:
- `.afyapowers/features/<feature>/artifacts/implementation-concerns.md`
- Formato: lista de cada tarefa com suas preocupacoes
- Nota: coleta limpa a cada re-execucao (sobrescreve, nao acumula)

#### Artefato Produzido

- `plan.md` atualizado (todos os checkboxes marcados `- [x]`)
- `implementation-concerns.md` (opcional, se houve preocupacoes)

#### Criterios de Conclusao

- Todos os checkboxes do plano marcados `- [x]`
- Todas as tarefas completadas (nenhuma pendente ou needs-retry)
- `state.yaml` atualizado
- Evento registrado em `history.yaml` (se arquivo de preocupacoes criado)

---

### 2.4 Fase 4: Review

**Skill:** `reviewing` (`src/skills/reviewing/SKILL.md`)
**Objetivo:** Realizar revisao de codigo abrangente em 2 etapas (conformidade com especificacao + qualidade de codigo).

#### Gate de Entrada

- Confirmar que `current_phase` e `review`

#### Processo Detalhado

**Passo 1 — Coletar Contexto**
- Ler `design.md` — requisitos
- Ler `plan.md` — plano de implementacao
- Ler `implementation-concerns.md` se existir — preocupacoes sinalizadas durante implementacao
- Obter git diff das mudancas da feature

**Passo 2 — Etapa 1: Revisao de Conformidade com Especificacao**
- Despachar subagente `spec-reviewer` (prompt: `skills/implementing/spec-reviewer-prompt.md`)
- Fornecer: especificacao de design como "o que foi solicitado", resumo da implementacao como "o que foi construido", diff de codigo, Areas Prioritarias (de concerns ou "Nenhuma preocupacao sinalizada.")
- Iterar ate 5 vezes ate estar conforme com a especificacao
- Usuario corrige problemas de codigo durante a fase de revisao se lacunas forem encontradas

**Passo 3 — Etapa 2: Revisao de Qualidade de Codigo**
- Despachar subagente `code-quality-reviewer` (prompt: `skills/reviewing/code-reviewer.md`)
- Fornecer: resumo da implementacao, referencia ao plano, SHAs base/head, descricao, Areas Prioritarias (de concerns)
- Categorizar achados por severidade:
  - **Critical** — deve corrigir (bloqueia aprovacao)
  - **Important** — deve corrigir (bloqueia aprovacao)
  - **Minor** — anotar para depois (nao bloqueia)
- Iterar ate 5 vezes ate todos os problemas Critical/Important resolvidos

**Passo 4 — Produzir Artefato de Revisao**
- Usar template `templates/review.md`
- Preencher: achados de conformidade e resolucoes, achados de qualidade e resolucoes
- **Veredicto:** "Approved" (somente se ambas as revisoes passam) ou "Changes Requested"

#### Artefato Produzido

`.afyapowers/features/<feature>/artifacts/review.md`

#### Gate Critico

O veredicto **DEVE** ser "Approved" para que `/afyapowers:next` aceite a transicao. Se o veredicto for "Changes Requested", o usuario deve corrigir os problemas e re-executar a revisao.

#### Criterios de Conclusao

- Revisao de conformidade aprovada pelo subagente reviewer
- Revisao de qualidade aprovada pelo subagente reviewer
- `review.md` salvo com Veredicto: "Approved"
- `state.yaml` atualizado: `phases.review.artifacts` inclui `review.md`
- Evento registrado em `history.yaml`

---

### 2.5 Fase 5: Complete

**Skill:** `completing` (`src/skills/completing/SKILL.md`)
**Sub-Skill:** `auto-documentation` (`src/skills/auto-documentation/SKILL.md`)
**Objetivo:** Executar verificacao final, merge/PR, gerar resumo de conclusao e atualizar documentacao.

#### Gate de Entrada

- Confirmar que `current_phase` e `complete`

#### Processo Detalhado

**Passo 1 — Verificacao Final**
- Executar suite de testes do projeto — todos os testes devem passar
- Verificar que nao ha mudancas nao commitadas
- Ler `review.md` — confirmar que veredicto e "Approved"
- Reportar problemas ou prosseguir

**Passo 2 — Apresentar Opcoes ao Usuario**
- **Opcao 1:** Merge local (`git checkout main && git merge`)
- **Opcao 2:** Criar PR (`git push -u origin && gh pr create`)
- **Opcao 3:** Manter como esta (deixar branch para depois)
- **Opcao 4:** Descartar (confirmar antes)

**Passo 3 — Executar Escolha do Usuario**
- Realizar operacoes git conforme selecionado

**Passo 4 — Atualizar Documentacao (SUB-SKILL OBRIGATORIO)**
- Invocar skill `auto-documentation`
- Processo:
  - Executar `git diff` contra branch default ou ultimo commit
  - Se nao ha mudancas: pular documentacao
  - Verificar se `docs/afyapowers/` existe; criar se nao
  - Escanear docs existentes em `docs/afyapowers/` para correspondencia por area de dominio
  - Atualizar doc correspondente ou criar novo (usar `templates/feature-doc.md`)
  - Adicionar entrada de changelog no inicio (mais recente primeiro)
  - Commitar mudancas de documentacao

**Passo 5 — Produzir Artefato de Conclusao**
- Usar template `templates/completion.md`
- Preencher: resumo da entrega, arquivos/componentes alterados, como testar, info de PR/merge
- Salvar em `.afyapowers/features/<feature>/artifacts/completion.md`

#### Artefatos Produzidos

- `.afyapowers/features/<feature>/artifacts/completion.md`
- Documentacao em `docs/afyapowers/` (documentacao viva)

#### Criterios de Conclusao

- Testes passando
- Feature merged ou PR criado
- Documentacao gerada
- `completion.md` salvo
- `state.yaml` atualizado: `phases.complete.artifacts` inclui `completion.md`
- Evento registrado em `history.yaml`
- Feature marcada como `completed` na proxima chamada a `/afyapowers:next`

---

## 3. Diagrama de Transicao de Fases

```
                    /afyapowers:new
                         |
                         v
                  +-----------+
                  |  DESIGN   |  --> Artefato: design.md
                  +-----------+
                         |
                    Gate: design.md existe
                         |
                  /afyapowers:next
                         |
                         v
                  +-----------+
                  |   PLAN    |  --> Artefato: plan.md
                  +-----------+
                         |
                    Gate: plan.md existe
                         |
                  /afyapowers:next
                         |
                         v
                  +-----------+
                  | IMPLEMENT |  --> Artefato: plan.md (atualizado)
                  +-----------+     + implementation-concerns.md (opcional)
                         |
                    Gate: todos os checkboxes - [x]
                         |
                  /afyapowers:next
                         |
                         v
                  +-----------+
                  |  REVIEW   |  --> Artefato: review.md
                  +-----------+
                         |
                    Gate: review.md existe E Veredicto = "Approved"
                         |
                  /afyapowers:next
                         |
                         v
                  +-----------+
                  | COMPLETE  |  --> Artefato: completion.md
                  +-----------+     + docs/afyapowers/*.md
                         |
                    Gate: completion.md existe
                         |
                  /afyapowers:next
                         |
                         v
                  [Feature Concluida]
```

### Mapeamento Fase -> Skill

| Transicao | Skill Invocado |
|-----------|----------------|
| `/afyapowers:new` -> Design | `design` |
| Design -> Plan | `writing-plans` |
| Plan -> Implement | `implementing` (que invoca `subagent-driven-development`) |
| Implement -> Review | `reviewing` |
| Review -> Complete | `completing` (que invoca `auto-documentation`) |

---

## 4. Sistema de Estado

### 4.1 state.yaml

Arquivo mutavel que rastreia o progresso da feature:

```yaml
feature: "<nome-da-feature>"
status: "active | completed | aborted"
created_at: "<timestamp-ISO-8601>"
current_phase: "design | plan | implement | review | complete"
phases:
  design:
    status: "pending | in_progress | completed | aborted"
    started_at: "<timestamp>"
    completed_at: "<timestamp>"       # preenchido ao concluir
    artifacts: ["design.md"]
  plan:
    status: "pending | in_progress | completed | aborted"
    started_at: "<timestamp>"
    completed_at: "<timestamp>"
    artifacts: ["plan.md"]
  implement:
    status: "pending | in_progress | completed | aborted"
    started_at: "<timestamp>"
    completed_at: "<timestamp>"
    artifacts: ["plan.md"]            # atualizado in-place com checkmarks
  review:
    status: "pending | in_progress | completed | aborted"
    started_at: "<timestamp>"
    completed_at: "<timestamp>"
    artifacts: ["review.md"]
  complete:
    status: "pending | in_progress | completed | aborted"
    started_at: "<timestamp>"
    completed_at: "<timestamp>"
    artifacts: ["completion.md"]
```

### 4.2 history.yaml

Log de eventos imutavel (append-only). Nunca e editado — apenas recebe novas entradas:

```yaml
events:
  - timestamp: "<ISO-8601>"
    event: "feature_created"
    phase: "design"
    command: "/afyapowers:new"
    details: "Feature criada: <nome>"

  - timestamp: "<ISO-8601>"
    event: "phase_started"
    phase: "design"
    command: "/afyapowers:new"
    details: "Fase design iniciada"

  - timestamp: "<ISO-8601>"
    event: "artifact_created"
    phase: "design"
    command: "/afyapowers:next"
    details: "Artefato design.md criado"

  - timestamp: "<ISO-8601>"
    event: "phase_completed"
    phase: "design"
    command: "/afyapowers:next"
    details: "Fase design concluida"

  - timestamp: "<ISO-8601>"
    event: "feature_completed"
    phase: "complete"
    command: "/afyapowers:next"
    details: "Feature concluida"
```

**Tipos de evento:**
- `feature_created` — Feature foi criada
- `phase_started` — Uma fase foi iniciada
- `artifact_created` — Um artefato foi produzido
- `phase_completed` — Uma fase foi concluida
- `feature_completed` — A feature inteira foi concluida
- `feature_aborted` — A feature foi abortada

### 4.3 Arquivo active

O arquivo `.afyapowers/features/active` contem apenas o slug do diretorio da feature ativa (ex: `2026-04-01-minha-feature`). Este arquivo e **gitignored** para evitar conflitos entre desenvolvedores.

---

## 5. Comandos

O afyapowers disponibiliza 8 comandos slash. A nomenclatura varia por IDE:

| Claude Code | Cursor | GitHub Copilot | Descricao |
|-------------|--------|----------------|-----------|
| `/afyapowers:new` | `/afyapowers-new` | `/new` | Iniciar nova feature |
| `/afyapowers:next` | `/afyapowers-next` | `/next` | Avancar para proxima fase |
| `/afyapowers:status` | `/afyapowers-status` | `/status` | Ver status da feature |
| `/afyapowers:history` | `/afyapowers-history` | `/history` | Ver timeline de eventos |
| `/afyapowers:switch` | `/afyapowers-switch` | `/switch` | Trocar feature ativa |
| `/afyapowers:features` | `/afyapowers-features` | `/features` | Listar todas as features |
| `/afyapowers:abort` | `/afyapowers-abort` | `/abort` | Abortar feature atual |
| `/afyapowers:component` | `/afyapowers-component` | `/component` | Componente Figma standalone |

### 5.1 /afyapowers:new — Iniciar Nova Feature

**Arquivo fonte:** `src/commands/new.md`

**Processo:**
1. Obter nome e breve descricao da feature do usuario
2. Gerar slug a partir do nome (minusculas, espacos -> hifens, maximo 50 caracteres)
3. Criar diretorio: `.afyapowers/features/<AAAA-MM-DD>-<slug>/`
4. Criar subdiretorio `artifacts/`
5. Inicializar `state.yaml` (`current_phase: design`, `status: active`)
6. Inicializar `history.yaml` com eventos `feature_created` e `phase_started`
7. Escrever nome do diretorio em `.afyapowers/features/active`
8. Invocar skill **design** para iniciar a fase de design

### 5.2 /afyapowers:next — Avancar Fase

**Arquivo fonte:** `src/commands/next.md`

**Processo:**
1. Ler `.afyapowers/features/active` para obter a feature ativa
2. Validar conclusao da fase atual:
   - **design:** `design.md` deve existir
   - **plan:** `plan.md` deve existir
   - **implement:** Todos os checkboxes em `plan.md` devem ser `- [x]`
   - **review:** `review.md` deve existir E Veredicto deve ser "Approved"
   - **complete:** `completion.md` deve existir
3. Se fase terminal (complete):
   - Marcar `phases.complete.status` = `completed`
   - Marcar feature `status` = `completed`
   - Registrar eventos `phase_completed` + `feature_completed`
   - Informar usuario: "Feature concluida!"
   - Parar
4. Caso contrario:
   - Marcar fase atual `status` = `completed`, definir `completed_at`
   - Marcar proxima fase `status` = `in_progress`, definir `started_at`
   - Atualizar `current_phase`
   - Registrar eventos `phase_completed` + `phase_started`
   - Invocar skill da proxima fase

### 5.3 /afyapowers:status — Ver Status

**Arquivo fonte:** `src/commands/status.md`

**Saida:**
- Nome da feature, status (active/completed/aborted), data de criacao
- Fase atual com status
- Todas as 5 fases com indicadores visuais e artefatos:
  - Concluida
  - Em andamento
  - Pendente
  - Abortada
- Se na fase implement: progresso de tarefas (X de Y concluidas)

### 5.4 /afyapowers:switch — Trocar Feature

**Arquivo fonte:** `src/commands/switch.md`

**Processo:**
1. Se argumento fornecido: buscar feature correspondente por slug ou nome
2. Caso contrario: listar todas as features nao-abortadas, pedir ao usuario para escolher
3. Verificar que feature nao esta abortada
4. Escrever nome do diretorio da feature em `.afyapowers/features/active`
5. Exibir status da feature

### 5.5 /afyapowers:features — Listar Features

**Arquivo fonte:** `src/commands/features.md`

**Saida:** Tabela de todas as features com fase, status e data de criacao. Marcar feature ativa.

### 5.6 /afyapowers:history — Timeline de Eventos

**Arquivo fonte:** `src/commands/history.md`

**Saida:** Timeline cronologica de eventos do `history.yaml` da feature ativa.

### 5.7 /afyapowers:abort — Abortar Feature

**Arquivo fonte:** `src/commands/abort.md`

**Processo:**
1. Ler feature ativa
2. Confirmar com usuario (irreversivel!)
3. Marcar feature `status` = `aborted`
4. Marcar fase atual em `in_progress` como `status` = `aborted`
5. Registrar evento `feature_aborted`
6. Limpar `.afyapowers/features/active`

### 5.8 /afyapowers:component — Componente Figma Standalone

**Arquivo fonte:** `src/commands/component.md`

**Processo:** Invocar skill `figma-component` para desenvolvimento de componente Figma fora do workflow de 5 fases. Veja [secao 9.7](#97-figma-component---componente-figma-standalone) para detalhes completos.

---

## 6. Hook de Sessao

### session-start

**Arquivo fonte:** `src/hooks/session-start` (script bash)
**Configuracao:** `src/hooks/hooks.json` (trigger: `SessionStart`)

**Objetivo:** Restaurar o contexto da feature ativa automaticamente ao iniciar uma nova sessao do agente de IA.

#### Fluxo de Execucao

1. **Verificar existencia do diretorio `.afyapowers/`**
   - Se nao existe: retornar JSON vazio `{}`

2. **Tentar ler `.afyapowers/features/active`**
   - Validar que aponta para um diretorio de feature existente
   - Se invalido: limpar e prosseguir para fallback

3. **Fallback: Escanear features em andamento**
   - Percorrer todos os `state.yaml` procurando `status: in_progress`
   - Pular features abortadas
   - Se exatamente 1 feature em andamento: usar automaticamente
   - Se multiplas em andamento: injetar mensagem pedindo ao usuario para usar `/afyapowers:switch`
   - Se nenhuma: retornar JSON vazio

4. **Se feature ativa encontrada:**
   - Extrair de `state.yaml`: nome da feature, fase atual, status, data de criacao
   - Contar artefatos no diretorio `artifacts/`
   - Se na fase implement: contar tarefas concluidas vs total a partir de `plan.md`
   - Injetar `additionalContext` no agente contendo:
     - Nome da feature ativa e data de criacao
     - Fase atual e progresso de tarefas
     - Lista de artefatos disponiveis
     - **LEMBRETE:** "Nao avance fases autonomamente. Quando a fase atual estiver completa, sugira `/afyapowers:next`."

#### Saida JSON

```json
{
  "additionalContext": "Voce tem uma feature ativa: \"Minha Feature\" (iniciada 2026-04-01)\nFase atual: implement (3 de 5 tarefas concluidas)\nArtefatos: design.md, plan.md\n\nIMPORTANT: Nao avance fases autonomamente. Sugira /afyapowers:next quando completo."
}
```

---

## 7. Templates de Artefatos

Os templates ficam em `src/templates/` e sao copiados para a distribuicao de cada IDE.

### 7.1 design.md

Template para o artefato da fase de Design. Secoes:

| Secao | Obrigatoria | Descricao |
|-------|-------------|-----------|
| JIRA Context | Nao | Issue key, resumo, tipo, requisitos, criterios de aceitacao, issues vinculadas |
| Problem Statement | Sim | Qual problema estamos resolvendo e por que |
| Requirements | Sim | Requisitos chave descobertos durante o design |
| Constraints | Sim | Restricoes tecnicas, de negocio ou de tempo |
| Approaches Considered | Sim | 2-3 abordagens com trade-offs |
| Chosen Approach | Sim | Qual abordagem e por que |
| Architecture | Sim | Componentes e como interagem |
| Data Flow | Sim | Como os dados fluem pelo sistema |
| API / Interface Changes | Sim | Interfaces novas ou modificadas |
| Error Handling | Sim | Modos de falha e como sao tratados |
| Testing Strategy | Sim | O que testar e como |
| Dependencies | Sim | Dependencias externas ou pre-requisitos |
| Open Questions | Sim | Qualquer coisa nao resolvida |
| Figma Resources | Nao | URL do arquivo, file key, breakpoints, Node Map (Componentes Reutilizaveis + Telas) |

### 7.2 plan.md

Template para o artefato da fase de Plan. Estrutura:

- **Cabecalho:** Goal (uma frase), Architecture (2-3 frases), Tech Stack
- **Blocos de tarefa padrao:**
  - `### Task N: [nome]`
  - `**Files:**` com Create/Modify/Test
  - `**Depends on:**` com numeros de tarefas ou `none`
  - Passos com checkboxes (`- [ ]` pendente, `- [x]` concluido)
- **Blocos de tarefa Figma:**
  - Mesma estrutura + bloco `**Figma:**` com File Key, Node ID, Breakpoints
  - Passo unico: `- [ ] Implement using the Figma implementer workflow and commit`

### 7.3 review.md

Template para o artefato da fase de Review. Secoes:

- **Spec Compliance Review** — Tabela de achados (Severidade, Achado, Resolucao)
- **Code Quality Review** — Tabela de achados (Severidade, Achado, Resolucao)
- **Verdict** — "Approved" ou "Changes Requested"

### 7.4 completion.md

Template para o artefato da fase de Complete. Secoes:

- **Summary** — O que foi entregue
- **Changes Made** — Arquivos e componentes chave alterados
- **How to Test** — Passos para verificar que a feature funciona
- **PR / Merge Info** — Link do PR, nome da branch, detalhes de merge

### 7.5 feature-doc.md

Template para documentacao viva gerada pelo sub-skill `auto-documentation`. Secoes:

- **Overview** — Descricao breve do que a feature faz e por que existe
- **Business Rules** — Regras de negocio (opcional)
- **Usage** — Como usar a feature (configuracao, API, comandos)
- **Technical Details** — Architecture, Key Files, Data Flow
- **Changelog** — Entradas adicionadas no inicio (mais recente primeiro), nunca remove entradas antigas

---

## 8. Integracoes Externas

### 8.1 Integracao JIRA

A integracao com JIRA acontece exclusivamente na **Fase 1 (Design)**.

**Fluxo:**
1. O skill de design **oferece** ao usuario a opcao de fornecer uma chave de issue JIRA
2. Se fornecida, busca a issue via MCP: `mcp__claude_ai_Atlassian__getJiraIssue()`
3. Extrai:
   - Resumo e tipo da issue
   - Descricao completa
   - Criterios de aceitacao
   - Issues vinculadas (blockers, relacionadas)
   - Labels e componentes
4. Apresenta resumo ao usuario para confirmacao
5. Inclui secao `## JIRA Context` no artefato `design.md`

**Importante:** A integracao e baseada em oferta (o agente pergunta), nao e automatica.

### 8.2 Integracao Figma

A integracao com Figma acontece em 3 fases do workflow, com diferentes niveis de acesso:

#### Na Fase de Design (Acesso Limitado)

- **Gatilho:** Deteccao de palavras-chave de UI na solicitacao do usuario
- **Chamada MCP permitida:** Apenas `get_metadata()` no no raiz (unica chamada)
- **Chamadas MCP PROIBIDAS:** `get_screenshot`, `get_design_context`, `get_variable_defs`
- **Saida:** Node Map com Componentes Reutilizaveis e Telas no `design.md`
- **Breakpoints:** Inferidos a partir dos nomes e dimensoes dos frames de nivel superior

#### Na Fase de Plan (Sem Acesso MCP)

- **Nenhuma chamada MCP** — tudo e inferido a partir do Node Map do `design.md`
- **Camada 1:** Cada COMPONENT/COMPONENT_SET se torna uma tarefa independente
- **Camada 2:** Cada FRAME (tela) se torna uma tarefa dependendo das tarefas da Camada 1
- **Validacao:** Cada componente tem sua propria tarefa (nunca mesclar em tarefa de tela)

#### Na Fase de Implement (Acesso Completo via Subagentes)

- **Subagentes fazem as chamadas:** `get_design_context`, `get_screenshot`, `get_variable_defs`
- **Limite de concorrencia:** Maximo 4 tarefas Figma por onda
- **Motivo do limite:** Figma limita a 15 requisicoes/minuto; 4 tarefas x 3 chamadas = 12 requisicoes (margem segura)
- **Prompt de tarefa Figma:** `skills/implementing/implement-figma-design.md`

---

## 9. Skills Standalone (Cross-Cutting)

Alem dos skills vinculados as fases do workflow, o afyapowers inclui skills autonomos que podem ser usados independentemente ou sao invocados como sub-habilidades durante o workflow.

### 9.1 Test-Driven Development (TDD)

**Arquivo:** `src/skills/test-driven-development/SKILL.md`

**Principio Central:** "Se voce nao assistiu o teste falhar, voce nao sabe se ele testa a coisa certa."

**Lei de Ferro:** NENHUM CODIGO DE PRODUCAO SEM UM TESTE FALHANDO PRIMEIRO

**Ciclo RED-GREEN-REFACTOR:**

1. **RED** — Escrever um teste minimo mostrando o comportamento esperado
   - Verificar que ele falha (obrigatorio)
   - Confirmar que a razao da falha e a feature faltando, nao um erro de digitacao
2. **GREEN** — Escrever o codigo mais simples possivel para passar no teste
   - Sem over-engineering
   - Sem melhorias "ja que estou aqui"
3. **REFACTOR** — Limpar (apos green)
   - Remover duplicacao, melhorar nomes, extrair helpers
   - Manter testes verdes; nao adicionar comportamento

**Quando e usado:** Em todas as tarefas padrao (nao-Figma) da fase de implementacao. Cada passo de tarefa no plano segue o padrao: escrever teste -> ver falhar -> implementar -> ver passar -> commitar.

**Red Flags (sinais de violacao):**
- Codigo antes do teste
- Teste passa imediatamente (nao viu RED)
- Nao consegue explicar por que o teste falhou
- Racionalizar "so dessa vez"
- Multiplos fixes de uma vez (impede isolamento)

### 9.2 Systematic Debugging

**Arquivo:** `src/skills/systematic-debugging/SKILL.md`

**Principio Central:** "SEMPRE encontre a causa raiz antes de tentar correcoes. Correcoes de sintomas sao falhas."

**Lei de Ferro:** NENHUMA CORRECAO SEM INVESTIGACAO DA CAUSA RAIZ PRIMEIRO

**Quatro Fases Obrigatorias:**

1. **Investigacao da Causa Raiz**
   - Ler mensagens de erro completamente
   - Reproduzir de forma consistente
   - Verificar mudancas recentes (`git diff`, commits)
   - Coletar evidencias em sistemas multi-componente (logs nos limites)
   - Rastrear fluxo de dados de tras para frente

2. **Analise de Padroes**
   - Encontrar exemplos funcionais no codebase
   - Ler implementacoes de referencia completamente
   - Identificar todas as diferencas do codigo funcionando
   - Entender dependencias e premissas

3. **Hipotese e Teste**
   - Formar uma unica hipotese especifica
   - Testar minimamente (uma variavel)
   - Verificar antes de continuar
   - Se nao sabe: dizer que nao sabe, pedir ajuda

4. **Implementacao**
   - Criar caso de teste falhando primeiro (usar TDD)
   - Implementar correcao unica (tratar causa raiz)
   - Verificar que a correcao resolve o problema
   - Se 3+ correcoes falharam: questionar a arquitetura (discussao necessaria antes da tentativa #4)

**Red Flags:**
- "Correcao rapida por enquanto"
- "So tenta X"
- "Nao entendo totalmente, mas pode funcionar"
- "Mais uma correcao" (apos 2+)
- Cada fix revela novo problema em outro lugar

### 9.3 Verification Before Completion

**Arquivo:** `src/skills/verification-before-completion/SKILL.md`

**Principio Central:** "Afirmar que o trabalho esta completo sem verificacao e desonestidade, nao eficiencia."

**Lei de Ferro:** NENHUMA AFIRMACAO DE CONCLUSAO SEM EVIDENCIA DE VERIFICACAO FRESCA

**A Funcao Gate:**
1. **IDENTIFICAR:** Qual comando prova esta afirmacao?
2. **EXECUTAR:** Executar o comando COMPLETO (fresco, completo)
3. **LER:** Saida completa, verificar exit code, contar falhas
4. **VERIFICAR:** A saida confirma a afirmacao?
5. **SO ENTAO:** Fazer a afirmacao

**Padrao correto vs incorreto:**
```
Correto:  [Executar testes] [Ver: 34/34 passam] "Todos os testes passam"
Errado:   "Deve estar funcionando agora" / "Parece correto"
```

**Red Flags:**
- Palavras como "deveria", "provavelmente", "parece que"
- Expressar satisfacao antes da verificacao
- Prestes a commitar/push/PR sem verificacao

### 9.4 Using Git Worktrees

**Arquivo:** `src/skills/using-git-worktrees/SKILL.md`

**Objetivo:** Criar workspaces isolados compartilhando o mesmo repositorio.

**Prioridade de Selecao de Diretorio:**
1. Verificar existencia de `.worktrees/` ou `worktrees/`
2. Verificar `CLAUDE.md` por preferencia
3. Perguntar ao usuario (local ao projeto vs global)

**Verificacao de Seguranca:**
- Para diretorio local: verificar que esta no `.gitignore` (usar `git check-ignore`)
- Se nao esta ignorado: adicionar ao `.gitignore` e commitar

**Passos de Criacao:**
1. Detectar nome do projeto: `basename "$(git rev-parse --show-toplevel)"`
2. Criar worktree: `git worktree add <path> -b <branch>`
3. Executar setup do projeto (auto-detectar: npm, cargo, poetry, go mod)
4. Verificar baseline limpo (executar testes)

### 9.5 Dispatching Parallel Agents

**Arquivo:** `src/skills/dispatching-parallel-agents/SKILL.md`

**Padrao:** Um agente por dominio de problema independente, despacho em paralelo.

**Quando USAR:**
- 3+ arquivos de teste falhando com causas raiz diferentes
- Multiplos subsistemas quebrados independentemente
- Cada problema pode ser entendido independentemente
- Sem estado compartilhado entre investigacoes

**Quando NAO USAR:**
- Falhas sao relacionadas (corrigir uma pode corrigir outras)
- Precisa do estado completo do sistema
- Agentes interfeririam entre si

**Diferenca do subagent-driven-development:** Este skill e para investigacao/resolucao ad-hoc de problemas independentes. O SDD e especificamente para execucao de tarefas de um plano com grafos de dependencia.

### 9.6 Auto-Documentation

**Arquivo:** `src/skills/auto-documentation/SKILL.md`

**Objetivo:** Gerar e atualizar documentacao viva de features apos a implementacao.

**Quando invocado:** Durante a fase de Complete (Passo 4), apos merge/PR, antes do artefato de conclusao.

**Processo:**
1. Coletar mudancas: `git diff` contra branch default ou ultimo commit
2. Se nao ha mudancas: pular documentacao
3. Preparar diretorio `docs/afyapowers/` (criar se nao existe)
4. Escanear docs existentes (extrair nome da feature, Overview, Key Files)
5. Relacionar mudancas com docs existentes por area de dominio (semantico, nao por heuristica de keywords)
6. Atualizar doc correspondente ou criar novo:
   - Reescrever secoes (Overview, Business Rules, Usage, Technical Details) para refletir estado atual
   - Preservar Changelog (append-only, mais recente primeiro)
7. Commitar: `git add docs/afyapowers/ && git commit -m "docs: update docs/afyapowers/<feature>.md"`

**Fontes de contexto (prioridade):** Artefatos afyapowers (design/plan/review) -> git diff -> docs existentes

### 9.7 Figma Component — Componente Figma Standalone

**Arquivo:** `src/skills/figma-component/SKILL.md`
**Gatilho:** Comando `/afyapowers:component` OU solicitacao do usuario com palavra-chave de acao + "component" + URL Figma

**Objetivo:** Desenvolver um unico componente Figma fora do workflow de 5 fases.

**Protocolo de 9 Tarefas em 3 Fases:**

#### Fase 1 — Parse & Validate (Chamadas MCP: get_metadata, get_code_connect_map)
- T1: Parsear URL, extrair file key e node ID
- T2: Verificar disponibilidade do MCP
- T3: Validar que o no e COMPONENT ou COMPONENT_SET
- T4: Verificar Code Connect para implementacao existente

#### Fase 2 — Dependencies & Location (Sem chamadas MCP)
- T5: Escanear metadados armazenados para dependencias INSTANCE
- T6: Fazer referencia cruzada com mapa Code Connect
- T7: Detectar local de saida (glob para diretorios de componentes), framework (package.json, configs), e Storybook

#### Fase 3 — Present & Confirm (Sem chamadas MCP)
- T8: Mostrar resultados pre-voo: nome do componente, variantes, dependencias, diretorio sugerido, framework, Storybook
- T9 (apos confirmacao): Despachar subagente implementador
  - Subagente faz suas proprias chamadas MCP (`get_variable_defs`, `get_screenshot`, `get_design_context`)
  - Inclui auto-revisao contra dados do Figma

**Hard Stops (paradas obrigatorias):**
- URL malformada
- `node-id` faltando
- Tipo do no nao e COMPONENT/COMPONENT_SET
- Componente ja existe no codebase

**Restricao critica:** NUNCA chamar `get_design_context`/`get_screenshot`/`get_variable_defs` nas Fases 1/2 — apenas o subagente na Fase 3.

### 9.8 Subagent-Driven Development (SDD)

**Arquivo:** `src/skills/subagent-driven-development/SKILL.md`

**Principio Central:** "Subagente fresco por tarefa + auto-revisao + coleta de preocupacoes = iteracao rapida com revisao de qualidade diferida"

**Integracao:** Invocado pelo skill `implementing` para executar todas as tarefas do plano.

**Algoritmo de Execucao em Ondas:**
1. Parsear tarefas com dependencias
2. Verificar ciclos
3. Computar conjunto pronto (pending/needs-retry com deps concluidas)
4. Validar sobreposicao de arquivos
5. Despachar em ondas:
   - Todas as tarefas nao-Figma (sem limite)
   - Tarefas Figma (max 4 por onda, respeitando rate limits)
6. Esperar resultados
7. Processar: DONE -> concluido, DONE_WITH_CONCERNS -> armazenar preocupacoes + concluido, NEEDS_CONTEXT -> apresentar ao usuario, BLOCKED -> avaliar
8. Repetir ate todas concluidas

**Selecao de Modelo:** Usar modelo menos poderoso para tarefas mecanicas, padrao para integracao, mais capaz para arquitetura/design/revisao.

---

## 10. Padroes de Subagentes

O afyapowers faz uso extensivo de subagentes ao longo do workflow. Aqui esta um mapa completo:

### 10.1 Subagentes por Fase

| Fase | Subagente | Funcao | Max Iteracoes |
|------|-----------|--------|---------------|
| Design | `spec-document-reviewer` | Revisar design para completude e consistencia | 5 |
| Plan | `plan-document-reviewer` | Revisar plano para granularidade, dependencias, caminhos de arquivo | 5 |
| Implement | Subagentes de tarefa (1 por tarefa) | Implementar tarefa individual + auto-revisao | N/A (por onda) |
| Implement (Figma) | Subagente Figma implementador | Implementar componente/tela Figma + auto-revisao | Max 4 por onda |
| Review | `spec-reviewer` | Verificar se implementacao corresponde ao design | 5 |
| Review | `code-quality-reviewer` | Verificar qualidade, padroes, casos extremos | 5 |
| Complete | Auto-documentacao | Gerar/atualizar docs vivos | N/A |
| Standalone | Figma component implementador | Implementar componente Figma unitario | N/A |

### 10.2 Padrao de Comunicacao

Todos os subagentes de implementacao retornam um status padronizado:

| Status | Significado | Acao do Orquestrador |
|--------|-------------|---------------------|
| `DONE` | Tarefa concluida com sucesso | Marcar checkbox `- [x]` |
| `DONE_WITH_CONCERNS` | Concluida, mas com preocupacoes | Armazenar concerns, marcar concluida |
| `NEEDS_CONTEXT` | Precisa de informacao adicional | Apresentar ao usuario, marcar needs-retry |
| `BLOCKED` | Nao consegue prosseguir | Avaliar opcoes, marcar needs-retry |

### 10.3 Subagentes de Revisao

Os subagentes de revisao (spec-reviewer e code-quality-reviewer) usam um ciclo iterativo:

1. Despachar subagente com contexto completo
2. Receber achados categorizados por severidade
3. Se Critical/Important encontrados: usuario corrige, re-despachar
4. Se apenas Minor: anotar, aprovar
5. Maximo 5 iteracoes; escalar ao usuario se excedido

---

## 11. Distribuicao Multi-IDE

### 11.1 Pipeline Source -> Distribution

Todo o conteudo canonico vive em `src/`. O script `sync.sh` transforma em distribuicoes especificas por IDE em `dist/`:

```
src/                          dist/
  config/<agent>.json    -->    <agent>/
  commands/*.md          -->    <agent>/commands/
  skills/*/SKILL.md      -->    <agent>/skills/
  templates/*.md         -->    <agent>/templates/
  hooks/                 -->    <agent>/hooks/
  manifests/<agent>/     -->    <agent>/  (manifesto na raiz)
```

### 11.2 Sistema de Frontmatter

Cada comando e skill possui um arquivo `.frontmatter.yaml` paralelo ao `.md`, com chaves de nivel superior para cada IDE:

```yaml
claude:
  name: afyapowers:new
  description: Start a New Feature
cursor:
  name: afyapowers-new
  description: Start a New Feature
github-copilot:
  name: new
  description: Start a New Feature
```

O `sync.sh` extrai a secao do agente alvo e converte em bloco YAML frontmatter (`---`) prefixado ao arquivo de saida.

### 11.3 Configuracao por IDE

| IDE | Config | Prefixo de Comando | Prefixo de Skill | Manifesto |
|-----|--------|--------------------|--------------------|-----------|
| Claude Code | `src/config/claude.json` | Nenhum (`:`) | Nenhum | `.claude-plugin/plugin.json` |
| Cursor | `src/config/cursor.json` | `afyapowers-` | `afyapowers-` | `.cursor-plugin/plugin.json` |
| Gemini | `src/config/gemini.json` | Nenhum | Nenhum | Nenhum |
| GitHub Copilot | `src/config/github-copilot.json` | Nenhum | Nenhum | `plugin.json` |

### 11.4 Usando o sync.sh

```bash
./sync.sh                  # Sincronizar todos os agentes
./sync.sh claude           # Sincronizar agente especifico
./sync.sh --clean          # Limpar diretorios de saida antes de sincronizar
./sync.sh cursor --clean   # Limpar + agente especifico
```

**Processo interno:**
1. Parsear argumentos (agentes especificos, flag `--clean`)
2. Para cada agente:
   - Carregar config de `src/config/<agent>.json`
   - Processar comandos: injetar frontmatter, aplicar prefixo
   - Processar skills: injetar frontmatter, copiar arquivos de suporte
   - Copiar templates (se habilitado no config)
   - Copiar hooks (se habilitado, preservar permissoes de execucao)
   - Copiar manifesto (conforme caminho no config)

**Requisitos:** `jq` (com fallback para Python 3 se indisponivel)

---

## Apendice: Referencia Rapida

### Todos os Skills do Projeto

| # | Skill | Tipo | Arquivo |
|---|-------|------|---------|
| 1 | `design` | Fase | `src/skills/design/SKILL.md` |
| 2 | `writing-plans` | Fase | `src/skills/writing-plans/SKILL.md` |
| 3 | `implementing` | Fase | `src/skills/implementing/SKILL.md` |
| 4 | `reviewing` | Fase | `src/skills/reviewing/SKILL.md` |
| 5 | `completing` | Fase | `src/skills/completing/SKILL.md` |
| 6 | `subagent-driven-development` | Cross-cutting | `src/skills/subagent-driven-development/SKILL.md` |
| 7 | `test-driven-development` | Cross-cutting | `src/skills/test-driven-development/SKILL.md` |
| 8 | `systematic-debugging` | Cross-cutting | `src/skills/systematic-debugging/SKILL.md` |
| 9 | `verification-before-completion` | Cross-cutting | `src/skills/verification-before-completion/SKILL.md` |
| 10 | `using-git-worktrees` | Cross-cutting | `src/skills/using-git-worktrees/SKILL.md` |
| 11 | `dispatching-parallel-agents` | Cross-cutting | `src/skills/dispatching-parallel-agents/SKILL.md` |
| 12 | `auto-documentation` | Cross-cutting | `src/skills/auto-documentation/SKILL.md` |
| 13 | `figma-component` | Standalone | `src/skills/figma-component/SKILL.md` |

### Todos os Comandos

| # | Comando (Claude) | Arquivo |
|---|------------------|---------|
| 1 | `/afyapowers:new` | `src/commands/new.md` |
| 2 | `/afyapowers:next` | `src/commands/next.md` |
| 3 | `/afyapowers:status` | `src/commands/status.md` |
| 4 | `/afyapowers:history` | `src/commands/history.md` |
| 5 | `/afyapowers:switch` | `src/commands/switch.md` |
| 6 | `/afyapowers:features` | `src/commands/features.md` |
| 7 | `/afyapowers:abort` | `src/commands/abort.md` |
| 8 | `/afyapowers:component` | `src/commands/component.md` |

### Todos os Templates

| # | Template | Fase | Arquivo |
|---|----------|------|---------|
| 1 | `design.md` | Design | `src/templates/design.md` |
| 2 | `plan.md` | Plan | `src/templates/plan.md` |
| 3 | `review.md` | Review | `src/templates/review.md` |
| 4 | `completion.md` | Complete | `src/templates/completion.md` |
| 5 | `feature-doc.md` | Auto-docs | `src/templates/feature-doc.md` |
