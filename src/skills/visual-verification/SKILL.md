---
claude:
  name: afyapowers:visual-verification
  description: "Use when verifying UI against a Figma reference — shared protocol invoked identically by implement (figma-design-implementer self-check) and review (visual-fidelity-reviewer)"
  model: sonnet
  effort: medium
cursor:
  name: afyapowers-visual-verification
  description: "Use when verifying UI against a Figma reference — shared protocol invoked identically by implement (figma-design-implementer self-check) and review (visual-fidelity-reviewer)"
  model: claude-4-6-sonnet
github-copilot:
  name: visual-verification
  description: "Use when verifying UI against a Figma reference — shared protocol invoked identically by implement (figma-design-implementer self-check) and review (visual-fidelity-reviewer)"
---

# Visual Verification

Protocolo único e compartilhado de verificação visual. É invocado de forma idêntica por dois chamadores:
- **Implement:** autoconferência do `figma-design-implementer` logo após implementar uma task de UI.
- **Review:** o `visual-fidelity-reviewer`, ao auditar a fidelidade visual do que foi entregue.

Ambos os chamadores consomem a mesma entrada e recebem a mesma saída — nenhum dos dois reimplementa este protocolo por conta própria.

## Contrato de Entrada

Os 2 contratos definidos em `artifacts/design.md`:
- **Contrato de Verificação** — `verificacao_visual`, Setup & Dev Server, URL Base & Rotas, Sinal de Readiness, Estratégia de Auth, Cenários de Dados Semeados, Ferramenta de Browser.
- **Contrato de Layout** — `captured-at` + tabela (Frame / Breakpoint, Container max-width, Margens laterais, Gaps, Nº de colunas, Min/Max por peça).

Se `verificacao_visual` for **não-aplicável**, a skill não deve ser invocada — não há o que verificar visualmente.

O chamador também informa: qual task/nó Figma está sendo verificado e em qual fase (`implement` ou `review`), para a convenção de nome de arquivo de evidência.

## Contrato de Saída

- **PASS/FAIL** — resultado binário da verificação.
- As medidas numéricas efetivamente obtidas, citadas (não apenas "dentro da tolerância" — os valores).
- Se FAIL: a lista de asserções específicas que falharam.
- Caminhos das evidências salvas em `artifacts/visual-checks/`.

## Processo

### 1. Ler os contratos

Ler o Contrato de Verificação e o Contrato de Layout de `artifacts/design.md`. Se algum campo necessário para os passos abaixo estiver ausente ou vazio, tratar como falha de preflight (Passo 5) — não adivinhar valores.

### 2. Detectar o browser MCP (autoritativa, runtime)

A detecção de qual ferramenta de browser MCP está disponível acontece agora, em runtime — o campo "Ferramenta de Browser" do Contrato de Verificação é apenas informativo (preenchido durante o design) e nunca substitui esta checagem.

**Fail-closed:** se nenhum browser MCP estiver disponível no runtime atual, a verificação inteira é bloqueada. Não capturar screenshots por outros meios, não aproximar por inspeção de código, não seguir adiante sem evidência visual real.

### 3. Ciclo de vida do dev server (singleton referência-contado por fase)

Esta skill é a **única dona** do dev server usado para verificação visual e da sua serialização. Nenhum outro processo deve subir ou derrubar esse server durante a fase.

- **1ª invocação da fase:** subir o dev server com o comando de "Setup & Dev Server" do contrato, e adquirir um lock (arquivo de lock dedicado + checagem de que a porta do Contrato de Verificação está respondendo).
- **Invocações seguintes na mesma fase:** reusar o mesmo server sob o mesmo lock. Se o lock estiver detido por outra invocação em andamento, **bloquear e esperar** — nunca subir um segundo server nem reusar a mesma aba/viewport enquanto outra invocação a está usando. É assim que autoconferências de UI se serializam: sem starts rivais, sem viewports concorrentes disputando uma aba compartilhada.
- **Health-check** do server (porta responde, readiness alcançável) antes de cada uso, mesmo quando reusado.
- O server só é **derrubado ao final da verificação da fase inteira** (última invocação daquela fase), nunca ao final de uma única invocação.

Se subir o server falhar, ou o health-check falhar após retries razoáveis, é fail-closed (bloqueia) — ver seção Fail-closed abaixo.

### 4. Auth + seed

Aplicar a Estratégia de Auth do contrato (storageState pré-autenticado ou rota de bypass) e semear os dados do cenário sendo verificado, conforme a linha correspondente em Cenários de Dados Semeados.

### 5. Preflight

Antes de capturar qualquer evidência, confirmar todas as condições abaixo:
- A URL final carregada **não é** uma tela de login (auth foi aplicada com sucesso).
- O seletor de readiness do contrato está presente no DOM.
- Não há erro fatal no console do browser.

**Falha em qualquer condição de preflight bloqueia a verificação** — não prosseguir para captura de screenshots com um estado de página que não se sabe estar correto.

### 6. Por breakpoint × (pior caso + estados críticos)

Para cada combinação de breakpoint (do Contrato de Layout) e cenário de dados (pior caso + estados críticos do Contrato de Verificação):

1. Definir o viewport para a largura do breakpoint.
2. Navegar para a rota alvo.
3. Aguardar o sinal de readiness — incluindo o settle de animações/transições especificado no contrato, não apenas a presença do seletor.
4. Capturar screenshot do navegador.
5. **Medir o DOM**: `getBoundingClientRect().width` no elemento-alvo (border-box) + computed styles relevantes (margens, gaps, nº de colunas via posição dos irmãos). Comparar contra o Contrato de Layout com:
   - Tolerância **±1px** em dimensões (container max-width, margens, gaps, min/max por peça).
   - Exatidão **exata** (não tolerante) em nº de colunas e em unidades de token (ex.: não aceitar `px` onde o token exige `rem`, ou vice-versa).
6. Obter `get_screenshot` do nó Figma correspondente.
7. Julgamento por rubrica lado a lado (screenshot do navegador vs. screenshot do Figma): espaçamento, tipografia, cor, alinhamento, estado.
8. Salvar a evidência em `artifacts/visual-checks/`, seguindo a convenção de nome `<task>-<breakpoint>-<estado>-<fase>.png` (ex.: `task-07-desktop-worst-case-implement.png`).

### 7. Retornar o resultado

Retornar **PASS/FAIL**:
- Sempre citar os números medidos (não só "ok"/"dentro da tolerância").
- Se FAIL, listar as asserções específicas que falharam (ex.: "Gaps: esperado 24px ±1px, medido 31px").
- Listar os caminhos de todas as evidências salvas em `artifacts/visual-checks/` nesta execução.

## Fail-closed (R10)

As seguintes condições **bloqueiam** a verificação, sem exceção automática:
- Browser MCP ausente no runtime (Passo 2).
- Dev server não sobe, ou falha no health-check (Passo 3).
- Preflight falho (Passo 5).
- Qualquer asserção do Passo 6 resultando em FAIL.

A única forma de prosseguir apesar de um bloqueio é um **override code-only explícito por-task**, registrado no momento da implementação. O override reusa o mesmo mecanismo de `[ACCEPTED BY USER: <motivo>]` já usado em `implementation-concerns.md`: o implementador registra a linha de concern com esse marcador e o motivo do override. Quando existe um override aceito para a task, a verificação visual daquela task é **pulada** — e esse pulo fica registrado (não é um PASS silencioso; é uma ausência de verificação explicitamente aceita pelo usuário).
