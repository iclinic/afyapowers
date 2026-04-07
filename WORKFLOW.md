## 📘 afyapowers — Documentação Completa do Workflow

> O **afyapowers** é um plugin de workflow determinístico (*phase-gated*) para IDEs com IA (Claude Code, Cursor, Gemini, GitHub Copilot).
> Ele impõe um fluxo estruturado em **5 fases**, com estado persistente, artefatos versionados e auditoria completa.

---

## 📑 Sumário

1. [Visão Geral](#1--visão-geral-do-sistema)
2. [As 5 Fases](#2--as-5-fases-do-workflow)
3. [Diagrama de Transição](#3--diagrama-de-transição)
4. [Sistema de Estado](#4--sistema-de-estado)
5. [Comandos](#5--comandos)
6. [Hook de Sessão](#6--hook-de-sessão)
7. [Templates de Artefatos](#7--templates-de-artefatos)
8. [Integrações Externas](#8--integrações-externas)
9. [Skills Standalone](#9--skills-standalone-cross-cutting)
10. [Padrões de Subagentes](#10--padrões-de-subagentes)
11. [Distribuição Multi-IDE](#11--distribuição-multi-ide)

---

## 1. 🚀 Visão Geral do Sistema

O afyapowers transforma o desenvolvimento assistido por IA em um processo:

* determinístico
* auditável
* estruturado

### 🔁 Fluxo obrigatório

```
Design → Plan → Implement → Review → Complete
```

---

## 🧠 Princípios Fundamentais

1. **Progressão determinística**
   Fases são sequenciais e obrigatórias.

2. **Artefatos persistentes**
   Cada fase gera um documento obrigatório.

3. **Auditoria completa**
   Eventos registrados em `history.yaml`.

4. **Gates de transição**
   `/afyapowers:next` valida antes de avançar.

5. **Execução paralela controlada**
   Implementação usa ondas + dependências.

6. **Auto-revisão**
   Subagentes revisam continuamente.

7. **Continuidade de sessão**
   Contexto restaurado automaticamente.

---

## 📁 Estrutura de Diretórios

```
.afyapowers/
  features/
    active
    <data>-<slug>/
      state.yaml
      history.yaml
      artifacts/
        design.md
        plan.md
        implementation-concerns.md
        review.md
        completion.md
```

---

## 2. 🔄 As 5 Fases do Workflow

---

## 2.1 🎯 Design

**Objetivo:** transformar ideias em especificações completas.

### Processo

1. Explorar contexto do projeto
2. Descoberta JIRA (opcional)
3. Descoberta Figma (opcional)
4. Perguntas de esclarecimento
5. Propor 2–3 abordagens
6. Definir arquitetura completa
7. Revisão com subagente
8. Aprovação do usuário

### Output

```
design.md
```

### Critérios

* Documento revisado
* Usuário aprovou
* Artefato salvo

---

## 2.2 🧩 Plan

**Objetivo:** quebrar o design em tarefas executáveis.

### Processo

1. Verificar escopo
2. Definir estrutura de arquivos
3. Inferir tarefas Figma (se aplicável)
4. Criar tarefas (estilo TDD)
5. Declarar dependências
6. Estruturar documento
7. Revisão automática

### Output

```
plan.md
```

---

## 2.3 ⚙️ Implement

**Objetivo:** executar tarefas via subagentes.

### Algoritmo (Wave Execution)

1. Parse das tarefas
2. Detectar ciclos
3. Identificar tarefas prontas
4. Validar conflitos de arquivos
5. Despachar tarefas
6. Processar resultados
7. Repetir

### Resultados possíveis

* DONE
* DONE_WITH_CONCERNS
* NEEDS_CONTEXT
* BLOCKED

### Outputs

* plan.md atualizado
* implementation-concerns.md (opcional)

---

## 2.4 🔍 Review

**Objetivo:** validar qualidade e conformidade.

### Etapas

1. **Spec Compliance**
2. **Code Quality**

### Severidades

* Critical
* Important
* Minor

### Output

```
review.md
```

### Gate

```
Verdict = Approved
```

---

## 2.5 ✅ Complete

**Objetivo:** finalizar e documentar.

### Processo

1. Validar testes
2. Verificar git
3. Escolher ação:

   * merge
   * PR
   * manter
   * descartar
4. Atualizar documentação
5. Gerar completion.md

### Outputs

* completion.md
* docs/afyapowers/*

---

## 3. 🔁 Diagrama de Transição

```
Design → Plan → Implement → Review → Complete → Done
```

Cada etapa exige:

* artefato da fase anterior
* validação do estado

---

## 4. 🧾 Sistema de Estado

## state.yaml

* fase atual
* status
* timestamps
* artefatos

## history.yaml

Eventos:

* feature_created
* phase_started
* artifact_created
* phase_completed
* feature_completed
* feature_aborted

## active

Arquivo que aponta a feature atual (gitignored)

---

## 5. ⚡ Comandos

| Comando                 | Função           |
| ----------------------- | ---------------- |
| `/afyapowers:new`       | Criar feature    |
| `/afyapowers:next`      | Avançar          |
| `/afyapowers:status`    | Status           |
| `/afyapowers:history`   | Histórico        |
| `/afyapowers:switch`    | Trocar           |
| `/afyapowers:features`  | Listar           |
| `/afyapowers:abort`     | Abortar          |
| `/afyapowers:component` | Figma standalone |

---

## Fluxos de Comandos

### `/new`

* cria estrutura
* inicia Design

### `/next`

* valida fase atual
* avança
* dispara próxima skill

---

## 6. 🔌 Hook de Sessão

Executado ao iniciar sessão.

### Funções

* detectar feature ativa
* restaurar contexto
* exibir progresso

### Output

* fase atual
* tarefas concluídas
* artefatos disponíveis

⚠️ Nunca avança automaticamente.

---

## 7. 📄 Templates de Artefatos

## design.md

* problema
* requisitos
* arquitetura
* fluxo
* testes

## plan.md

* tarefas
* dependências
* arquivos

## review.md

* problemas
* resoluções
* veredito

## completion.md

* resumo
* mudanças
* instruções de teste

---

## 8. 🔗 Integrações Externas

* JIRA (contexto de issue)
* Figma (UI e componentes)
* Git / GitHub (PRs e diffs)
* Documentação automática

---

## 9. 🧠 Skills Standalone (Cross-Cutting)

* design
* writing-plans
* implementing
* reviewing
* completing
* auto-documentation
* figma-component

---

## 10. 🤖 Padrões de Subagentes

* spec-document-reviewer
* plan-document-reviewer
* spec-reviewer
* code-quality-reviewer

---

## 11. 🧩 Distribuição Multi-IDE

Compatível com:

* Claude Code
* Cursor
* GitHub Copilot
* Gemini