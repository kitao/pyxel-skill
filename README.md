# pyxel-skill

[![Tests](https://img.shields.io/github/actions/workflow/status/kitao/pyxel-skill/test.yml?branch=main&label=tests)](https://github.com/kitao/pyxel-skill/actions/workflows/test.yml)

A standalone Agent Skill for building and verifying Pyxel games. It supplies task judgment and a proportional workflow; [pyxel-mcp](https://github.com/kitao/pyxel-mcp) supplies the observation tools.

Version v1.3.0 targets pyxel-mcp >= 1.2.0, Pyxel >= 2.9.6, and Python >= 3.11.

## Install

First register pyxel-mcp:

```bash
uvx pyxel-mcp install
```

Add the printed MCP configuration to the client and restart it. A `pyxel_info` call should report pyxel-mcp 1.2 or newer.

Then install the skill. The installed folder or symlink must be named `pyxel`.

With the [skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add kitao/pyxel-skill
```

For a project-scoped install:

```bash
git clone https://github.com/kitao/pyxel-skill.git .claude/skills/pyxel
rm -rf .claude/skills/pyxel/.git
```

For a shared local clone:

```bash
mkdir -p ~/src
git clone https://github.com/kitao/pyxel-skill.git ~/src/pyxel-skill

# Agent Skills
mkdir -p ~/.agents/skills
ln -s ~/src/pyxel-skill ~/.agents/skills/pyxel

# Codex
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -s ~/src/pyxel-skill "${CODEX_HOME:-$HOME/.codex}/skills/pyxel"

# Claude Code
mkdir -p ~/.claude/skills
ln -s ~/src/pyxel-skill ~/.claude/skills/pyxel
```

Restart the client after installing or updating the skill.

## Contents

- `SKILL.md` — trigger, runtime contract, default workflow, and boundaries.
- `references/pyxel.md` — Pyxel-specific behavior loaded only when relevant.
- `references/strict-mode.md` — opt-in release and audit evidence.

## Development

```bash
pytest -q test_skill_content.py
```

## Compatibility

| pyxel-skill | pyxel-mcp | Pyxel | Python |
|---|---|---|---|
| 1.3.0 | >= 1.2.0 | >= 2.9.6 | >= 3.11 |

## License

MIT. See [LICENSE](LICENSE).
