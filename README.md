# afyapowers

Um plugin de workflow de desenvolvimento determinístico, com fases controladas, para o Claude Code, fork do [superpowers](https://github.com/obra/superpowers). Aplica desenvolvimento estruturado de features com estado persistente, continuidade de sessão e auditabilidade completa.

O afyapowers se baseia nas skills do superpowers (TDD, debugging sistemático, desenvolvimento orientado a subagentes, etc.) e as adapta em um workflow de 5 fases controladas, onde cada fase produz um artefato persistente antes que a próxima possa começar.

## Instalação

```bash
claude plugin install afyapowers
```

## Início Rápido

```bash
# Iniciar uma nova feature
/afyapowers:new

# Trabalhar em cada fase, avançando com:
/afyapowers:next

# Verificar o status atual a qualquer momento
/afyapowers:status
```

## Fases do Workflow

Toda feature progride por 5 fases ordenadas:

| Fase | O que acontece | Artefato |
| ---- | -------------- | -------- |
| **Design** | Esclarecer requisitos, explorar abordagens, definir arquitetura. Opcionalmente busca contexto de issues do JIRA e designs do Figma. | `design.md` |
| **Planejamento** | Decompor o design em tarefas de implementação com grafos de dependência. Infere tarefas de componentes/telas do Figma a partir do Node Map do design. Valida que não há sobreposição de arquivos entre tarefas paralelas. | `plan.md` |
| **Implementação** | Executar tarefas via despacho de subagentes baseado em ondas com TDD. Respeita a ordem de dependência e limites de taxa do Figma (máx. 4 tarefas Figma por onda). Cada subagente faz auto-revisão e sinaliza preocupações. | `plan.md` atualizado |
| **Revisão** | Revisão de código em 2 etapas: conformidade com a spec e depois qualidade do código. Itera até 5 vezes até o veredito ser "Aprovado". | `review.md` |
| **Conclusão** | Executar suíte de testes, merge/PR/cleanup, gerar documentação viva automaticamente. | `completion.md` |

As fases são controladas — você deve completar o artefato da fase atual antes de avançar para a próxima.

## Comandos

| Comando | Descrição |
| ------- | --------- |
| `/afyapowers:new` | Iniciar um novo workflow de feature |
| `/afyapowers:next` | Avançar para a próxima fase (valida conclusão da fase atual) |
| `/afyapowers:status` | Mostrar status atual da feature e progresso da fase |
| `/afyapowers:features` | Listar todas as features e seus estados |
| `/afyapowers:switch` | Alternar o contexto da feature ativa |
| `/afyapowers:history` | Mostrar a linha do tempo completa de eventos da feature ativa |
| `/afyapowers:abort` | Abandonar a feature ativa (irreversível) |
| `/afyapowers:component` | Desenvolver um componente Figma (standalone, fora do workflow de 5 fases) |

## Integrações

### JIRA

Durante a fase de **Design**, você pode opcionalmente fornecer uma chave de issue do JIRA. O afyapowers busca o contexto da issue (resumo, descrição, critérios de aceitação) via servidor MCP do Atlassian e o incorpora na spec de design.

### Figma

A integração com o Figma abrange múltiplas fases:

- **Design** — Detecta palavras-chave relacionadas a UI e solicita URLs do Figma. Realiza uma chamada superficial de metadados para construir um Node Map (página > seção > componente, até profundidade 2).
- **Planejamento** — Infere tarefas do Figma a partir do Node Map sem chamadas MCP adicionais. Tarefas da Camada 1 cobrem componentes reutilizáveis; tarefas da Camada 2 cobrem telas que dependem deles.
- **Implementação** — Subagentes chamam `get_design_context`, `get_screenshot` e `get_variable_defs` para fidelidade total ao design. Limitado a 4 tarefas Figma por onda.

## Estrutura do Projeto

```text
.afyapowers/
  .gitignore                # Criado automaticamente; gitignore de features/active
  features/
    active                  # Slug da feature ativa atual (gitignored)
    <data>-<slug>/
      state.yaml            # Estado da feature (fase, status, timestamps)
      history.yaml          # Linha do tempo completa de eventos (imutável)
      artifacts/
        design.md           # Spec de design (requisitos + arquitetura)
        plan.md             # Plano de implementação com checkboxes
        review.md           # Achados da revisão de código e veredito
        completion.md       # Resumo de conclusão
```

### Layout do Código-Fonte

```text
src/
  commands/                 # Definições de slash commands (8 no total)
  skills/                   # Skills de fase e transversais (13 no total)
  config/                   # Configuração específica por IDE (Claude, Cursor, Gemini)
  hooks/                    # Hook de início de sessão para restauração de contexto
  manifests/                # Manifestos do plugin para Claude e Cursor
  templates/                # Templates Markdown para artefatos
```

## Continuidade de Sessão

Um hook de início de sessão detecta automaticamente a feature ativa e injeta contexto no Claude Code — fase atual, progresso das tarefas, artefatos disponíveis — para que você possa retomar o trabalho de forma transparente entre sessões.

## Skills

### Skills de Fase

- **design** — Exploração colaborativa + especificação técnica com contexto opcional de JIRA/Figma
- **writing-plans** — Criação de plano de implementação a partir da spec de design com grafos de dependência e inferência de tarefas Figma
- **implementing** — Despacho de subagentes baseado em ondas com ordenação por dependência e gates de auto-revisão
- **reviewing** — Revisão de código em 2 etapas (conformidade com spec + qualidade do código) com ciclos iterativos de correção
- **completing** — Execução da suíte de testes, merge/PR/cleanup e resumo de conclusão
- **figma-component** — Desenvolvimento standalone de componente Figma (fora do workflow de 5 fases)

### Skills Transversais

- **test-driven-development** — Ciclo RED-GREEN-REFACTOR
- **systematic-debugging** — Investigação de causa raiz antes de correções
- **verification-before-completion** — Evidência antes de afirmações
- **using-git-worktrees** — Workspaces isolados para trabalho em features
- **dispatching-parallel-agents** — Investigação paralela de problemas independentes
- **subagent-driven-development** — Subagente novo por tarefa com execução em ondas e gates de revisão
- **auto-documentation** — Geração de documentação viva após implementação

## Documentação Detalhada do Workflow

Para uma descrição completa e aprofundada de todo o workflow — incluindo gates de fase, padrões de subagentes, templates de artefatos, mecânica de hooks, integrações Figma/JIRA, skills standalone e o pipeline de distribuição multi-IDE — consulte [WORKFLOW.md](WORKFLOW.md).

## Licença

MIT
