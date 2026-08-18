---
name: statusline
description: Install or remove the afyapowers status line
disable-model-invocation: true
---
# /afyapowers:statusline — Install or Remove the afyapowers Status Line

You are installing (or removing) the afyapowers custom status line for the current user. It is installed **globally** in `~/.claude/settings.json` and applies to every project on this machine. Follow these steps exactly.

The status line shows, at the bottom of Claude Code: the afyapowers plugin version, model and context usage; the active feature, workflow phase (with task progress during implement) and the current Jira ticket — resolved per-project from the session's working directory, and simply omitted in projects without afyapowers; git branch/status, session cost and duration.

## Step 0: Preconditions

**Claude Code only.** The status line is a Claude Code feature (`statusLine` in `~/.claude/settings.json`). If you are running in any other IDE (Cursor, Gemini, GitHub Copilot), tell the user: "A status line do afyapowers é um recurso exclusivo do Claude Code — este IDE não a suporta." Then **stop**.

afyapowers requires Python 3.9+ at runtime. Check it is available:

```bash
command -v python3 >/dev/null && echo OK || echo MISSING
```

If the result is `MISSING`, tell the user: "O afyapowers requer Python 3.9+, que não está no seu PATH. Instale o Python 3.9 ou mais recente e rode `/afyapowers:statusline` novamente." Then **stop**.

## Step 1: Determine the Mode

- Default (no arguments, or words like "install", "on", "enable"): **install**.
- If the user asked for removal ("remove", "off", "uninstall", "disable", "remover", "desativar"): **remove**.

## Step 2: Run the Installer

Run the install script. The plugin root is in your session context (injected by the session-start hook as "Plugin root: ..."):

```bash
python3 "<plugin-root>/skills/statusline/scripts/install.py"
```

For removal, append `--remove`:

```bash
python3 "<plugin-root>/skills/statusline/scripts/install.py" --remove
```

The script is idempotent. On install it writes the user-level `~/.claude/afyapowers/plugin-root` pointer and merges a `statusLine` entry into `~/.claude/settings.json`, preserving every other key. On removal it deletes only the `statusLine` key.

Confirm the output is `ok=true`. If it is `ok=false` or the command errors, report the error output to the user and **stop**. In particular, if the failure mentions invalid JSON in `~/.claude/settings.json`, tell the user the file needs to be fixed by hand first — the installer never overwrites a broken settings file.

## Step 3: Confirm to the User

After a successful **install**, tell the user:
- A status line foi instalada globalmente para o seu usuário em `~/.claude/settings.json` e vale para todos os projetos; aparece na próxima interação (ou nova sessão).
- Ela é atualizada automaticamente quando o plugin for atualizado (o hook de início de sessão regrava o ponteiro `~/.claude/afyapowers/plugin-root`).
- Em projetos sem afyapowers, os segmentos de feature e Jira simplesmente não aparecem.
- Para removê-la: `/afyapowers:statusline remove`.

After a successful **remove**, tell the user the status line entry was removed from `~/.claude/settings.json` and the default footer returns on the next interaction.
