# Design: {{feature_name}}

## Contexto do JIRA
<!-- Incluído apenas quando a feature tem uma issue do JIRA associada. Remova esta seção se não se aplicar. -->

**Issue:** [PROJ-123](https://your-site.atlassian.net/browse/PROJ-123)
**Type:** Story | Bug | Task | Epic
**Summary:** <!-- Resumo em uma linha vindo do JIRA -->

### Requisitos do JIRA
<!-- Principais requisitos extraídos da descrição do JIRA e dos critérios de aceite -->
- ...

### Critérios de Aceite
<!-- Critérios de aceite da issue do JIRA, verbatim ou levemente reformatados -->
- [ ] ...

### Issues Vinculadas
<!-- Issues do JIRA relacionadas: bloqueios, dependências, trabalhos relacionados -->
- Blocked by: PROJ-100 — ...
- Related to: PROJ-150 — ...

## Declaração do Problema
<!-- Qual problema estamos resolvendo e por quê -->

## Requisitos
<!-- Principais requisitos descobertos durante o design -->

## Restrições
<!-- Restrições técnicas, de negócio ou de tempo -->

## Abordagens Consideradas
<!-- 2-3 abordagens com trade-offs -->

### Abordagem 1: ...
### Abordagem 2: ...

## Abordagem Escolhida
<!-- Qual abordagem e por quê -->

## Arquitetura
<!-- Componentes, como interagem -->

## Decisões de Reúso de Componentes
<!-- Uma linha por candidato de reúso avaliado (componentes de DS do Figma vão na Árvore de DS, não aqui).
     NENHUMA adoção automática: o agente recomenda, o usuário decide cada linha.
     Decisão ∈ "Aprovado pelo usuário" | "Rejeitado pelo usuário (build custom)"; divergência entre as
     colunas = usuário sobrescreveu (mantenha o registro). Remova a seção se nenhum candidato foi avaliado. -->

| Target (Figma node / requisito) | Componente candidato | Name | Layout | Behavior | Recomendação do agente | Decisão do usuário |
|---------------------------------|----------------------|------|--------|----------|------------------------|--------------------|
<!-- ex.: | Specialty Chip (2:5471) | DropdownPicker (DS) | ✗ | ✗ | ✗ drawer vs popover | Build custom | Rejeitado pelo usuário (build custom) | -->
<!-- ex.: | Submit Button (3:120)   | PrimaryButton       | ✓ | ✓ | ✓                   | Reusar               | Aprovado pelo usuário                 | -->
<!-- ex.: | Filter Row (4:88)       | ToolbarRow          | ✓ | ✓ | ✓                   | Reusar               | Rejeitado pelo usuário (build custom) | ← divergência registrada -->

## Fluxo de Dados
<!-- Como os dados transitam pelo sistema -->

## Mudanças de API / Interface
<!-- Interfaces novas ou modificadas -->

## Tratamento de Erros
<!-- Modos de falha e como são tratados -->

## Casos de Borda & Estados
<!-- Saída da Interrogação de Requisitos. Uma linha por estado/condição que a feature deve tratar —
     vazio, carregando, erro, zero/um/muitos, muito-grande, não-autorizado, offline, valores de borda, texto
     longo, etc. Confirmado com o usuário. Obrigatório para qualquer feature com estado/UI. -->

| Estado / condição | Comportamento esperado |
|-------------------|------------------------|
<!-- ex.: | Lista vazia | Mostrar placeholder "Nenhum quiz ainda", ocultar filtro | -->
<!-- ex.: | Requisição falha | Mostrar banner de retry; manter últimos dados válidos se houver | -->

## Premissas & Riscos
<!-- Saída da Interrogação de Requisitos. Toda premissa da qual o design depende, com como foi
     confirmada. Uma premissa BLOQUEANTE não confirmada deve ser resolvida antes de o design ser escrito. -->

| Premissa | Confirmação | Risco se estiver errada |
|----------|-------------|-------------------------|
<!-- ex.: | GET /quiz/{id} retorna {context, question, options[]} | Confirmado contra endpoint de homolog | Adapter + mocks errados | -->

## Estratégia de Testes
<!-- O que testar e como -->

## Dependências
<!-- Dependências externas ou pré-requisitos -->

## Questões em Aberto
<!-- Saída da Interrogação de Requisitos. Todo item levantado deve terminar resolvido ou explicitamente
     adiado — nenhuma linha BLOQUEANTE pode estar "aberta" quando o design é escrito (REQUIREMENTS-GATE). -->

| Questão | Severidade | Status | Resolução |
|---------|------------|--------|-----------|
<!-- ex.: | O que torna o formulário válido? | bloqueante | resolvida | Todos os campos não-vazios + formato de email | -->
<!-- ex.: | i18n para textos de erro? | não-bloqueante | adiada | Fora de escopo nesta iteração | -->

## Recursos do Figma
<!-- Incluído apenas quando a feature tem designs no Figma. Remova esta seção se não se aplicar. -->
<!-- Estrutura: Arquivos → Telas → Componentes → Anotações. Cada entrada de Telas e de Componentes é
     AUTOSSUFICIENTE: carrega tudo que é necessário para buscá-la no Figma (fileKey, node id, nome, tipo),
     sem depender de outra seção. Telas recebem IDs T1, T2…; Componentes recebem C1, C2…
     Essas IDs são a chave usada pelo Contrato de Layout (por T#) e pela Árvore de Componentes de DS (por C#),
     para que nenhuma coordenada seja repetida em dois lugares e possa divergir. -->

### Arquivos
<!-- Todo arquivo do Figma envolvido: o da tela e cada arquivo de origem de componente (ex.: o do design system).
     Necessário porque um componente pode ter origem em arquivo diferente do da tela. -->

| # | Papel | URL | fileKey |
|---|-------|-----|---------|
<!-- ex.: | F1 | telas da feature      | figma.com/design/eS5l5l…/Transmissões?node-id=3048-1870 | `eS5l5l…` | -->
<!-- ex.: | F2 | design system (origem) | figma.com/design/AbC123/Core-Components?node-id=45-12   | `AbC123`  | -->

### Breakpoints
<!-- Inferidos a partir dos nomes e dimensões dos frames de topo na resposta do get_metadata -->
- <breakpoint_name>: <width>px (Tela T<n> "<frame_name>", node `<node_id>`)

### Telas
<!-- Uma entrada por FRAME de topo. Cada uma autossuficiente para fetch: arquivo, node id, tipo, dimensões.
     Filhos INSTANCE referenciam o componente por C# — a identidade e as coordenadas do componente vivem em
     ### Componentes, não aqui, para não duplicar.
     Marque "(subárvore não explorada)" em todo nó com filhos não percorridos (limite de depth 2). -->

#### T1 — <screen_name>
- **Arquivo:** F1 (`<file_key>`)
- **Node ID:** `<node_id>`
- **Tipo:** FRAME
- **Dimensões:** <width>x<height>
- **Breakpoint:** <breakpoint_name>
- **Página no Figma:** <page_name>
- **Conteúdo:**
  - C1 <component_name> ×3 (instâncias: `<node_id>`, `<node_id>`, `<node_id>`)
  - C2 <component_name> ×1 (instância: `<node_id>`) (subárvore não explorada)
  - <leaf_name> (node `<node_id>`, TEXT)

### Componentes
<!-- Uma entrada por componente DISTINTO, autossuficiente para fetch do ORIGINAL (o COMPONENT/COMPONENT_SET
     no arquivo que o DECLARA — nunca a instância; regras completas na skill analyzing-design-system).
     Identidade = fileKey + node id (a URL de origem não é guardada). Coordenada preenchida = original
     resolvido e validado. Tipo: COMPONENT_SET (eixos de variante) | COMPONENT (único).
     Origem: local (original no arquivo das telas — F1, qualquer página; "team component") |
     externa (original em arquivo de DS — F2+). Decide o Task Type e o contrato de tokens no implement.
     Variantes que o layout usa: tuplas COMPLETAS por instância (mecânico: componentId da instância →
     symbol da variante → nome do symbol = tupla), uma linha por tupla distinta com suas instâncias;
     nunca resumo em prosa, nunca derivado de anotações; irresolvível na resposta → "tuplas pendentes"
     com pares instância → componentId.
     Variantes a implementar: só para veredito de código em escopo reduzido (regra: Origem externa;
     Origem local implementa o catálogo inteiro e a linha não aparece, salvo escopo reduzido escolhido
     explicitamente pelo usuário) = variantes semânticas que o layout usa (união das tuplas — eixo que
     varia entre tuplas usadas NUNCA é colapsado) + TODOS os estados interativos que o original declara
     (hovered, pressed, selected, focused, disabled, …).
     Coordenada não resolvida → campos `—` + linha `Pendência:`; um componente
     com Pendência bloqueia a fase design e NÃO entra na Árvore de Componentes de DS. -->

#### C1 — <component_name>
- **Arquivo do original:** F2 (`<file_key>`)
- **Node ID do original:** `<node_id>`
- **Tipo:** COMPONENT_SET
- **Origem:** externa
- **Variantes que o original declara:** <axis>=<v1>|<v2>, <axis>=<v1>|<v2>
- **Variantes que o layout usa:** <axis>=<v1>, <axis>=<v1> (T1 `<node_id>`, `<node_id>`); <axis>=<v2>, <axis>=<v1> (T2 `<node_id>`)
- **Variantes a implementar:** <axis>=<v1>|<v2>, state=hovered|pressed|disabled (escopo reduzido)
- **Instâncias:** 3 em T1, 1 em T2

<!-- ex. de componente declarado no próprio arquivo da tela (nenhum link foi necessário):
#### C2 — Header
- **Arquivo do original:** F1 (`eS5l5l…`)
- **Node ID do original:** `88:2`
- **Tipo:** COMPONENT
- **Origem:** local
- **Variantes que o original declara:** (nenhuma — COMPONENT simples)
- **Variantes que o layout usa:** —
- **Instâncias:** 1 em T1
-->

<!-- ex. de componente ainda pendente (bloqueia a fase):
#### C3 — Pagination
- **Arquivo do original:** —
- **Node ID do original:** —
- **Tipo:** —
- **Origem:** —
- **Pendência:** aguardando link direto do nó (o último link recebido era de arquivo, sem node-id — rejeitado sem chamada MCP)
- **Variantes que o original declara:** — (sem acesso ao original)
- **Variantes que o layout usa:** — (tuplas pendentes — `<node_id>` → componentId `<component_id>`)
- **Instâncias:** 1 em T1
-->

### Anotações de Design
<!-- Todas as anotações do Dev Mode extraídas via use_figma. Uma entrada por nó anotado, verbatim. Omita esta subseção se nenhuma. -->
<!-- Anotações são requisitos (regras de negócio, comportamento, animações, acessibilidade, instruções de dev). Reflita-as também nas seções acima — regras de negócio em Requisitos. -->
<!-- Remova [<category>] se não houver categoria do Figma; remova a cláusula "— pins:" se não houver propriedades fixadas. -->
<!-- Referencie o dono quando aplicável (T# ou C#), para a anotação ter destino nas tasks. -->
- node `<node_id>` (<node_name>) [<category>] (dono: T1 | C1): "<annotation label / note text>" — pins: <property types>

## Árvore de Componentes de DS
<!-- Incluída apenas quando a feature tem referência Figma com componentes. Remova esta seção se não se aplicar. -->
<!-- Produzida pela skill analyzing-design-system (regras completas lá). Nenhuma linha entra sem decisão
     explícita do usuário — nem Importar. ESTA TABELA SÓ CARREGA DECISÕES: coordenadas e Origem vivem em
     ### Componentes, referenciadas pela C# (quem monta a task lê o veredito aqui e o fileKey/node-id lá).
     Ordem: folhas→raiz. Veredito ∈ Implementar (do zero, a partir do original; Origem local = todas as
     variantes do catálogo; Origem externa = escopo reduzido, só "Variantes a implementar" da C#;
     com filhos em "Depende de" = composto: compõe, não reconstrói) | Importar (já existe; sem task, só
     import path) | Atualizar (falta variante; aditivo; Origem externa = só o que as telas usam e falta;
     aprovado nesta fase) | Derivar (novo, envolve a base = primeiro item de "Depende de"; Origem externa =
     wrapper só com o que as telas usam) | Adiado (Origem externa não encontrada no código; usuário optou
     por implementar fora do workflow — a fase design NÃO CONCLUI enquanto houver linha Adiado).
     Task Type ∈ UI Team Component (Origem local) | UI DS Component (Origem externa) | — (Importar/Adiado).
     Paridade = campos divergentes instância vs original (justificativa). Nome no código = confirmado;
     para Importar, o import path. Override do usuário → registre as duas
     em "Veredito" (ex.: "Derivar (recomendado: Atualizar)"). Componente com Pendência não entra aqui. -->

| # | Componente | Veredito | Depende de | Paridade | Nome no código | Task Type |
|---|-----------|----------|------------|----------|----------------|-----------|
<!-- ex.: | C4 | Button      | Importar    | —        | size=lg já existe        | `@ds/Button`           | —                 | -->
<!-- ex.: | C5 | Input       | Atualizar   | —        | falta state=error        | `@ds/Input`            | UI DS Component   | -->
<!-- ex.: | C6 | Menu        | Implementar | —        | não existe no código     | `Menu`                 | UI Team Component | -->
<!-- ex.: | C7 | MultiSelect | Implementar | C5, C6   | composto de 2 filhos     | `MultiSelect`          | UI Team Component | -->
<!-- ex.: | C8 | ProfileCard+Badge | Derivar | C2      | badge extra sobre avatar | `ProfileCardWithBadge` | UI DS Component   | -->
<!-- ex.: | C9 | DataTable   | Adiado      | —        | não existe no código (DS) | —                     | —                 | -->

### Avisos da análise de DS
<!-- Omita esta subseção se não houver avisos. -->
<!-- Originais inalcançáveis (usuário não conseguiu fornecer link válido — o nó fica FORA da árvore e o que
     depende dele fica bloqueado), confiança reduzida de inventário (tipagem fraca, ...rest spreads, wrappers
     de terceiros), nós deprioritizados pelo usuário, nós rejeitados com o efeito em cascata nos pais
     (skip vs. implementar sem a dependência), e componentes homônimos com componentIds diferentes. -->
- ...

## Contrato de Layout
<!-- Incluído apenas quando a feature tem UI + referência Figma. Remova esta seção se não se aplicar. Validado pelo design-reviewer. -->
<!-- Medidas derivadas do get_metadata: margens = child.x relativo ao pai; gaps = sibling.x − (prev.x + prev.width);
     nº de colunas = irmãos de mesmo y; container = largura do frame de conteúdo; min/max = width/height. -->
<!-- Serve como guia de fidelidade para o implementador (medidas de aceite por breakpoint) — não é verificado por renderização de tela. -->

**captured-at:** `<timestamp ISO 8601 de quando as medidas foram extraídas do get_metadata>`

<!-- Chaveado por T# (ver ### Telas) — a identidade e as coordenadas da tela vivem lá, não aqui. -->

| # | Tela / Breakpoint | Container max-width | Margens laterais | Gaps | Nº de colunas | Min/Max por peça |
|---|-------------------|----------------------|-------------------|------|----------------|--------------------|
<!-- ex.: | T1 | Desktop (1440px) | 1200px | 120px | 24px | 3 | 360px / 400px | -->
<!-- ex.: | T2 | Mobile (375px)   | 343px  | 16px  | 16px | 1 | 343px / 343px  | -->
