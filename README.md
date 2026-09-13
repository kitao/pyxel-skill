# pyxel-skill

[![Tests](https://img.shields.io/github/actions/workflow/status/kitao/pyxel-skill/test.yml?branch=main&label=tests)](https://github.com/kitao/pyxel-skill/actions/workflows/test.yml)
[![Agent Skills](https://img.shields.io/badge/Agent_Skills-spec_compliant-blue)](https://agentskills.io/specification)
[![License](https://img.shields.io/github/license/kitao/pyxel-skill)](LICENSE)

An [Agent Skill](https://agentskills.io) for building and verifying [Pyxel](https://github.com/kitao/pyxel) games. It tells the agent what to build, how to drive the game, and what counts as evidence; [pyxel-mcp](https://github.com/kitao/pyxel-mcp) supplies the observation tools it drives.

Version 1.4.0 targets pyxel-mcp >= 1.3.0, Pyxel >= 2.9.6, and Python >= 3.11.

## Install

### Claude Code

The repository is also a plugin that bundles the pyxel-mcp server configuration:

```bash
claude plugin marketplace add kitao/pyxel-skill
claude plugin install pyxel@pyxel-skill
```

The plugin registers the `pyxel` MCP server as `uvx pyxel-mcp`, so do not add the server again by hand. The skill is available as `/pyxel:pyxel` and activates on its own for Pyxel work.

### Any agent with the skills CLI

Register pyxel-mcp first, then add the skill:

```bash
uvx pyxel-mcp install
npx skills add kitao/pyxel-skill
```

`uvx pyxel-mcp install` prints the setup command or config snippet for Claude Code, Codex CLI, Gemini CLI, Cursor, and VS Code. Restart the client after registering.

### Manual

The installed folder or symlink must be named `pyxel`.

```bash
git clone https://github.com/kitao/pyxel-skill.git .claude/skills/pyxel
rm -rf .claude/skills/pyxel/.git
```

For a shared local clone:

```bash
git clone https://github.com/kitao/pyxel-skill.git ~/src/pyxel-skill

# Agent Skills
mkdir -p ~/.agents/skills && ln -s ~/src/pyxel-skill ~/.agents/skills/pyxel

# Codex
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills" && ln -s ~/src/pyxel-skill "${CODEX_HOME:-$HOME/.codex}/skills/pyxel"

# Claude Code
mkdir -p ~/.claude/skills && ln -s ~/src/pyxel-skill ~/.claude/skills/pyxel
```

## Contents

- `SKILL.md` — trigger, runtime contract, default workflow, minimum evidence, and boundaries.
- `references/pyxel.md` — Pyxel behavior for input, drawing, assets, audio, and deterministic runs.
- `references/design.md` — presentation and game-feel defaults for new or polished games.
- `references/strict-mode.md` — opt-in release evidence and gates.
- `.claude-plugin/` and `.mcp.json` — Claude Code plugin manifest, marketplace entry, and bundled server configuration.

## Development

```bash
pip install pytest skills-ref
pytest -q test_skill_content.py
mkdir -p /tmp/skills && cp -R . /tmp/skills/pyxel && agentskills validate /tmp/skills/pyxel
claude plugin validate .
```

## Compatibility

| pyxel-skill | pyxel-mcp | Pyxel | Python |
|---|---|---|---|
| 1.4.0 | >= 1.3.0 | >= 2.9.6 | >= 3.11 |
| 1.3.0 | >= 1.2.0 | >= 2.9.6 | >= 3.11 |

See [CHANGELOG.md](CHANGELOG.md) for release notes.

## License

MIT. See [LICENSE](LICENSE).
