# pyxel-skill

[![Tests](https://img.shields.io/github/actions/workflow/status/kitao/pyxel-skill/test.yml?branch=main&label=tests)](https://github.com/kitao/pyxel-skill/actions/workflows/test.yml)
[![Agent Skills](https://img.shields.io/badge/Agent_Skills-spec_compliant-blue)](https://agentskills.io/specification)
[![License](https://img.shields.io/github/license/kitao/pyxel-skill)](LICENSE)

An [Agent Skill](https://agentskills.io) for building and verifying [Pyxel](https://kitao.dev/pyxel/) games. It guides implementation and verification for the requested game; [pyxel-mcp](https://github.com/kitao/pyxel-mcp) supplies the observation tools it drives.

Version 1.4.3 targets pyxel-mcp >= 1.3.1, Pyxel >= 2.9.6, and Python >= 3.11.

## Install

### Claude Code

The repository is also a plugin that bundles the pyxel-mcp server configuration:

```bash
claude plugin marketplace add kitao/pyxel-skill
claude plugin install pyxel@pyxel-skill
```

The plugin registers the `pyxel` MCP server as `uvx --from 'pyxel-mcp>=1.3.1' pyxel-mcp`, so do not add the server again by hand. The skill is available as `/pyxel:pyxel` and activates on its own for Pyxel work.

### Any agent with the skills CLI

Add the skill:

```bash
npx skills add kitao/pyxel-skill
```

For clients without automatic plugin registration, also follow [MCP setup](#mcp-setup). Claude Code recognizes this skill's plugin manifest and registers the bundled server; for a project install, trust the workspace and enable the server when prompted.

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

Claude Code loads a full checkout under `~/.claude/skills` as the plugin `pyxel@skills-dir`, which registers the `pyxel` MCP server from `.mcp.json` just like the plugin install, so do not add the server again by hand.

For Codex and other clients without automatic plugin registration, also follow [MCP setup](#mcp-setup).

### MCP setup

For a client without automatic plugin registration, print the setup examples:

```bash
uvx --from 'pyxel-mcp>=1.3.1' pyxel-mcp install
```

This command only prints instructions. Apply the command or configuration for your client, replacing the printed `uvx pyxel-mcp` with `uvx --from 'pyxel-mcp>=1.3.1' pyxel-mcp`. For example, register it with Codex CLI using:

```bash
codex mcp add pyxel -- uvx --from 'pyxel-mcp>=1.3.1' pyxel-mcp
```

The version requirement prevents `uvx` from reusing an older installed tool. If the server is already registered, update its existing command; for a plugin-managed server, update the plugin. Restart the client and confirm `pyxel_info` reports pyxel-mcp 1.3.1 or newer.

## Contents

- `SKILL.md` — trigger, runtime setup, implementation and verification workflow, and boundaries.
- `references/pyxel.md` — Pyxel behavior for input, drawing, assets, audio, and deterministic runs.
- `references/design.md` — presentation and feedback for new or polished games.
- `references/strict-mode.md` — broader coverage and retained evidence for release checks and audits.
- `.claude-plugin/` and `.mcp.json` — Claude Code plugin manifest, marketplace entry, and bundled server configuration.

## Development

```bash
pip install pytest skills-ref uv 'mcp>=2,<3'
pytest -q
mkdir -p /tmp/skills && cp -R . /tmp/skills/pyxel && agentskills validate /tmp/skills/pyxel
claude plugin validate .
```

The runtime tests need network access to install published MCP packages into temporary environments. They exercise the bundled server command with an older uv tool installed, verify inline frames and state, and execute the documented audio request. To run only the content checks, use `pytest -q test_skill_content.py`.

Content checks cover distribution metadata, local links, and server commands. Review prose changes for scope, clarity, and appropriate evidence; wording and document length are not test contracts.

## Compatibility

| pyxel-skill | pyxel-mcp | Pyxel | Python |
|---|---|---|---|
| 1.4.3 | >= 1.3.1 | >= 2.9.6 | >= 3.11 |
| 1.4.2 | >= 1.3.1 | >= 2.9.6 | >= 3.11 |
| 1.4.1 | >= 1.3.0 | >= 2.9.6 | >= 3.11 |
| 1.4.0 | >= 1.3.0 | >= 2.9.6 | >= 3.11 |
| 1.3.0 | >= 1.2.0 | >= 2.9.6 | >= 3.11 |

See [CHANGELOG.md](CHANGELOG.md) for release notes.

## License

MIT. See [LICENSE](LICENSE).
