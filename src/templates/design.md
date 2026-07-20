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
<!-- Preenchida sempre que o design reutiliza um componente existente do codebase/DS. Uma linha por reúso. Um
     componente só pode ser reutilizado silenciosamente SE for uma correspondência exata nos três eixos (Name +
     Layout + Behavior). Qualquer outra coisa exige aprovação explícita do usuário antes de adotá-lo.
     Decision = "Exact match (auto)" ou "Approved by user" ou "Build custom (rejected)".
     Remova esta seção se nenhum componente for reutilizado. -->

| Target (Figma node / requisito) | Componente candidato | Name | Layout | Behavior | Decision |
|---------------------------------|----------------------|------|--------|----------|----------|
<!-- ex.: | Specialty Chip (2:5471) | DropdownPicker (DS) | ✗ | ✗ | ✗ drawer vs popover | Build custom (rejected) | -->
<!-- ex.: | Submit Button (3:120)   | PrimaryButton (DS)  | ✓ | ✓ | ✓                   | Exact match (auto)     | -->

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
<!-- Se a feature abrange múltiplos arquivos do Figma, repita a estrutura File/File Key/Node Map para cada arquivo. -->

**File:** `<figma_url>`
**File Key:** `<file_key>`

### Breakpoints
<!-- Inferidos a partir dos nomes e dimensões dos frames de topo na resposta do get_metadata -->
- <breakpoint_name>: <width>px (Frame "<frame_name>", node `<node_id>`)

### Node Map
<!-- Uma única chamada get_metadata em depth 2. Separado em subseções Reusable Components e Screens. -->
<!-- Nós COMPONENT/COMPONENT_SET vão em Reusable Components. Todo o resto fica em Screens. -->

#### Page: <page_name>

**Componentes Reutilizáveis:**
<!-- Liste todos os nós COMPONENT/COMPONENT_SET com node IDs. Se nenhum, escreva: (nenhum — todos os componentes são externos ou pré-existentes) -->
- <component_name> (node `<node_id>`, COMPONENT)
- <component_set_name> (node `<node_id>`, COMPONENT_SET)

**Telas:**
<!-- Liste cada FRAME de topo com filhos (excluindo COMPONENT/COMPONENT_SET já listados acima). Colapse nós INSTANCE repetidos com contagem ×N. -->
- **<screen_name>** (node `<node_id>`, FRAME, <width>x<height>)
  - <element_name> (node `<node_id>`, INSTANCE, componentId: `<component_id>`) ×N
  - <leaf_name> (node `<node_id>`, TEXT)

### Anotações de Design
<!-- Todas as anotações do Dev Mode extraídas via use_figma. Uma entrada por nó anotado, verbatim. Omita esta subseção se nenhuma. -->
<!-- Anotações são requisitos (regras de negócio, comportamento, animações, acessibilidade, instruções de dev). Reflita-as também nas seções acima — regras de negócio em Requisitos. -->
<!-- Remova [<category>] se não houver categoria do Figma; remova a cláusula "— pins:" se não houver propriedades fixadas. -->
- node `<node_id>` (<node_name>) [<category>]: "<annotation label / note text>" — pins: <property types>

## Árvore de Componentes de DS
<!-- Incluída apenas quando a feature tem referência Figma com componentes de design system. Remova esta seção se não se aplicar. -->
<!-- Mapeamento entre nós Figma e componentes de código — um nó por linha, ordenação topológica folhas→raiz.
     Componentes compartilhados aparecem UMA vez; dependências via coluna "Depende de". -->

| Nó (nome Figma · main node-id · componentKey) | Tipo Figma | Veredito | Depende de | Paridade (campos que divergem inst.↔original) | Nome no código (proposto) | Fonte do catálogo | Task Type |
|------------------------------------------------|------------|----------|------------|------------------------------------------------|---------------------------|-------------------|-----------|
<!-- ex.: | card · 2001:8579 · 4433e34… | COMPONENT_SET | Derivar | **`Card` (base)**, Thumbnail, _Icon buttons, Tag | layout, border, filhos add. | `LiveCard` (proposto) | Figma lib (URL) | UI Component | -->
<!-- ex.: | Thumbnail · … · … | COMPONENT | Implementar | — | — | `Thumbnail` | Figma lib (URL) | UI Component | -->
<!-- ex.: | Card genérico · … · … | COMPONENT_SET | Importar | — | só conteúdo | `Card` (existe) | código | — | -->

<!-- === Notas de convenção === -->
<!-- **Paridade** = conjunto de campos que divergem entre a instância e o original:
     "só conteúdo" ⇒ reusar; diffs estruturais/layout/estilo-fora-de-token ⇒ derivar. -->
<!-- **Fonte do catálogo** = `código (existente)` | `Figma lib <url/libName>` | `só observado — catálogo não confirmado`. -->
<!-- **Agrupamento de instâncias:** instâncias do mesmo original com diff só de conteúdo ⇒ um padrão "reusar";
     grupos com conjuntos de diffs equivalentes além do corte ⇒ um derivado por grupo. -->
<!-- **Convenção para "Derivar":** o PRIMEIRO item de "Depende de" é sempre o genérico base (o original que
     o derivado compõe por baixo) — garante que a task do derivado só rode após a task/importação do genérico. -->
<!-- **Determinação aditivo-vs-breaking (veredito "Atualizar"):** acontece AQUI, na fase design (a checagem de
     existência inspeciona o código: props/tipos/Storybook); se a variante exigida só puder ser adicionada de forma
     quebrante, o veredito já sai como "Derivar". Assim o plan permanece estável (R14) — o implement não reclassifica. -->

## Contrato de Layout
<!-- Incluído apenas quando a feature tem UI + referência Figma. Remova esta seção se não se aplicar. Validado pelo design-reviewer. -->
<!-- Medidas derivadas do get_metadata: margens = child.x relativo ao pai; gaps = sibling.x − (prev.x + prev.width);
     nº de colunas = irmãos de mesmo y; container = largura do frame de conteúdo; min/max = width/height. -->
<!-- Serve como guia de fidelidade para o implementador (medidas de aceite por breakpoint) — não é verificado por renderização de tela. -->

**captured-at:** `<timestamp ISO 8601 de quando as medidas foram extraídas do get_metadata>`

| Frame / Breakpoint | Container max-width | Margens laterais | Gaps | Nº de colunas | Min/Max por peça |
|---------------------|----------------------|-------------------|------|----------------|--------------------|
<!-- ex.: | Desktop (1440px) | 1200px | 120px | 24px | 3 | 360px / 400px | -->
<!-- ex.: | Mobile (375px)   | 343px  | 16px  | 16px | 1 | 343px / 343px  | -->
