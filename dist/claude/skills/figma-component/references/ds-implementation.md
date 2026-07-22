# Regras de Implementacao de Design System

Referencia compartilhada entre os implementadores (`figma-component-implementer` e `figma-design-implementer`). Define o corte reusar-vs-derivar e os padroes de implementacao para componentes de design system.

---

## 1. Corte Reusar vs. Derivar (R3)

Toda instancia Figma que referencia um componente generico do DS passa por um diff contra o original. O resultado desse diff determina se o generico e reusado diretamente ou se um derivado e criado.

### 1.1 Reusar o generico (so props/variant)

Reusar o componente generico existente -- passando props, variants e conteudo -- quando as **unicas** divergencias entre a instancia e o original forem:

- **Conteudo** (texto, imagem, icone) trocado dentro de slots existentes.
- **Valor de variant ou component-property ja existente** no original (ex.: `size="lg"` em vez de `size="md"`, `variant="secondary"` em vez de `variant="primary"`).
- **Mostrar/ocultar slot existente** (ex.: esconder o icone trailing que o generico ja expoe via prop booleana ou children opcionais).

Nessas condicoes, a instancia e uma **configuracao** do generico, nao uma derivacao. Nao crie um componente novo.

Caso especial: instancia sem nenhum override (copia exata do original) -- usar o generico direto; nao criar derivado.

### 1.2 Derivar (componente novo compondo o generico)

Criar um componente derivado quando **qualquer** divergencia ultrapassar o que props/variant expressam:

- **Filho adicionado ou removido** que nenhuma variant ou slot existente cobre (ex.: badge extra, segundo botao, indicador de status).
- **Mudanca de layout/estrutura** -- direcao do auto-layout alterada, reordenacao de filhos, hierarquia diferente.
- **Novos subcomponentes compostos** -- a instancia agrega outros componentes que o original nao preve.
- **Comportamento novo** -- interacao, animacao ou logica ausente no original (tooltip, drawer, validacao).
- **Estilo (cor/borda/spacing) fora do que token/variant expressa** -- se o estilo divergente nao pode ser atingido por nenhuma combinacao de variant + token existente, e uma derivacao.

### 1.3 Classificacao: so-conteudo vs. estrutural

Para eliminar ambiguidade no diff, classifique cada divergencia:

**Conta como so-conteudo (reusar):**

| Tipo | Exemplos |
|------|----------|
| Texto | Label, placeholder, titulo, descricao |
| Imagem/icone | Trocar icone dentro de um slot `icon`, trocar `src` de avatar |
| Valor de variant existente | `color="error"` quando o original suporta `color` |
| Visibilidade de slot | `showCloseButton={false}` quando o slot ja existe |

**Conta como estrutural (derivar):**

| Tipo | Exemplos |
|------|----------|
| Filho adicionado/removido | Badge sobre avatar, segundo CTA, divider extra |
| Layout alterado | Coluna vira linha, filhos reordenados, gap diferente |
| Subcomponente composto | Tooltip wrapping um botao, menu dropdown novo |
| Comportamento | Drag-and-drop, validacao inline, animacao de entrada |
| Estilo fora de token/variant | Cor de fundo customizada sem variant correspondente |

---

## 2. Padrao de Wrapper para Derivados

Um derivado e implementado como **wrapper**: um componente com interface propria que **compoe** o generico base por baixo. O generico base e sempre a primeira dependencia do derivado.

### 2.1 Estrutura

```
DerivadoCard
  └── GenericoCard (via import)
        ├── ...slots do generico...
        └── ...props passadas pelo wrapper...
  └── FilhosExtras (adicionados pelo wrapper)
```

O wrapper:

1. **Importa** o generico base e o renderiza como filho principal.
2. **Passa props** do generico via spread ou mapeamento explicito -- nao reimplementa a logica interna do generico.
3. **Adiciona** filhos, slots ou comportamento que justificaram a derivacao.
4. **Exporta** sua propria interface de props, que pode ser um superconjunto das props do generico ou uma interface independente que abstrai a complexidade.

### 2.2 O que NAO fazer

- **Nao duplique o generico.** Nunca copie o codigo-fonte do generico para dentro do derivado. Se voce precisa alterar o generico para acomodar o derivado, isso e uma atualizacao aditiva (secao 3.2) -- nao uma copia.
- **Nao substitua o generico por reimplementacao.** Se o derivado deixa de usar o generico e reimplementa tudo do zero, ele nao e um derivado -- e um componente separado, e a decisao de design deve refletir isso.
- **Nao importe o generico apenas para descartar a maior parte dele.** Se o wrapper usa menos de ~30% da renderizacao do generico, questione se a composicao faz sentido ou se um componente independente seria mais claro.

### 2.3 Composicao de multiplos componentes (peers)

Um **composto** difere de um **derivado**: o derivado (secoes 2/2.1) e um wrapper sobre **um unico** generico base do qual ele estende; um composto e um componente **novo** montado a partir de **N componentes peer**, sem um base primario unico. Exemplo: `multi-select = input + menu` -- nem o input nem o menu e "o base"; ambos sao filhos compostos lado a lado.

Os filhos de um composto chegam ao implementer pela lista `[COMPOSE_FROM]` (`{ nome de codigo, import path }` por filho). Quando o composto e implementado (verdict `implementar`), **todos os filhos ja existem no codigo** -- o orquestrador os implementou/importou antes, em ordem folhas->raiz. Regras:

1. **Importe e componha cada filho** de `[COMPOSE_FROM]` pelo seu import path resolvido -- renderize-os na estrutura que o Figma mostra.
2. **Nao reimplemente** nenhum filho listado (mesma proibicao da secao 2.2): nunca copie/reinline o codigo-fonte de um filho que ja existe.
3. **Adicione apenas** o que o composto tem de proprio: layout, wiring/estado entre os filhos, e quaisquer elementos extras que nao sejam os filhos.
4. **Exporte** sua propria interface de props, que orquestra os filhos (superconjunto ou interface independente que abstrai a composicao).

Se um filho listado nao existe ou seu import nao resolve, isso e um problema **BLOCKING** -- reporte, nao reimplemente para tapar o buraco (a ordenacao folhas->raiz do orquestrador deveria ter garantido a existencia).

---

## 3. Isolamento, Atualizacao Aditiva e Casos de Borda

### 3.1 Isolamento

Cada componente (generico ou derivado) e **isolado**:

- **Arquivo separado** -- um arquivo por componente (ou um diretorio com `index` + submodulos se a complexidade justificar).
- **Auto-contido** -- todas as dependencias sao importacoes explicitas; nenhum efeito colateral global alem de CSS-in-JS/modules scopados.
- **Exportado** -- o componente e exportado pelo seu modulo (named export ou default, conforme convencao do projeto) e pode ser importado de qualquer lugar sem dependencias implicitas.

### 3.2 Atualizacao Aditiva (R9)

Quando um generico existente precisa ser atualizado para acomodar novos usos:

- **So mudancas nao-quebrantes** (non-breaking): nova prop opcional, novo valor de variant, novo slot opcional. Consumidores existentes do generico nao devem ser afetados.
- **Aprovacao explicita** -- toda atualizacao aditiva exige aprovacao do usuario antes de ser aplicada. Nunca altere a interface publica de um generico sem confirmacao.
- **Se exigir breaking change, o veredito ja teria saido como "Derivar" na fase design.** Se durante a implementacao voce perceber que a atualizacao quebraria consumidores existentes, nao faca a atualizacao -- reporte um **BLOCKING** concern e indique que o veredito correto seria Derivar. A decisao entre atualizar e derivar pertence a fase de design, nao a de implementacao.

### 3.3 Props Independentes para Component Sets Combinatorios

Quando o Figma modela um component set com eixos combinatorios (ex.: `size` x `type` x `state`), implemente cada eixo como uma **prop independente**:

```typescript
// CORRETO: props independentes
interface ButtonProps {
  size?: 'sm' | 'md' | 'lg';
  variant?: 'primary' | 'secondary' | 'ghost';
  state?: 'default' | 'hover' | 'disabled';
}

// ERRADO: produto cartesiano
type ButtonKind =
  | 'sm-primary-default'
  | 'sm-primary-hover'
  | 'md-secondary-disabled'
  | /* ... explosao combinatoria ... */;
```

Cada prop aceita seus proprios valores sem depender dos outros (a menos que o Figma explicitamente restrinja uma combinacao). Props de estado de interacao (`hover`, `active`, `disabled`, `focus`) devem ser mapeadas para pseudo-classes CSS, nao expostas como props -- conforme documentado nos agents implementadores.

### 3.4 Subcomponentes de Terceiros

Quando o Figma referencia um subcomponente que pertence a outra biblioteca ou pacote (ex.: icone de um icon pack, componente de um DS externo):

- **Importar do pacote** -- use o import do pacote ja instalado no projeto.
- **Nao reimplemente** -- nunca recrie o subcomponente localmente. Se o pacote nao esta instalado, reporte como **NEEDS_CONTEXT** para que a dependencia seja adicionada.
- Antes de importar, verifique que o pacote esta declarado em `package.json` (ou equivalente). Se nao estiver, reporte.

### 3.5 Colisao de Nome

Antes de nomear um derivado, **cheque a codebase** para colisoes com simbolos existentes (componentes, types, utilitarios):

1. Busque pelo nome proposto no projeto.
2. Se colidir, proponha um nome alternativo que preserve a semantica (ex.: `ProfileCard` ja existe -> `ProfileCardCompact`, `ProfileCardWithBadge`).
3. Nunca sobrescreva ou shadow um simbolo existente sem aprovacao explicita.

### 3.6 Tratamento de Erros: Update que Exige Breaking Change

Se durante a implementacao uma atualizacao de generico exigiria breaking change (remocao de prop, alteracao de tipo, mudanca de comportamento default):

1. **Nao aplique a mudanca.**
2. Reporte como **BLOCKING** concern, citando: qual prop/comportamento quebraria, quais consumidores seriam afetados.
3. Indique que o veredito correto para esse caso e **Derivar** em vez de Atualizar -- a decisao pertence a fase de design.

Esta regra garante que a fronteira entre atualizar e derivar seja respeitada em runtime, mesmo quando a analise de design nao previu a necessidade.
