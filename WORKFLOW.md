# 🚀 afyapowers — Guia do Workflow

O **afyapowers** e um plugin que organiza o desenvolvimento assistido por IA em 5 fases bem definidas. Em vez de deixar a IA escrever codigo livremente, ele guia voce por um caminho estruturado — do design ate a entrega — com documentacao automatica e rastreamento completo.

Funciona com **Claude Code**, **Cursor**, **Gemini** e **GitHub Copilot**.

---

## ⚡ Inicio Rapido

O fluxo basico e simples:

```
/afyapowers:new  →  🎨 Design  →  📋 Plan  →  ⚙️ Implement  →  🔍 Review  →  ✅ Complete
                         ↓             ↓             ↓              ↓             ↓
                    design.md      plan.md     codigo pronto    review.md   completion.md
```

1. Use `/afyapowers:new` para iniciar uma feature
2. Trabalhe em cada fase ate concluir
3. Use `/afyapowers:next` para avancar para a proxima fase
4. Repita ate chegar ao final

> 💡 **Dica:** Cada fase produz um artefato (arquivo Markdown). Voce so avanca quando o artefato da fase atual estiver pronto.

---

## 📑 Sumario

- [1. 🔄 As 5 Fases do Workflow](#1--as-5-fases-do-workflow)
  - [🎨 Fase 1: Design](#-fase-1-design)
  - [📋 Fase 2: Plan](#-fase-2-plan)
  - [⚙️ Fase 3: Implement](#️-fase-3-implement)
  - [🔍 Fase 4: Review](#-fase-4-review)
  - [✅ Fase 5: Complete](#-fase-5-complete)
- [2. 🗺️ Diagrama de Transicao](#2-️-diagrama-de-transicao)
- [3. 💾 Sistema de Estado](#3--sistema-de-estado)
- [4. 📦 Comandos](#4--comandos)
- [5. 🔄 Hook de Sessao](#5--hook-de-sessao)
- [6. 📄 Templates de Artefatos](#6--templates-de-artefatos)
- [7. 🔗 Integracoes (JIRA e Figma)](#7--integracoes-jira-e-figma)
- [8. 🧩 Skills Extras](#8--skills-extras)
- [9. 🤖 Subagentes](#9--subagentes)
- [10. 🖥️ Distribuicao Multi-IDE](#10-️-distribuicao-multi-ide)
- [11. 📚 Referencia Rapida](#11--referencia-rapida)

---

## 1. 🔄 As 5 Fases do Workflow

### Principios que guiam o workflow

| Principio | O que significa |
|-----------|----------------|
| **Progressao sequencial** | As fases seguem uma ordem fixa. Nao da pra pular nem voltar. |
| **Artefatos obrigatorios** | Cada fase gera um documento. Sem ele, voce nao avanca. |
| **Auditoria completa** | Tudo que acontece fica registrado com data e contexto. |
| **Verificacao antes de avancar** | O comando `/afyapowers:next` checa se a fase foi realmente concluida. |
| **Execucao paralela** | Na implementacao, tarefas independentes rodam ao mesmo tempo. |
| **Auto-revisao** | Subagentes revisam o proprio trabalho durante a implementacao. |
| **Continuidade de sessao** | Se voce fechar e abrir a IDE, o plugin restaura onde voce parou. |

### 📁 Estrutura de diretorios

Quando voce cria uma feature, o plugin inicializa esta estrutura no seu projeto:

```
.afyapowers/
  features/
    active                            ← qual feature esta ativa agora (gitignored)
    2026-04-07-minha-feature/
      state.yaml                      ← estado atual (fase, status, timestamps)
      history.yaml                    ← historico de eventos (so cresce, nunca edita)
      artifacts/
        design.md                     ← documento da fase Design
        plan.md                       ← documento da fase Plan
        implementation-concerns.md    ← preocupacoes levantadas na implementacao (opcional)
        review.md                     ← documento da fase Review
        completion.md                 ← documento da fase Complete
```

---

### 🎨 Fase 1: Design

**Objetivo:** Transformar sua ideia em uma especificacao tecnica completa, atraves de conversa colaborativa.

**O que acontece:**

1. **Exploracao do projeto** — O agente analisa seu codebase, documentacao e commits recentes para entender o contexto

2. **Contexto JIRA** *(opcional)* — O agente oferece a opcao de vincular uma issue JIRA. Se voce fornecer a chave (ex: `PROJ-123`), ele puxa resumo, descricao, criterios de aceitacao e issues relacionadas

3. **Contexto Figma** *(opcional)* — Se sua solicitacao envolve UI (paginas, telas, componentes visuais), o agente pergunta se ha designs no Figma. Se voce compartilhar URLs, ele extrai a estrutura de componentes e telas

4. **Perguntas de esclarecimento** — O agente faz perguntas para entender melhor o proposito, restricoes e criterios de sucesso

5. **Propostas de abordagem** — Apresenta 2-3 abordagens com trade-offs e uma recomendacao

6. **Especificacao completa** — Monta o documento com requisitos, arquitetura, fluxo de dados, interfaces, tratamento de erros e estrategia de testes

7. **Revisao automatica** — Um subagente revisor verifica a spec (ate 5 rodadas de refinamento)

8. **Sua aprovacao** — Voce revisa e aprova a especificacao antes de prosseguir

**Artefato gerado:** `artifacts/design.md`

> ⚠️ **Para avancar:** O `design.md` precisa existir e ter sido aprovado por voce.

---

### 📋 Fase 2: Plan

**Objetivo:** Decompor o design em tarefas de implementacao concretas, com dependencias e arquivos especificos.

**O que acontece:**

1. **Verificacao de escopo** — Se a spec cobre subsistemas independentes, o plano e dividido

2. **Mapeamento de arquivos** — Define quais arquivos serao criados ou modificados e suas responsabilidades

3. **Criacao de tarefas** — Cada tarefa segue o padrao TDD:
   - Escrever teste que falha → verificar a falha → implementar → verificar que passa → commitar
   - Sem trechos de codigo no plano, apenas descricoes em linguagem natural

4. **Tarefas Figma** *(se aplicavel)* — Componentes viram tarefas independentes (Camada 1), telas viram tarefas que dependem dos componentes (Camada 2)

5. **Grafo de dependencias** — Cada tarefa declara de quais outras depende, permitindo execucao paralela segura

6. **Revisao automatica** — Um subagente revisor verifica granularidade, dependencias e caminhos de arquivo

**Estrutura de cada tarefa no plano:**
```markdown
### Task N: Nome da tarefa
**Files:** Create/Modify/Test com caminhos exatos
**Depends on:** none | Task 1, Task 3
- [ ] Passo 1
- [ ] Passo 2
```

**Artefato gerado:** `artifacts/plan.md`

> ⚠️ **Para avancar:** O `plan.md` precisa existir e ter sido revisado.

---

### ⚙️ Fase 3: Implement

**Objetivo:** Executar o plano de implementacao, despachando subagentes em ondas paralelas.

**O que acontece:**

O plugin usa um algoritmo de execucao em ondas (**wave execution**):

1. **Analisa o plano** — Extrai tarefas, dependencias e status de cada uma

2. **Calcula o que esta pronto** — Uma tarefa esta pronta se todas as suas dependencias foram concluidas

3. **Verifica conflitos** — Se duas tarefas prontas mexem nos mesmos arquivos, uma espera a outra

4. **Despacha subagentes** — Cada tarefa pronta recebe um subagente dedicado que:
   - Implementa seguindo TDD (teste → codigo → refactor)
   - Faz auto-revisao do proprio trabalho
   - Reporta o resultado: sucesso, sucesso com preocupacoes, precisa de contexto, ou bloqueado

5. **Processa resultados:**
   | Resultado | O que acontece |
   |-----------|----------------|
   | ✅ Concluido | Checkbox marcado `- [x]` |
   | ⚠️ Concluido com preocupacoes | Preocupacoes anotadas para a fase de Review |
   | ❓ Precisa de contexto | Pergunta apresentada a voce |
   | 🚫 Bloqueado | Avaliacao de alternativas |

6. **Repete** ate todas as tarefas estarem concluidas

> 💡 **Sobre tarefas Figma:** No maximo 4 por onda, para respeitar o limite de requisicoes da API do Figma (15/min).

**Artefatos gerados:**
- `plan.md` atualizado (checkboxes marcados)
- `artifacts/implementation-concerns.md` *(se houve preocupacoes)*

> ⚠️ **Para avancar:** Todos os checkboxes do plano precisam estar marcados `- [x]`.

---

### 🔍 Fase 4: Review

**Objetivo:** Revisao de codigo em duas etapas — conformidade com a spec e qualidade de codigo.

**O que acontece:**

**Etapa 1 — Conformidade com a especificacao**
- Um subagente compara o que foi pedido (design.md) com o que foi construido (diff do git)
- Se houver lacunas, voce corrige antes de prosseguir
- Ate 5 rodadas de refinamento

**Etapa 2 — Qualidade de codigo**
- Outro subagente analisa padroes, qualidade, casos extremos
- Achados sao classificados por severidade:

| Severidade | Acao necessaria |
|------------|-----------------|
| 🔴 **Critical** | Corrigir obrigatoriamente (bloqueia aprovacao) |
| 🟡 **Important** | Corrigir obrigatoriamente (bloqueia aprovacao) |
| 🟢 **Minor** | Anotado para depois (nao bloqueia) |

**Artefato gerado:** `artifacts/review.md` (com veredicto: "Approved" ou "Changes Requested")

> ⚠️ **Para avancar:** O veredicto precisa ser **"Approved"**. Se for "Changes Requested", corrija os problemas e rode a revisao novamente.

---

### ✅ Fase 5: Complete

**Objetivo:** Verificacao final, merge/PR, documentacao automatica e resumo de entrega.

**O que acontece:**

1. **Verificacao final** — Testes passando, sem mudancas nao commitadas, veredicto da review e "Approved"

2. **Escolha de finalizacao** — Voce decide o que fazer com o codigo:

   | Opcao | Descricao |
   |-------|-----------|
   | 🔀 Merge local | `git checkout main && git merge` |
   | 🌐 Criar PR | `git push && gh pr create` |
   | ⏸️ Manter como esta | Deixa a branch para depois |
   | 🗑️ Descartar | Remove tudo (com confirmacao) |

3. **Documentacao automatica** — O plugin gera/atualiza docs em `docs/afyapowers/` com base nas mudancas feitas

4. **Resumo de conclusao** — Documento final com o que foi entregue, arquivos alterados, como testar e info de PR/merge

**Artefatos gerados:**
- `artifacts/completion.md`
- Documentacao em `docs/afyapowers/` (atualizada automaticamente)

> ⚠️ **Para finalizar:** Use `/afyapowers:next` uma ultima vez apos o `completion.md` existir. A feature sera marcada como concluida.

---

## 2. 🗺️ Diagrama de Transicao

```
                      /afyapowers:new
                           |
                           v
                    +-------------+
                    | 🎨 DESIGN  |  → design.md
                    +-------------+
                           |
                      design.md existe?
                           |
                     /afyapowers:next
                           |
                           v
                    +-------------+
                    |  📋 PLAN   |  → plan.md
                    +-------------+
                           |
                      plan.md existe?
                           |
                     /afyapowers:next
                           |
                           v
                    +-------------+
                    | ⚙️ IMPLEMENT|  → plan.md atualizado
                    +-------------+    + concerns.md (opcional)
                           |
                      tudo marcado - [x]?
                           |
                     /afyapowers:next
                           |
                           v
                    +-------------+
                    | 🔍 REVIEW  |  → review.md
                    +-------------+
                           |
                      veredicto = "Approved"?
                           |
                     /afyapowers:next
                           |
                           v
                    +-------------+
                    | ✅ COMPLETE |  → completion.md
                    +-------------+    + docs/afyapowers/*.md
                           |
                      completion.md existe?
                           |
                     /afyapowers:next
                           |
                           v
                   🏁 Feature Concluida!
```

### Qual skill roda em cada fase?

| Transicao | Skill usado |
|-----------|-------------|
| `/afyapowers:new` → Design | `design` |
| Design → Plan | `writing-plans` |
| Plan → Implement | `implementing` + `subagent-driven-development` |
| Implement → Review | `reviewing` |
| Review → Complete | `completing` + `auto-documentation` |

---

## 3. 💾 Sistema de Estado

O afyapowers rastreia o progresso de cada feature usando dois arquivos YAML.

### state.yaml — Estado atual

Este arquivo e atualizado conforme voce avanca pelas fases:

```yaml
feature: "minha-feature"
status: "active"                    # active | completed | aborted
created_at: "2026-04-07T10:00:00Z"
current_phase: "implement"          # em qual fase voce esta agora

phases:
  design:
    status: "completed"
    started_at: "2026-04-07T10:00:00Z"
    completed_at: "2026-04-07T11:30:00Z"
    artifacts: ["design.md"]
  plan:
    status: "completed"
    started_at: "2026-04-07T11:30:00Z"
    completed_at: "2026-04-07T12:00:00Z"
    artifacts: ["plan.md"]
  implement:
    status: "in_progress"           # esta fase esta em andamento
    started_at: "2026-04-07T12:00:00Z"
    artifacts: ["plan.md"]
  review:
    status: "pending"               # ainda nao chegou aqui
  complete:
    status: "pending"
```

### history.yaml — Historico de eventos

Log imutavel (so cresce, nunca e editado). Cada evento tem timestamp, tipo e contexto:

```yaml
events:
  - timestamp: "2026-04-07T10:00:00Z"
    event: "feature_created"
    phase: "design"
    details: "Feature criada: minha-feature"

  - timestamp: "2026-04-07T11:30:00Z"
    event: "phase_completed"
    phase: "design"
    details: "Fase design concluida"

  - timestamp: "2026-04-07T11:30:00Z"
    event: "phase_started"
    phase: "plan"
    details: "Fase plan iniciada"
```

**Tipos de evento:** `feature_created`, `phase_started`, `artifact_created`, `phase_completed`, `feature_completed`, `feature_aborted`

### Arquivo active

O arquivo `.afyapowers/features/active` contem o slug da feature ativa (ex: `2026-04-07-minha-feature`). E **gitignored** para evitar conflitos entre desenvolvedores.

---

## 4. 📦 Comandos

### Referencia rapida

| Comando | O que faz |
|---------|-----------|
| `/afyapowers:new` | 🆕 Inicia uma nova feature |
| `/afyapowers:next` | ⏭️ Avanca para a proxima fase |
| `/afyapowers:status` | 📊 Mostra o status da feature atual |
| `/afyapowers:history` | 📜 Mostra a timeline de eventos |
| `/afyapowers:switch` | 🔀 Troca a feature ativa |
| `/afyapowers:features` | 📋 Lista todas as features |
| `/afyapowers:abort` | ❌ Aborta a feature atual |
| `/afyapowers:component` | 🧩 Cria componente Figma standalone |

> 💡 **Nomes variam por IDE:** No Cursor, o prefixo e `afyapowers-` (ex: `/afyapowers-new`). No GitHub Copilot, sem prefixo (ex: `/new`).

### Detalhes de cada comando

#### 🆕 `/afyapowers:new` — Iniciar feature

1. Voce informa o nome e uma breve descricao
2. O plugin cria o diretorio da feature com `state.yaml` e `history.yaml`
3. A feature e marcada como ativa
4. A fase de Design comeca automaticamente

#### ⏭️ `/afyapowers:next` — Avancar fase

1. Verifica se a fase atual foi concluida:
   - **Design:** `design.md` existe
   - **Plan:** `plan.md` existe
   - **Implement:** todos os checkboxes marcados `- [x]`
   - **Review:** `review.md` existe com veredicto "Approved"
   - **Complete:** `completion.md` existe → feature finalizada!
2. Se tudo ok, marca a fase como concluida e inicia a proxima
3. Invoca o skill correspondente a nova fase

#### 📊 `/afyapowers:status` — Ver status

Exibe: nome da feature, fase atual, status de cada fase (com indicadores visuais), artefatos gerados e progresso de tarefas (na fase de implementacao).

#### 🔀 `/afyapowers:switch` — Trocar feature

Se voce tem multiplas features, use este comando para alternar entre elas. Pode passar o slug diretamente ou escolher de uma lista.

#### 📋 `/afyapowers:features` — Listar features

Tabela com todas as features, mostrando fase atual, status e data de criacao. A feature ativa fica destacada.

#### 📜 `/afyapowers:history` — Timeline

Exibe a timeline cronologica de eventos da feature ativa.

#### ❌ `/afyapowers:abort` — Abortar feature

Marca a feature como abortada. **Irreversivel!** O plugin pede confirmacao antes de executar.

#### 🧩 `/afyapowers:component` — Componente Figma

Cria um componente a partir do Figma **fora do workflow de 5 fases**. Util para implementar componentes isolados rapidamente. Veja a [secao de Skills Extras](#figma-component) para mais detalhes.

---

## 5. 🔄 Hook de Sessao

### O que e?

Quando voce abre uma nova sessao na IDE, o plugin automaticamente restaura o contexto da feature que voce estava trabalhando. Voce nao precisa lembrar onde parou.

### Como funciona?

1. Verifica se existe `.afyapowers/` no projeto
2. Le o arquivo `active` para encontrar a feature ativa
3. Se nao encontrar, procura features em andamento automaticamente
4. Injeta no agente: nome da feature, fase atual, progresso de tarefas e artefatos disponiveis

> 💡 **Multiplas features em andamento?** O hook pede para voce escolher com `/afyapowers:switch`.

### Exemplo do contexto injetado

```
Voce tem uma feature ativa: "Minha Feature" (iniciada 2026-04-07)
Fase atual: implement (3 de 5 tarefas concluidas)
Artefatos: design.md, plan.md
```

---

## 6. 📄 Templates de Artefatos

Os templates ficam em `src/templates/` e definem a estrutura de cada documento gerado.

### design.md

| Secao | Obrigatoria | Descricao |
|-------|:-----------:|-----------|
| JIRA Context | Nao | Issue key, resumo, criterios de aceitacao |
| Problem Statement | Sim | Qual problema e por que resolver |
| Requirements | Sim | Requisitos descobertos no design |
| Constraints | Sim | Restricoes tecnicas ou de negocio |
| Approaches Considered | Sim | 2-3 abordagens com trade-offs |
| Chosen Approach | Sim | Qual abordagem e por que |
| Architecture | Sim | Componentes e interacoes |
| Data Flow | Sim | Fluxo de dados pelo sistema |
| API / Interface Changes | Sim | Interfaces novas ou modificadas |
| Error Handling | Sim | Modos de falha e tratamento |
| Testing Strategy | Sim | O que testar e como |
| Dependencies | Sim | Dependencias externas |
| Open Questions | Sim | Pontos em aberto |
| Figma Resources | Nao | URLs, breakpoints, mapa de componentes/telas |

### plan.md

- **Cabecalho:** Objetivo (1 frase), Arquitetura (2-3 frases), Tech Stack
- **Blocos de tarefa:** Numero, nome, arquivos (Create/Modify/Test), dependencias, passos com checkboxes
- **Tarefas Figma:** Mesma estrutura + bloco com File Key, Node ID e Breakpoints

### review.md

- **Revisao de conformidade** — Tabela de achados com severidade e resolucao
- **Revisao de qualidade** — Tabela de achados com severidade e resolucao
- **Veredicto** — "Approved" ou "Changes Requested"

### completion.md

- **Summary** — O que foi entregue
- **Changes Made** — Arquivos e componentes alterados
- **How to Test** — Passos para verificar a feature
- **PR / Merge Info** — Link do PR, branch, detalhes de merge

### feature-doc.md

Template para documentacao viva (gerada automaticamente na fase Complete):
- Overview, Business Rules, Usage, Technical Details, Changelog

---

## 7. 🔗 Integracoes (JIRA e Figma)

### JIRA

A integracao com JIRA acontece **apenas na fase de Design**.

- O agente **oferece** a opcao de vincular uma issue — nao e automatico
- Se voce fornecer a chave (ex: `PROJ-123`), ele busca via MCP e extrai: resumo, descricao, criterios de aceitacao, issues vinculadas, labels e componentes
- O contexto aparece no `design.md` na secao "JIRA Context"

### Figma

O Figma e usado em 3 fases, com niveis de acesso diferentes:

| Fase | Acesso | O que acontece |
|------|--------|----------------|
| 🎨 **Design** | Limitado (so metadados) | Extrai estrutura de componentes e telas do arquivo Figma |
| 📋 **Plan** | Nenhum (usa dados do Design) | Transforma componentes em tarefas independentes e telas em tarefas dependentes |
| ⚙️ **Implement** | Completo (via subagentes) | Subagentes acessam screenshots, contexto de design e variaveis |

> 💡 **Limite de concorrencia Figma:** Maximo 4 tarefas Figma por onda de implementacao (para respeitar o rate limit de 15 requisicoes/minuto da API).

---

## 8. 🧩 Skills Extras

Alem dos skills das 5 fases, o afyapowers inclui skills autonomos que podem ser usados a qualquer momento.

### 🧪 Test-Driven Development (TDD)

**Quando usar:** Em todas as tarefas de implementacao (nao-Figma).

**Ciclo obrigatorio:**

1. 🔴 **RED** — Escreva um teste minimo que falha. Confirme que a falha e pela feature faltando, nao por erro de digitacao
2. 🟢 **GREEN** — Escreva o codigo mais simples possivel para o teste passar. Sem over-engineering
3. 🔵 **REFACTOR** — Limpe o codigo. Remova duplicacao, melhore nomes. Mantenha testes verdes

> ⚠️ **Regra de ferro:** Nenhum codigo de producao sem um teste falhando primeiro.

### 🔎 Systematic Debugging

**Quando usar:** Ao encontrar qualquer bug, falha de teste ou comportamento inesperado.

**4 etapas obrigatorias:**

1. **Investigar causa raiz** — Ler erros, reproduzir, checar mudancas recentes, rastrear fluxo de dados
2. **Analisar padroes** — Encontrar exemplos funcionais no codebase e comparar
3. **Hipotese e teste** — Uma hipotese por vez, testar de forma minima
4. **Implementar** — Criar teste falhando, corrigir causa raiz, verificar

> ⚠️ **Regra de ferro:** Nenhuma correcao sem investigacao da causa raiz primeiro.

### ✔️ Verification Before Completion

**Quando usar:** Antes de afirmar que qualquer trabalho esta concluido.

**O processo:**
1. **Identificar** — Qual comando prova a afirmacao?
2. **Executar** — Rodar o comando completo
3. **Ler** — Verificar saida, exit code, contagem de falhas
4. **Confirmar** — A saida confirma a afirmacao?
5. **So entao** — Fazer a afirmacao

> ⚠️ **Regra de ferro:** Nenhuma afirmacao de conclusao sem evidencia de verificacao.

### 🌳 Using Git Worktrees

**Quando usar:** Para criar workspaces isolados que compartilham o mesmo repositorio.

O plugin detecta automaticamente o melhor diretorio, verifica o `.gitignore`, cria o worktree com uma branch dedicada e roda o setup do projeto (npm, cargo, poetry, go mod).

### 🔀 Dispatching Parallel Agents

**Quando usar:** Para resolver multiplos problemas independentes ao mesmo tempo.

**Usar quando:**
- 3+ testes falhando com causas raiz diferentes
- Multiplos subsistemas quebrados independentemente
- Sem estado compartilhado entre investigacoes

**Nao usar quando:**
- Falhas sao relacionadas (corrigir uma pode corrigir outras)
- Agentes interfeririam entre si

### 📝 Auto-Documentation

**Quando usar:** Invocado automaticamente na fase Complete.

Gera e atualiza documentacao viva em `docs/afyapowers/` com base nas mudancas feitas. Reescreve secoes para refletir o estado atual e preserva o changelog (append-only).

### 🧩 Figma Component {#figma-component}

**Quando usar:** Para desenvolver um componente Figma isolado, fora do workflow de 5 fases. Acionado via `/afyapowers:component` ou quando voce pede um componente com URL do Figma.

**Protocolo em 3 fases:**

1. **Parse & Validate** — Extrai dados da URL, verifica se o no e um componente, checa se ja existe no codebase
2. **Dependencies & Location** — Analisa dependencias, detecta framework e diretorio de saida
3. **Present & Confirm** — Mostra resumo pre-implementacao. Apos sua confirmacao, despacha um subagente implementador

### ⚡ Subagent-Driven Development (SDD)

**Quando usar:** Invocado automaticamente na fase Implement.

Orquestra a execucao de todas as tarefas do plano usando o algoritmo de ondas: parseia tarefas → verifica ciclos → calcula o que esta pronto → valida conflitos de arquivo → despacha subagentes → processa resultados → repete.

---

## 9. 🤖 Subagentes

O afyapowers usa subagentes extensivamente. Aqui esta o mapa completo:

### Por fase

| Fase | Subagente | O que faz | Limite |
|------|-----------|-----------|--------|
| 🎨 Design | Revisor de spec | Verifica completude e consistencia do design | 5 rodadas |
| 📋 Plan | Revisor de plano | Verifica granularidade, dependencias e caminhos | 5 rodadas |
| ⚙️ Implement | Implementador (1 por tarefa) | Implementa + auto-revisao | Por onda |
| ⚙️ Implement | Implementador Figma | Implementa componente/tela Figma | Max 4/onda |
| 🔍 Review | Revisor de conformidade | Compara implementacao com spec | 5 rodadas |
| 🔍 Review | Revisor de qualidade | Analisa padroes e casos extremos | 5 rodadas |
| ✅ Complete | Auto-documentacao | Gera/atualiza docs | — |
| 🧩 Standalone | Implementador Figma | Implementa componente isolado | — |

### Comunicacao padrao

Todos os subagentes de implementacao retornam um status padronizado:

| Status | Significado | Proxima acao |
|--------|-------------|--------------|
| ✅ `DONE` | Tarefa concluida com sucesso | Marcar checkbox |
| ⚠️ `DONE_WITH_CONCERNS` | Concluida, mas com ressalvas | Anotar preocupacoes |
| ❓ `NEEDS_CONTEXT` | Falta informacao | Perguntar ao usuario |
| 🚫 `BLOCKED` | Nao consegue prosseguir | Avaliar alternativas |

### Ciclo de revisao

Os subagentes revisores (spec e qualidade) seguem este ciclo:

1. Recebem contexto completo
2. Retornam achados por severidade
3. Se Critical/Important: voce corrige, subagente reavalia
4. Se apenas Minor: aprovado
5. Maximo 5 rodadas; se exceder, escala para voce

---

## 10. 🖥️ Distribuicao Multi-IDE

### Como funciona

Todo o conteudo canonico fica em `src/`. O script `sync.sh` gera distribuicoes customizadas para cada IDE em `dist/`:

```
src/                           →    dist/<ide>/
  config/<ide>.json                   comandos com frontmatter
  commands/*.md                       skills com frontmatter
  skills/*/SKILL.md                   templates copiados
  templates/*.md                      hooks copiados
  hooks/                              manifesto na raiz
  manifests/<ide>/
```

### Frontmatter por IDE

Cada comando e skill tem um `.frontmatter.yaml` com configuracoes por IDE:

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

### Configuracao por IDE

| IDE | Prefixo de comando | Prefixo de skill | Manifesto |
|-----|---------------------|-------------------|-----------|
| Claude Code | `:` (padrao) | Nenhum | `.claude-plugin/plugin.json` |
| Cursor | `afyapowers-` | `afyapowers-` | `.cursor-plugin/plugin.json` |
| Gemini | Nenhum | Nenhum | — |
| GitHub Copilot | Nenhum | Nenhum | `plugin.json` |

### Usando o sync.sh

```bash
./sync.sh                  # Sincronizar todos os agentes
./sync.sh claude           # Sincronizar um agente especifico
./sync.sh --clean          # Limpar antes de sincronizar
./sync.sh cursor --clean   # Limpar + agente especifico
```

> 💡 **Requisito:** `jq` instalado (com fallback para Python 3 se indisponivel).

---

## 11. 📚 Referencia Rapida

### Todos os skills

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

### Todos os comandos

| # | Comando (Claude Code) | Arquivo |
|---|----------------------|---------|
| 1 | `/afyapowers:new` | `src/commands/new.md` |
| 2 | `/afyapowers:next` | `src/commands/next.md` |
| 3 | `/afyapowers:status` | `src/commands/status.md` |
| 4 | `/afyapowers:history` | `src/commands/history.md` |
| 5 | `/afyapowers:switch` | `src/commands/switch.md` |
| 6 | `/afyapowers:features` | `src/commands/features.md` |
| 7 | `/afyapowers:abort` | `src/commands/abort.md` |
| 8 | `/afyapowers:component` | `src/commands/component.md` |

### Todos os templates

| # | Template | Fase | Arquivo |
|---|----------|------|---------|
| 1 | `design.md` | Design | `src/templates/design.md` |
| 2 | `plan.md` | Plan | `src/templates/plan.md` |
| 3 | `review.md` | Review | `src/templates/review.md` |
| 4 | `completion.md` | Complete | `src/templates/completion.md` |
| 5 | `feature-doc.md` | Auto-docs | `src/templates/feature-doc.md` |
