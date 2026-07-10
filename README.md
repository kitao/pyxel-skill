# pyxel-skill

Standalone Pyxel game-building skill. It is intentionally small: modern models get more value from tight observation loops than from a large prescribed pipeline.

`pyxel-skill` decides what to build and how to verify it. [`pyxel-mcp`](https://github.com/kitao/pyxel-mcp) supplies the observation tools: `run`, `validate`, `pyxel_info`, `read_palette`, `read_image`, `read_animation`, `read_tilemap`, `read_audio`, and `diff_frames`.

## Status

`v1.2.0` targets pyxel-mcp >= 1.1.0 and Pyxel >= 2.9.6. The skill is three public files:

- `SKILL.md`: trigger, default loop, minimum verification, boundaries.
- `strict-mode.md`: optional release/audit evidence bundle.
- `pyxel-notes.md`: concise Pyxel footguns.

There is no default proof-bundle requirement, no stage pipeline, and no bundled stop hook. Use strict mode only when the user asks for release-grade evidence or the project size warrants it.

## Install

### 1. Register pyxel-mcp

Install and register pyxel-mcp >= 1.1.0 from PyPI via `uvx` first:

```bash
uvx pyxel-mcp install
```

Paste the printed MCP config into your client's MCP configuration. It should look like this:

```json
{
  "mcpServers": {
    "pyxel": { "command": "uvx", "args": ["pyxel-mcp"] }
  }
}
```

Ask the client to run `pyxel_info` and confirm `pyxel_mcp_version` is at least 1.1.0.

### 2. Install the skill

The installed folder or symlink must be named `pyxel`. Pick one route:

**One-liner (recommended)** — [skills CLI](https://github.com/vercel-labs/skills) installs and links the skill for 70+ agents:

```bash
npx skills add kitao/pyxel-skill
```

**Project-scoped** — commit the skill into a repository so every collaborator gets it:

```bash
git clone https://github.com/kitao/pyxel-skill.git .claude/skills/pyxel
```

**Manual clone + symlink** — the canonical source is `https://github.com/kitao/pyxel-skill.git`:

```bash
mkdir -p ~/src
git clone https://github.com/kitao/pyxel-skill.git ~/src/pyxel-skill
```

Then link it into the skill directory used by your client:

```bash
# Agent Skills default
mkdir -p ~/.agents/skills
test ! -e ~/.agents/skills/pyxel && ln -s ~/src/pyxel-skill ~/.agents/skills/pyxel

# Codex
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
test ! -e "${CODEX_HOME:-$HOME/.codex}/skills/pyxel" && ln -s ~/src/pyxel-skill "${CODEX_HOME:-$HOME/.codex}/skills/pyxel"

# Claude Code (personal)
mkdir -p ~/.claude/skills
test ! -e ~/.claude/skills/pyxel && ln -s ~/src/pyxel-skill ~/.claude/skills/pyxel
```

Restart the client after installing.

## Use

Ask for a Pyxel game or a Pyxel-game change. The skill should produce a playable slice, run `validate`, run the game headlessly, capture at least one frame, inspect the PNG, and report exact commands/results.

For release-level confidence, ask explicitly for strict mode or a proof bundle.

## Development

Content invariants are tested:

```bash
pytest test_skill_content.py
```

## Compatibility

| pyxel-skill | pyxel-mcp | Pyxel | Python |
|---|---|---|---|
| 1.2.0 | >= 1.1.0 | >= 2.9.6 | >= 3.10 |

## License

MIT. See `LICENSE`.
