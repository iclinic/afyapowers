---
name: analyzing-design-system
description: "Detecta, resolve, faz diff e emite veredito para componentes de design system a partir de um Node Map do Figma, montando a Árvore de Componentes de DS. Invocada pela fase design e pela skill standalone figma-component."
---

# Analyzing Design System (o cérebro)

Skill compartilhada que **detecta → resolve → faz diff → emite veredito → monta a Árvore de
Componentes de DS**. É o cérebro da análise de design system: recebe um Node Map do Figma,
identifica os componentes genéricos por trás das instâncias, compara cada instância com seu
original, decide **reusar vs. derivar** e **implementar vs. importar vs. atualizar**, e produz a
tabela da seção **`## Árvore de Componentes de DS`** conforme o esquema de `templates/design.md`.

A skill é invocada por **duas** entradas, com **paridade de capacidade** — a mesma análise roda nos
dois casos:

- pela **fase design** (`afyapowers:design`), depois que `afyapowers:reading-figma-designs` já leu o
  Figma;
- pela skill **standalone** `afyapowers:figma-component`, para um único componente.

O corte reusar-vs-derivar, o padrão de wrapper e as regras de atualização aditiva **não são
duplicados aqui** — estão em `references/ds-implementation.md`, que esta skill **referencia**.

---

## Passo 1 — Contrato de entrada (dois modos)

Esta skill opera em **dois modos**. Detecte o modo pelos parâmetros recebidos e siga o contrato
correspondente. **Em ambos os modos a saída é a mesma:** a tabela da seção
`## Árvore de Componentes de DS`.

### Modo workflow (invocada pela fase design)

- **Entrada:** o **Node Map já montado** por `afyapowers:reading-figma-designs` (as subseções
  **Componentes Reutilizáveis** e **Telas**, com nós, node-ids, tipos e `componentId` de cada
  INSTANCE). O formato exato do Node Map é o descrito por `afyapowers:reading-figma-designs` — trate-o
  como fonte da estrutura.
- **NÃO refaça `get_metadata`.** A composição (instâncias + `componentId`s) já está no Node Map;
  reutilize-a. A cadeia de resolução (Passo 2) começa direto em `get_libraries`.
- Recebe também o `fileKey` do arquivo consumidor (já parseado pela fase design) e, se o usuário
  tiver fornecido, a **URL do arquivo da lib de DS**.

### Modo standalone (invocada pela `figma-component`)

- **Entrada:** `node-id` + `file-key` do componente alvo (e, opcionalmente, a URL da lib de DS).
- **Monta o próprio Node Map:** faz **1×** `get_metadata(fileKey, nodeId)` e deriva a mesma
  estrutura de Node Map descrita por `afyapowers:reading-figma-designs` (Componentes Reutilizáveis +
  Telas, com `componentId`s das INSTANCEs). Este é o **único** `get_metadata` — não repita.

Depois de ter o Node Map (recebido ou montado), os dois modos convergem para a mesma cadeia de
resolução e montagem da árvore.

---

## Passo 2 — Cadeia de resolução Dev-seat, econômica (R13)

Resolva cada INSTANCE do Node Map até seu **original** (o componente genérico do DS) executando a
sequência abaixo **na ordem**, respeitando o orçamento de MCP (~12 req/min). Cada passo tem um
propósito único; **não repita chamadas** já feitas.

| # | Chamada | Escopo / cardinalidade | Para que serve (req.) |
|---|---------|------------------------|-----------------------|
| 1 | `get_metadata` | **1×** (só no modo standalone; no workflow já veio pronto) | Detecta instâncias + composição (R1) |
| 2 | `get_libraries` | **1×**, com os `libKey`s **cacheados na feature** | Descobre as libs de DS disponíveis (R2) |
| 3 | `search_design_system` | **escopado** nas libs de DS (não global) | Resolve original + `assetType` + `componentKey` + docs (R2) |
| 4 | `get_design_context` | **por original distinto, NÃO por instância** | Nome + node-id do main + descrições + anotações; apoia o diff (R3) |
| 5 | `get_context_for_code_connect` | no `COMPONENT_SET` **no arquivo da lib** | Catálogo completo de variantes (R5) — **condicional**, ver abaixo |
| 6 | `get_code_connect_map` + busca na codebase | por original | Veredito de existência (R4/R8) |

### Regras de orçamento e cache

- **Cacheie os `libKey`s na feature** após a chamada 1× de `get_libraries` e reutilize-os no
  `search_design_system` — não chame `get_libraries` de novo dentro da mesma análise.
- **`get_design_context` é por original distinto, não por instância.** Se cinco instâncias apontam
  para o mesmo `componentId`, faça **uma** chamada para esse original, não cinco.
- **Nunca repita** uma chamada cujo resultado você já tem. Antes de qualquer chamada, verifique se o
  dado já está em mãos (Node Map, cache de libs, contexto já lido).
- **Backoff + retry em 429:** ao receber HTTP 429 (rate limit), espere **30–60s** e tente
  novamente. Um 429 **não falha a fase** — é transitório; apenas atrasa. Se persistir após retries,
  reporte como CONCERN, não como erro fatal.

### Passo 5 é condicional (achado estrutural do spike)

O `get_context_for_code_connect` no `COMPONENT_SET` da lib exige o **`fileKey` do arquivo da lib**.
O **Figma MCP não expõe** esse `fileKey`: `get_libraries` devolve `libraryKey` (hash), não
`fileKey`; `search_design_system` devolve `componentKey` + `filePath` (virtual), não `fileKey` +
`nodeId`. Logo:

- Este passo **só é possível se o usuário fornecer a URL do arquivo da lib**
  (`https://figma.com/design/<fileKey>/...?node-id=...`).
- **Sem a URL da lib, este é o caminho PADRÃO, não a exceção:** siga direto para o fallback
  **"catálogo não confirmado"** (Passo 4c e Passo 5 de erros). Não trate como falha — é o
  comportamento comum e esperado.
- Por isso, **pedir/confirmar a URL da lib é um passo CRÍTICO e recorrente**, não opcional, sempre
  que for construir um genérico do zero. Recomende registrar "URL da lib DS" como input opcional mas
  fortemente recomendado no `design.md`.

---

## Passo 3 — Heurística de veredito e montagem da árvore

Para cada nó do Node Map, produza uma linha da Árvore de Componentes de DS. As regras:

### (a) Diff instância↔original e o corte reusar-vs-derivar

Compare cada INSTANCE com seu original (via `get_design_context` do original + composição do Node
Map). O corte **reusar-vs-derivar** e a classificação **só-conteúdo vs. estrutural** estão descritos
em **`references/ds-implementation.md`** (seção 1) — **siga aquele arquivo, não duplique a
heurística aqui**. Em resumo (a fonte é o arquivo referenciado):

- diffs **só de conteúdo** (texto/imagem/ícone, valor de variant existente, visibilidade de slot
  existente) ⇒ **reusar** (o genérico é reusado com props/variant);
- diffs **estruturais** (filho add./removido, layout, subcomponente composto, comportamento novo,
  estilo fora de token/variant) ⇒ **derivar** (wrapper que compõe o genérico base — padrão da seção
  2 de `references/ds-implementation.md`).

A coluna **Paridade** registra o conjunto de campos que divergem; ela é a justificativa do veredito
reusar/derivar.

### (b) Veredito de existência 3-vias, verificado contra a codebase (R4/R8/R9/R14)

Para o **original** de cada instância, decida entre três vereditos **inspecionando o código real**
(não só o Figma):

- **Implementar (completo):** o genérico não existe na codebase (nem em Code Connect nem por busca).
  Task de implementação do genérico do zero.
- **Importar:** o genérico já existe **e** cobre a variante exigida. A checagem inspeciona
  props/tipos/union types, `argTypes` de Storybook e usos na codebase (conforme o spike — TypeScript
  props como caminho primário, Storybook e grep de usos como secundário/terciário). Nenhuma task de
  código nova; só importar.
- **Atualizar (aditivo):** o genérico existe mas **falta** a variante exigida, **e** ela pode ser
  adicionada de forma **não-quebrante** (nova prop opcional, novo valor de variant, novo slot
  opcional). Exige **aprovação explícita** do usuário (seção 3.2 de `references/ds-implementation.md`).

**Regra dura (R9/R14):** a determinação aditivo-vs-quebrante acontece **aqui, na fase design**. A
checagem inspeciona o código (props/tipos/Storybook); **se a variante exigida só puder ser
adicionada de forma quebrante** (remoção/alteração de prop, mudança de tipo ou de default), o
veredito **já sai como "Derivar"** — nunca como "Atualizar". Assim o plan permanece estável e o
implement não reclassifica em runtime.

Use `get_code_connect_map` + busca na codebase para a checagem de existência (R4/R8). Onde o
inventário de variantes por código for de confiança reduzida (tipagem fraca, `...rest`, wrappers de
terceiros), **sinalize confiança reduzida** — a aprovação humana no design (R14) é a rede de
segurança.

### (c) Catálogo just-in-time e "catálogo não confirmado" (R5)

Ao construir um genérico **do zero** (veredito Implementar), o catálogo completo de variantes é
just-in-time:

- **Peça/confirme a URL do arquivo da lib** (Passo 2, chamada 5). Com ela, leia o `COMPONENT_SET` na
  lib e monte o catálogo completo; a coluna **Fonte do catálogo** vira `Figma lib <url/libName>`.
- **Se a URL for indisponível** (caminho comum, ver Passo 2), implemente as variantes/estados
  **observáveis** (as usadas nas telas, inferidas via `get_design_context` do consumidor) e
  **sinalize "catálogo não confirmado"**; a coluna **Fonte do catálogo** vira
  `só observado — catálogo não confirmado`. Trate isto como o caminho **esperado e recorrente**, com
  o prompt de URL como passo padrão.

### (d) Ordem folhas→raiz (R6)

Ordene as linhas da árvore em **ordenação topológica folhas→raiz**: um componente aparece **depois**
de todas as suas dependências. Para "Derivar", o **primeiro** item da coluna **Depende de** é sempre
o **genérico base** que o derivado compõe por baixo — garante que a task do derivado só rode após a
task/importação do genérico.

### (e) Agrupamento de instâncias e nomes de derivados propostos

- **Instâncias do mesmo original com diff só de conteúdo** ⇒ um único padrão "reusar" (uma entrada).
- **Grupos com conjuntos de diffs estruturais equivalentes** ⇒ **um derivado por grupo** (não um por
  instância).
- Proponha o **nome no código** de cada derivado preservando a semântica e checando **colisão de
  nome** na codebase antes de propor (seção 3.5 de `references/ds-implementation.md`): se colidir,
  proponha alternativa (ex.: `ProfileCard` existe ⇒ `ProfileCardCompact`).

### Saída

O resultado é a tabela da seção `## Árvore de Componentes de DS` gravada no `design.md`, com as
colunas do template:

```
| Nó (nome Figma · main node-id · componentKey) | Tipo Figma | Veredito | Depende de | Paridade (campos que divergem inst.↔original) | Nome no código (proposto) | Fonte do catálogo | Task Type |
```

- **Veredito:** `Implementar` | `Importar` | `Atualizar` | `Derivar`.
- **Fonte do catálogo:** `código (existente)` | `Figma lib <url/libName>` | `só observado — catálogo não confirmado`.
- **Task Type:** ex.: `UI Component` para genéricos/derivados a implementar; `—` para "Importar".

Emita a tabela **exatamente** no formato de `templates/design.md` (mesmas colunas, mesma ordem).

---

## Passo 4 — Tratamento de erros e casos de borda

Cubra explicitamente cada caso abaixo. Nenhum deles aborta a fase silenciosamente.

- **Original órfão** (INSTANCE cujo `componentId` não resolve para nenhum componente em nenhuma lib
  nem na codebase): **implementar isolado + aviso**; não aborta. Veredito `Implementar`, Fonte do
  catálogo conforme disponível. Registre o aviso de que o original não foi encontrado.
- **Lib inacessível / URL da lib ausente:** implementar **observável** + aviso
  **"catálogo não confirmado"**. Isto é **distinto** de órfão — aqui o original existe (foi resolvido
  por `search_design_system`), mas o **catálogo completo de variantes** não pôde ser lido. É o
  caminho **padrão** sem a URL da lib.
- **429 (rate limit):** backoff 30–60s + retry (Passo 2). **Não falha a fase.** Se persistir,
  CONCERN, não erro fatal.
- **`search_design_system` ambíguo** (mais de um candidato): cruzar **nome + descrição +
  `componentKey`** para desambiguar. Se ainda ambíguo, **confirmar com o usuário** — não escolha no
  chute.
- **Instância sem overrides** (cópia exata do original): usar o genérico direto; **não criar
  derivado** (seção 1.1 de `references/ds-implementation.md`, caso especial).
- **Múltiplas instâncias do mesmo original:** uma resolução (um `get_design_context`), agrupadas
  conforme Passo 3e.
- **Set combinatório** (eixos `size × type × state`): os eixos viram **props independentes**, não um
  produto cartesiano de variantes (seção 3.3 de `references/ds-implementation.md`).
- **Componente compartilhado por vários pais:** **uma entrada única** na árvore; os pais o referenciam
  via coluna **Depende de**. Nunca duplicar a linha.
- **Veredito divergente entre telas** (a mesma instância aparece com diffs diferentes em telas
  diferentes): o **mais específico prevalece** (o que exige derivação ganha do que só reusa).
- **Árvore com 30+ nós:** **pedir priorização** ao usuário e **registrar o que ficou de fora** — nunca
  truncar em silêncio.

---

## Passo 5 — Hand back

Retorne a seção `## Árvore de Componentes de DS` montada (mais quaisquer avisos: "catálogo não
confirmado", originais órfãos, confiança reduzida de inventário, itens fora de escopo por
priorização) para quem invocou:

- no **modo workflow**, a fase design grava a seção no `design.md` e segue com as demais seções;
- no **modo standalone**, a `figma-component` usa a árvore para orquestrar a implementação do
  componente.
