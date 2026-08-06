# Design: {{feature_name}}

<!-- IDs ESTÁVEIS: numere requisitos (R1, R2…), premissas (P1…) e questões (Q1…) com IDs que NUNCA são
     renumerados. Item novo = próximo ID livre; item removido deixa lacuna marcada ("R7 — removido: <motivo>").
     Referencie sempre por ID. Renumerar quebra todas as referências cruzadas do documento. -->

## Contexto do JIRA
<!-- Apenas quando há issue do JIRA. Remova se não se aplicar. -->

**Issue:** [PROJ-123](https://your-site.atlassian.net/browse/PROJ-123)
**Type:** Story | Bug | Task | Epic
**Summary:** <!-- resumo em uma linha -->

### Requisitos do JIRA
- ...

### Critérios de Aceite
- [ ] ...

### Issues Vinculadas
- Blocked by: PROJ-100 — ...

## Declaração do Problema
<!-- Qual problema estamos resolvendo e por quê -->

## Requisitos
<!-- R1, R2… — IDs estáveis (ver nota no topo) -->

## Restrições

## Abordagens Consideradas
<!-- 2-3 abordagens com trade-offs -->

### Abordagem 1: ...
### Abordagem 2: ...

## Abordagem Escolhida
<!-- Qual e por quê -->

## Arquitetura
<!-- Componentes, como interagem -->

## Decisões de Reúso de Componentes
<!-- Uma linha por candidato não-DS avaliado (DS vai na Árvore). Agente recomenda, usuário decide cada
     linha — sem adoção automática; divergência entre colunas = override registrado. Remova se vazio. -->

| Target (Figma node / requisito) | Componente candidato | Name | Layout | Behavior | Recomendação do agente | Decisão do usuário |
|---------------------------------|----------------------|------|--------|----------|------------------------|--------------------|
<!-- ex.: | Submit Button (3:120) | PrimaryButton | ✓ | ✓ | ✓ | Reusar | Aprovado pelo usuário | -->

## Fluxo de Dados

## Mudanças de API / Interface

## Tratamento de Erros

## Casos de Borda & Estados
<!-- Saída da Interrogação. Uma linha por estado/condição (vazio, carregando, erro, zero/um/muitos, …),
     confirmada com o usuário. Obrigatório para features com estado/UI. -->

| Estado / condição | Comportamento esperado |
|-------------------|------------------------|

## Premissas & Riscos
<!-- P1, P2… — toda premissa da qual o design depende, com como foi confirmada. -->

| # | Premissa | Confirmação | Risco se estiver errada |
|---|----------|-------------|-------------------------|

## Estratégia de Testes

## Dependências

## Questões em Aberto
<!-- Q1, Q2… — todo item termina resolvido ou explicitamente adiado; nenhuma linha BLOQUEANTE fica "aberta"
     quando o design é escrito (REQUIREMENTS-GATE). -->

| # | Questão | Severidade | Status | Resolução |
|---|---------|------------|--------|-----------|

## Recursos do Figma
<!-- Apenas quando há Figma. Remova se não se aplicar. Produzido pelo agente figma-reader (regras
     completas em agents/figma-reader.md). Toda entrada é AUTOSSUFICIENTE para fetch (fileKey + node id);
     Telas = T1, T2…, Componentes = C1, C2… — chaves usadas pelo Contrato de Layout (T#) e pela Árvore de DS (C#). -->

### Arquivos
<!-- Todo arquivo Figma envolvido — o da tela e cada arquivo de origem de componente. -->

| # | Papel | URL | fileKey |
|---|-------|-----|---------|

### Breakpoints
- <breakpoint_name>: <width>px (Tela T<n> "<frame_name>", node `<node_id>`)

### Telas
<!-- Uma entrada por FRAME de topo. Filhos INSTANCE referenciam por C# (coordenadas do componente vivem em
     ### Componentes). Marque "(subárvore não explorada)" onde não houve descida (depth 2). -->

#### T1 — <screen_name>
- **Arquivo:** F1 (`<file_key>`)
- **Node ID:** `<node_id>`
- **Tipo:** FRAME
- **Dimensões:** <width>x<height>
- **Breakpoint:** <breakpoint_name>
- **Página no Figma:** <page_name>
- **Conteúdo:**
  - C1 <component_name> ×3 (instâncias: `<node_id>`, `<node_id>`, `<node_id>`)
  - <leaf_name> (node `<node_id>`, TEXT)

### Componentes
<!-- Uma entrada por componente distinto, com as coordenadas do ORIGINAL (nunca da instância — regras na
     skill analyzing-design-system). Não resolvido → campos `—` + linha `Pendência:` (bloqueia a fase e
     fica fora da Árvore). -->

#### C1 — <component_name>
- **Arquivo do original:** F2 (`<file_key>`)
- **Node ID do original:** `<node_id>`
- **Tipo:** COMPONENT_SET
- **Variantes que o original declara:** <axis>=<v1>|<v2>
- **Variantes que o layout usa:** <axis>=<valor>
- **Instâncias:** 3 em T1, 1 em T2

### Anotações de Design
<!-- Todas as anotações do Dev Mode, verbatim, com dono (T#/C#). Omita se nenhuma. Regras de negócio
     refletem também em Requisitos. -->
- node `<node_id>` (<node_name>) [<category>] (dono: T1 | C1): "<annotation text>" — pins: <property types>

### Textos Reais
<!-- Textos renderizados extraídos do Figma, agrupados por Tela — evidência para decisões de copy/label.
     Omita se nenhum. -->
- node `<node_id>` (<name>, dono: T1): "<characters>" [maxLines: N | truncation: X]

### Ícones
<!-- Inventário do figma-reader. Ícones NÃO entram em ### Componentes, na Árvore de DS nem no gate de
     origem — a fonte deles é decidida em ## Estratégia de Ícones. Omita se nenhum. -->
- <nome> [heurística: name|size] — <N> instâncias (T1 ×2) — tamanhos: 24x24 — origem: remota (lib) | local (`<node_id>`)

## Árvore de Componentes de DS
<!-- Apenas quando há Figma com componentes. Produzida por analyzing-design-system (regras completas lá).
     Só carrega DECISÕES do usuário — coordenadas vivem em ### Componentes, via C#. Ordem folhas→raiz.
     Veredito ∈ Implementar | Importar (sem task; import path em "Nome no código") | Atualizar | Derivar.
     Override do usuário → registre ambos ("Derivar (recomendado: Atualizar)"). -->

| # | Componente | Veredito | Depende de | Paridade | Nome no código | Task Type |
|---|-----------|----------|------------|----------|----------------|-----------|
<!-- ex.: | C4 | Button | Importar | — | size=lg já existe | `@ds/Button` | — | -->

### Avisos da análise de DS
<!-- Omita se não houver: originais inalcançáveis, confiança reduzida, nós deprioritizados/rejeitados
     (com cascata nos pais), homônimos com componentIds diferentes. -->
- ...

## Estratégia de Ícones
<!-- Apenas quando ### Ícones não está vazio. Decidida com o usuário na análise de DS (Step 7.5).
     Cadeia de preferência com regra de IDÊNTICO em todo elo que não seja export do Figma;
     export do Figma é sempre o fallback final. -->

**Cadeia de preferência (decisão do usuário):**
1. <ex.: Lib `lucide-react` quando o ícone for IDÊNTICO (mesmo glyph/artwork)>
2. <ex.: Exportar do Figma (Asset Rules do implementer)>

**Import pattern da lib:** `<ex.: import { X } from 'lucide-react'>` <!-- omita se a cadeia não usa lib -->
**Diretório de ícones locais:** `<ex.: src/assets/icons/>` <!-- omita se a cadeia não usa locais -->

## Contrato de Layout
<!-- Apenas quando há UI + Figma. Derivado do get_metadata pelo agente figma-reader (regras em
     agents/figma-reader.md); guia de fidelidade do implementador, por breakpoint. Chaveado por T#. -->

**captured-at:** `<timestamp ISO 8601 da extração>`

| # | Tela / Breakpoint | Container max-width | Margens laterais | Gaps | Nº de colunas | Min/Max por peça |
|---|-------------------|----------------------|-------------------|------|----------------|--------------------|
