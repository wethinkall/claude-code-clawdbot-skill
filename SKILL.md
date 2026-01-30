---
name: claude-code-clawdbot
description: "Run Claude Code (Anthropic) from this host via the `claude` CLI (Agent SDK) in headless mode (`-p`) for codebase analysis, refactors, test fixing, and structured output. Use when the user asks to use Claude Code, run `claude -p`, use Plan Mode, auto-approve tools with --allowedTools, generate JSON output, or integrate Claude Code into Clawdbot workflows/cron." 
---

# Claude Code (Clawdbot)

Use the locally installed **Claude Code** CLI to run “headless” prompts (non-interactive) against the current codebase.

This skill is for **driving the Claude Code CLI**, not the Claude API directly.

## Quick checks

Verify installation:
```bash
claude --version
```

Run a minimal headless prompt (prints a single response):
```bash
./scripts/claude_code_run.py -p "Return only the single word OK."
```

## Core workflow

### 1) Run a headless prompt in a repo

```bash
cd /path/to/repo
/home/ubuntu/clawd/skills/claude-code-clawdbot/scripts/claude_code_run.py \
  -p "Summarize this project and point me to the key modules." \
  --permission-mode plan
```

### 2) Allow tools (auto-approve)

Claude Code supports tool allowlists via `--allowedTools`.
Example: allow read/edit + bash:
```bash
./scripts/claude_code_run.py \
  -p "Run the test suite and fix any failures." \
  --allowedTools "Bash,Read,Edit"
```

### 3) Get structured output

```bash
./scripts/claude_code_run.py \
  -p "Summarize this repo in 5 bullets." \
  --output-format json
```

### 4) Add extra system instructions

```bash
./scripts/claude_code_run.py \
  -p "Review the staged diff for security issues." \
  --append-system-prompt "You are a security engineer. Be strict." \
  --allowedTools "Bash(git diff *),Bash(git status *),Read"
```

## Notes (important)

- Claude Code sometimes expects a TTY. The wrapper script runs it through a pseudo-terminal using `script(1)` for reliability.
- Use `--permission-mode plan` when you want read-only planning.
- Keep `--allowedTools` narrow (principle of least privilege), especially in automation.

## Bundled script

- `scripts/claude_code_run.py`: wrapper that runs the local `claude` binary with a pseudo-terminal and forwards flags.
