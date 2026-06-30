---
name: release-notes
description: Gera documento de release em PT-BR a partir do diff entre duas tags git. Uso manual.
disable-model-invocation: true
---

# Release Notes

Gera um documento de release em **português (PT-BR)** a partir do diff entre duas tags git.
Ferramenta local de desenvolvimento — produz markdown no chat, não escreve arquivo.

**Uso:** `/release-notes <tag-base> <tag-alvo>`
- `<tag-base>` = tag mais antiga (ponto de partida)
- `<tag-alvo>` = tag mais recente (release sendo documentada)

O documento segue a estrutura: `🚀 Novidades`, `⚡ Melhorias`, `🐛 Correções` e um `📦 Resumo` final.

## Step 0 — Validar argumentos

São necessários **exatamente dois** argumentos de tag: `<from>` (base) e `<to>` (alvo).

Se algum estiver faltando, informe o uso correto e **PARE**:
```
Uso: /release-notes <tag-base> <tag-alvo>
```

## Step 1 — Verificar que as tags existem

```bash
git rev-parse -q --verify "refs/tags/<from>"
git rev-parse -q --verify "refs/tags/<to>"
```

Se qualquer comando falhar, reporte qual tag não existe e **PARE**. Liste candidatas para ajudar:
```bash
git tag --sort=-creatordate | head -20
```

## Step 2 — Validar a ordem (guard principal)

Compare a data do commit apontado por cada tag:
```bash
git log -1 --format=%ct "<from>"   # epoch (base)
git log -1 --format=%ct "<to>"     # epoch (alvo)
```

- Se o epoch de `<to>` **não for estritamente maior** que o de `<from>` (inclui o caso de datas
  iguais), a `<tag-alvo>` não é mais recente que a `<tag-base>`. **AVISE o usuário e PARE** — não
  gere o documento. Mostre as duas datas legíveis para contexto:
  ```bash
  git log -1 --format=%ci "<from>"
  git log -1 --format=%ci "<to>"
  ```
  Mensagem ao usuário, por exemplo:
  > A tag `<to>` (data X) não é mais recente que `<from>` (data Y). Verifique a ordem dos argumentos
  > (`/release-notes <tag-base> <tag-alvo>`). Geração interrompida.

- Caso contrário, prossiga.

## Step 3 — Coletar os dados do diff

```bash
git log --no-merges --format='%H%x09%s%x09%b' "<from>".."<to>"   # commits + corpos
git diff --stat "<from>".."<to>"                                  # visão geral de arquivos
git diff "<from>".."<to>"                                         # diff completo (análise semântica)
```

Para diffs muito grandes, prefira `--stat` + diffs por área (`git diff "<from>".."<to>" -- <path>`)
para não estourar o contexto. Os assuntos e corpos dos commits carregam a maior parte da intenção.

## Step 4 — Inferir e agrupar (análise)

Analise mensagens de commit + diff e decida o **bucket** de cada mudança pela intenção (não pelo
prefixo do commit):

- `🚀 Novidades` — novas capacidades/funcionalidades visíveis ao usuário
- `⚡ Melhorias` — refatorações, performance, simplificações, melhorias internas
- `🐛 Correções` — correções de bugs

Regras:
- **Una commits relacionados** em uma única entrada (não liste commits crus).
- Cada entrada = `### <título>` + 1 a 3 parágrafos curtos em PT-BR explicando **o que** mudou e
  **por quê** (prosa, como o template abaixo).
- **Omita** qualquer seção que não tenha entradas.

## Step 5 — Montar o `📦 Resumo`

Uma lista plana de bullets resumindo cada entrada acima, uma linha por mudança.

## Step 6 — Imprimir no chat

Imprima o markdown final no chat (não escreva arquivo). Onde uma imagem ajudaria, deixe o
placeholder `<!-- adicione screenshots aqui se relevante -->` — a skill não gera imagens; o usuário
adiciona manualmente (como os `<img>` do exemplo).

## Template de saída

```markdown
## 🚀 Novidades

### <título>
<parágrafos em PT-BR>

<!-- adicione screenshots aqui se relevante -->

---

## ⚡ Melhorias

### <título>
<parágrafos>

---

## 🐛 Correções

### <título>
<parágrafos>

---

## 📦 Resumo

* <bullet por mudança>
```
