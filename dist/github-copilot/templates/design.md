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
