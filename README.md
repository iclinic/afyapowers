# afyapowers

afyapowers é um plugin de workflow de desenvolvimento determinístico, derivado do [superpowers](https://github.com/obra/superpowers). Ele traz um processo estruturado para criação de features, com fases bem definidas, estado persistente, continuidade de sessão e auditabilidade total.

Baseado nas principais práticas do superpowers (como TDD, debugging sistemático e desenvolvimento orientado a subagentes), o afyapowers organiza o trabalho em 5 fases sequenciais. Cada fase só avança após a conclusão e registro do artefato correspondente, garantindo controle e rastreabilidade em todo o ciclo.

## Compatibilidade

- Claude Code
- Cursor
- GitHub Copilot

## Pré-requisitos

Antes de instalar o afyapowers, é necessário instalar o **Marketplace de DevEx da Afya**. Siga as instruções no repositório do [devex-marketplace](https://github.com/iclinic/devex-marketplace).

## Instalação

### Claude Code

> **Importante:** O comando deve ser executado **dentro** da instância do agente (com o Claude Code rodando).

```bash
/plugin install afyapowers@devex-marketplace
```

Após a instalação, execute `/reload-plugins` dentro do agente para carregar o plugin.

### Cursor

1. Abra o Cursor
2. Vá em **Settings → Plugins -> Marketplace ou Browse Marketplace**
3. Instale o plugin `afyapowers`
4. **Faça um reload do Cursor** após a instalação (obrigatório)`

### GitHub Copilot

> O comando deve ser executado **fora** da instância do agente (com o Copilot CLI sem estar rodando)

```bash
copilot plugin install afyapowers@devex-marketplace
```

## Início Rápido

### Claude Code e Copilot CLI

```bash
# Iniciar uma nova feature
/afyapowers:new

# Trabalhar em cada fase, avançando com:
/afyapowers:next

# Verificar o status atual a qualquer momento
/afyapowers:status
```

### Cursor

> No Cursor, os comandos usam `-` (hífen) ao invés de `:` (dois-pontos).

```bash
# Iniciar uma nova feature
/afyapowers-new

# Trabalhar em cada fase, avançando com:
/afyapowers-next

# Verificar o status atual a qualquer momento
/afyapowers-status
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

| Claude Code / Copilot CLI | Cursor | Descrição |
| ----------- | ------ | --------- |
| `/afyapowers:new` | `/afyapowers-new` | Iniciar um novo workflow de feature |
| `/afyapowers:next` | `/afyapowers-next` | Avançar para a próxima fase (valida conclusão da fase atual) |
| `/afyapowers:status` | `/afyapowers-status` | Mostrar status atual da feature e progresso da fase |
| `/afyapowers:features` | `/afyapowers-features` | Listar todas as features e seus estados |
| `/afyapowers:switch` | `/afyapowers-switch` | Alternar o contexto da feature ativa |
| `/afyapowers:history` | `/afyapowers-history` | Mostrar a linha do tempo completa de eventos da feature ativa |
| `/afyapowers:abort` | `/afyapowers-abort` | Abandonar a feature ativa (irreversível) |
| `/afyapowers:figma-component` | `/afyapowers-figma-component` | Desenvolver um componente Figma (standalone, fora do workflow de 5 fases) |


## Integrações

### JIRA

Durante a fase de **Design**, você pode opcionalmente fornecer uma chave de issue do JIRA. O afyapowers busca o contexto da issue (resumo, descrição, critérios de aceitação) via servidor MCP do Atlassian e o incorpora na spec de design.

### Figma

A integração com o Figma abrange múltiplas fases:

- **Design** — Detecta palavras-chave relacionadas a UI e solicita URLs do Figma. Realiza uma chamada superficial de metadados para construir um Node Map (página > seção > componente, até profundidade 2).
- **Planejamento** — Infere tarefas do Figma a partir do Node Map sem chamadas MCP adicionais. Tarefas da Camada 1 cobrem componentes reutilizáveis; tarefas da Camada 2 cobrem telas que dependem deles.
- **Implementação** — Subagentes chamam `get_design_context`, `get_screenshot` e `get_variable_defs` para fidelidade total ao design. Limitado a 4 tarefas Figma por onda.

## Configuração dos MCPs (Atlassian e Figma)

O afyapowers utiliza servidores MCP para integração com JIRA (Atlassian) e Figma. A configuração varia por IDE:

> **Importante:** Em todos os agentes (Cursor, Claude Code, Copilot CLI, etc.), ambos os MCPs vão precisar de **autenticação** antes do primeiro uso.

### Claude Code

1. Abra o Claude Code
2. Execute `/plugins`
3. Vá para a aba Installed
4. Autentique nos plugins **claude.ai Atlassian** e **claude.ai Figma**

### Cursor

1. Abra o Cursor
2. Vá em **Settings → Plugins**
3. Instale o plugin do **Figma**
4. Instale o plugin do **Atlassian**
5. Autentique em ambos os plugins

## Telemetria (OpenTelemetry)

> Apenas Claude Code. As env vars `OTEL_*` e os eventos `claude_code.*` não existem nos outros IDEs.

O Claude Code já exporta métricas e eventos via OTLP, mas nada dinâmico: `env` em `settings.json` é
estritamente estático (sem interpolação, sem command substitution) e nenhum hook consegue exportar env
var de volta para o processo do Claude Code. Ou seja, a branch atual jamais chega em
`OTEL_RESOURCE_ATTRIBUTES`.

O hook `otel-context` resolve isso emitindo **log records OTLP próprios** para o mesmo coletor, em
`SessionStart`, `UserPromptSubmit` e `SessionEnd`. Cada record carrega:

| Atributo | Exemplo | Observação |
|---|---|---|
| `event.name` | `afyapowers.git_context` | discrimina nossos records dos nativos |
| `session.id` | `abc123` | **chave de join** com os eventos `claude_code.*` |
| `prompt.id` | `550e8400-…` | join exato por prompt; ausente no `SessionStart` |
| `hook.event` | `UserPromptSubmit` | qual evento originou o record |
| `git.branch` | `feat/tela-de-quizzes` | `detached` quando em detached HEAD |
| `git.repo` | `iclinic/afyapowers` | slug do remote (`origin`, ou o primeiro remote); cai para o nome da pasta local se não houver remote hospedado |
| `git.commit` | `73f5798` | SHA curto do `HEAD` |
| `git.dirty` | `true` / `false` | opt-in (ver abaixo) |

Os pares de `OTEL_RESOURCE_ATTRIBUTES` (department, cost center, squad) viajam no resource dos nossos
records também, então filtram igual aos eventos nativos.

> `git.repo` sai do remote justamente porque o nome da pasta local é escolha de cada dev e não
> identifica repositório numa frota. São extraídos apenas o owner e o repo — nunca o host nem
> credenciais eventualmente embutidas na URL de clone. Remote que é caminho local do filesystem é
> ignorado, para não vazar o layout de diretórios do dev.

**Como correlacionar:** no backend, junte nossos records aos nativos por `prompt.id` (exato) ou por
`session.id` (sessão inteira). Ex.: custo de tokens por branch = `claude_code.token.usage` ⨝
`event.name = 'afyapowers.git_context'` em `prompt.id`.

### Configuração

O hook não tem config própria obrigatória: ele **herda** a configuração OTLP que você já usa. Se
`CLAUDE_CODE_ENABLE_TELEMETRY=1` e houver um endpoint de logs resolvível, ele emite; caso contrário
fica silenciosamente inerte. As env vars podem vir do ambiente ou do bloco `env` de qualquer
`settings.json` (managed > projeto local > projeto > usuário) — o hook lê os arquivos como fallback,
então funciona independente de env var de settings ser herdada por subprocesso.

| Variável | Efeito |
|---|---|
| `AFYAPOWERS_OTEL_ENABLED` | `1` liga mesmo sem `CLAUDE_CODE_ENABLE_TELEMETRY`; `0` é kill switch e vence tudo |
| `AFYAPOWERS_OTEL_ENDPOINT` | sobrescreve o endpoint de logs (necessário se a org usa `grpc`, já que o hook só fala OTLP sobre HTTP) |
| `AFYAPOWERS_OTEL_HEADERS` | headers extras/sobrescritos, formato `k=v,k=v` |
| `AFYAPOWERS_OTEL_PROTOCOL` | `http/protobuf` (default) ou `http/json` |
| `AFYAPOWERS_OTEL_GIT_DIRTY` | `1` inclui `git.dirty`. Opt-in porque `git status` varre a árvore inteira e custa segundos em monorepo |
| `AFYAPOWERS_OTEL_DEBUG` | `1` grava o que foi enviado (ou por que não) em `.afyapowers/otel-debug.jsonl` |

Ordem de resolução do endpoint: `AFYAPOWERS_OTEL_ENDPOINT` → `OTEL_EXPORTER_OTLP_LOGS_ENDPOINT` →
`OTEL_EXPORTER_OTLP_ENDPOINT` + `/v1/logs`. Headers e protocolo seguem a mesma lógica per-signal do
OTel (`OTEL_EXPORTER_OTLP_LOGS_HEADERS` / `_PROTOCOL` ganham dos genéricos).

### Rollout na frota

Um único arquivo de managed settings (`/Library/Application Support/ClaudeCode/managed-settings.json`
no macOS, `/etc/claude-code/` no Linux) mais o plugin atualizado cobrem toda a base de devs — sem
dotfile e sem setting por repositório:

```json
{
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_LOGS_EXPORTER": "otlp",
    "OTEL_EXPORTER_OTLP_LOGS_PROTOCOL": "http/protobuf",
    "OTEL_EXPORTER_OTLP_LOGS_ENDPOINT": "https://collector.exemplo.com.br/v1/logs",
    "OTEL_EXPORTER_OTLP_LOGS_HEADERS": "Authorization=Bearer TOKEN",
    "OTEL_RESOURCE_ATTRIBUTES": "department=engineering,cost_center=eng-123",
    "OTEL_METRICS_INCLUDE_RESOURCE_ATTRIBUTES": "false"
  }
}
```

> Managed settings **remove** env vars conflitantes definidas pelo dev no startup. Fixar
> `OTEL_RESOURCE_ATTRIBUTES` ali é o que você quer para atributos organizacionais, mas inviabiliza
> qualquer enriquecimento local via wrapper de shell.

**Garantias do hook:** roda no caminho crítico do prompt apenas para resolver config e fazer spawn de
um filho destacado (~50 ms); git e rede acontecem no filho. Nunca escreve em stdout (em
`UserPromptSubmit` o stdout do hook seria injetado como contexto no prompt), nunca bloqueia a sessão e
sai `0` em qualquer erro. Fora de um repositório git, não emite nada.

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
  skills/                   # Todas as skills — workflow commands e skills de fase (19 no total)
  config/                   # Configuração específica por IDE (Claude, Cursor, Gemini)
  hooks/                    # Hooks: contexto de sessão, diretiva de idioma, histórico, telemetria OTLP
  manifests/                # Manifestos do plugin para Claude e Cursor
  templates/                # Templates Markdown para artefatos
```

## Documentação Detalhada do Workflow

Para uma descrição completa e aprofundada de todo o workflow — incluindo gates de fase, padrões de subagentes, templates de artefatos, mecânica de hooks, integrações Figma/JIRA, skills standalone e o pipeline de distribuição multi-IDE — consulte [WORKFLOW.md](WORKFLOW.md).

## Licença

MIT
