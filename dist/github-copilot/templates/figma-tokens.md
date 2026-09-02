# Tokens do Figma: {{feature_name}}

<!-- Artefato produzido pela skill reading-figma-designs (fase design). É a FONTE AUTORITATIVA dos
     VALORES de token do Figma para TODAS as fases seguintes (plan, implement, review). Consumidores
     leem ESTE ARQUIVO (ferramenta Read) — nunca uma cópia colada ou resumida em prompt: um resumo
     degradado re-introduz valores fabricados. -->
<!-- PROIBIÇÃO: nenhuma linha deste artefato pode vir de get_variable_defs sobre um ORIGINAL de
     design system (componente declarado em arquivo de DS, F2+). Originais em arquivo de DS resolvem
     variáveis no MODO PADRÃO da coleção — valores e até NOMES de token divergem do tema das telas
     (ex.: #1f1f1f vs #19174f; border/radius/full vs border/radius/md). Só frames de topo (T#) dos
     arquivos de TELAS entram aqui. -->
<!-- ESCOPO: este mapa responde "qual o valor do token X no tema das telas". Ele NÃO diz quais
     tokens um componente usa (não há mapeamento nó→token). É PROIBIDO derivar medidas de aceite por
     componente escolhendo tokens "plausíveis" desta tabela. -->

**captured-at:** `<ISO 8601 UTC>`
<!-- Obtido de um relógio real (`date -u +%Y-%m-%dT%H:%M:%SZ` via Bash) no momento das chamadas
     get_variable_defs. NUNCA inventado, estimado ou copiado de outro artefato. -->

## Proveniência

<!-- Uma linha por chamada get_variable_defs realizada — sempre sobre um frame de topo (T#) de
     arquivo de telas. Toda T# de ### Telas do design.md deve ter uma linha aqui. -->

| Chamada | Arquivo | Tela | Node ID | Tokens retornados |
|---------|---------|------|---------|-------------------|
| 1 | F1 (`<fileKey>`) | T1 — <nome da tela> | `<node_id>` | <n> |

## Tokens

<!-- Agrupados por prefixo (### color, ### spacing, ### border, ### typography, ### effect, …).
     "Telas" lista as T# em cuja resposta o token apareceu com esse valor. Valores idênticos em
     várias telas colapsam em uma linha. -->

### color

| Token | Valor | Tipo | Telas |
|-------|-------|------|-------|
| color/exemplo/accent/default | #19174f | COLOR | T1, T2 |

### spacing

| Token | Valor | Tipo | Telas |
|-------|-------|------|-------|

### border

| Token | Valor | Tipo | Telas |
|-------|-------|------|-------|

### typography

| Token | Valor | Tipo | Telas |
|-------|-------|------|-------|

### effect

| Token | Valor | Tipo | Telas |
|-------|-------|------|-------|

## Conflitos entre telas

<!-- ESCOPO RESTRITO: mesmo nome de token com valores diferentes entre T# DESTE(S) arquivo(s) de
     telas (ex.: telas em temas diferentes). Uma seção vazia é o esperado quando todas as telas
     compartilham o tema — e NÃO é evidência de ausência de conflito arquivo-de-telas ↔ arquivo-de-DS:
     nomes de token de um original de DS que não constam aqui são tratados na fase implement
     (cadeia de fallback do figma-component-implementer). Escreva "(nenhum)" quando vazio — nunca
     omita a seção. -->

| Token | Telas/Valores divergentes | Observação |
|-------|---------------------------|------------|

(nenhum)
