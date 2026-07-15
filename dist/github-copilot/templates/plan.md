# Plano de Implementação: {{feature_name}}

> **Para workers agênticos:** OBRIGATÓRIO: Use a skill de implementação do afyapowers para implementar este plano. Os passos usam sintaxe de checkbox (`- [ ]`) para rastreamento.

**Objetivo:** [Uma frase descrevendo o que isto constrói]

**Arquitetura:** [2-3 frases sobre a abordagem]

**Tech Stack:** [Principais tecnologias/bibliotecas]

---

### Task 1: [Nome do Componente]

**Files:**
- Create: `caminho/exato/do/arquivo`
- Modify: `caminho/exato/do/arquivo/existente:linhas`
- Test: `tests/caminho/exato/do/teste`

**Depends on:** none

- [ ] Passo 1: Escrever o teste que falha — descreva os comportamentos a testar e os resultados esperados
- [ ] Passo 2: Rodar o teste e confirmar que ele falha
- [ ] Passo 3: Implementar — descreva o que construir e as decisões-chave
- [ ] Passo 4: Rodar o teste e confirmar que ele passa

> O commit é feito pelo orquestrador após a conclusão da tarefa — não adicione um passo de commit.

### Task 2: [Nome da Tela] — Esqueleto (Layer 0) (Figma)

**Files:**
- Create: `caminho/exato/do/esqueleto` (o layout que envolve as seções da tela)

**Depends on:** none

**Figma:**
- **File Key:** `<file_key>`
- **Node ID:** `<id>` (frame raiz da tela)
- **Breakpoints:** <breakpoint_name> (<width>px), ...

> Esta task é a **dona do container**: largura máxima, centralização e margens laterais da página, mais o ritmo (gap) entre seções — tudo derivado da geometria do frame no Figma (ver Contrato de Layout do design). Tasks de tela/montagem (Layer 2) DEPENDEM desta task e não redefinem essas medidas.
>
> Componentes (Layer 1) são **PROIBIDOS** de setar max-width, centralização ou margens de página — eles vivem dentro do container que o esqueleto define. Quando um componente precisa de **full-bleed** legítimo (ex: banner que ultrapassa a margem lateral), ele usa o hook de escape exposto por este esqueleto (ex: prop/slot `fullBleed` ou classe utilitária documentada aqui) — nunca sobrescreve max-width/centralização diretamente no componente.

- [ ] Passo 1: Verificar a geometria do container vazio primeiro — sem conteúdo de seções, o esqueleto já deve exibir max-width, centralização e margens laterais corretas em todos os breakpoints
- [ ] Passo 2: Implementar o container — max-width, centralização, margens laterais e ritmo entre seções, conforme o Contrato de Layout do design
- [ ] Passo 3: Expor e documentar o hook de escape para full-bleed
- [ ] Passo 4: Rodar a verificação visual e confirmar que a geometria do container casa com o Contrato de Verificação (cenário de container vazio)

> O commit é feito pelo orquestrador após a conclusão da tarefa — não adicione um passo de commit.

### Task N: [Nome do Componente de UI] (Figma)

**Files:**
- Create: `caminho/exato/do/componente`

**Assets:** `<diretório de assets do projeto>/` — o implementador pode baixar & criar arquivos de ícone/imagem aqui conforme necessário (arquivos exatos desconhecidos no momento do plano)

**Depends on:** none | Task X

**Figma:**
- **File Key:** `<file_key>`
- **Node ID:** `<id>`
- **Breakpoints:** <breakpoint_name> (<width>px), ...
- **Medidas de aceite:** container max-width `<valor>`, margens laterais `<valor>`, gaps `<valor>`, colunas `<n>`, min/max de `<peça>` no breakpoint `<breakpoint_name>` (do Contrato de Layout)
- **Cenários:** pior caso (`<descrição, ex: texto mais longo/mais itens>`), estado vazio, estado com 1 item (do Contrato de Verificação)

- [ ] Implementar usando o workflow do implementador Figma
