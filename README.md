# pyxel-skill

Standalone Pyxel game-building skill. It is intentionally small: modern models get more value from tight observation loops than from a large prescribed pipeline.

`pyxel-skill` decides what to build and how to verify it. `pyxel-mcp >= 1.0.0` supplies the observation tools: `run`, `validate`, `pyxel_info`, `read_palette`, `read_image`, `read_animation`, `read_tilemap`, `read_audio`, and `diff_frames`.

## Status

`v1.1.0` targets pyxel-mcp 1.0.0 and Pyxel 2.9.6+. The default skill is three public files:

- `SKILL.md`: trigger, default loop, minimum verification, boundaries.
- `strict-mode.md`: optional release/audit evidence bundle.
- `pyxel-notes.md`: concise Pyxel footguns.

There is no default proof-bundle requirement, no stage pipeline, and no bundled stop hook. Use strict mode only when the user asks for release-grade evidence or the project size warrants it.

## Install

Install and register pyxel-mcp >= 1.0.0 from PyPI via `uvx` first:

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

Ask the client to run `pyxel_info` and confirm `pyxel_mcp_version` is at least 1.0.0. If your package index does not have 1.0.0 yet, release pyxel-mcp first or point the MCP config at a local pyxel-mcp checkout for development.

Then install this repository as a host-native skill. The canonical source for the skill is `https://github.com/kitao/pyxel-skill.git`.

Clone once:

```bash
mkdir -p ~/src
git clone https://github.com/kitao/pyxel-skill.git ~/src/pyxel-skill
```

Then link it into the skill directory used by your client. The installed folder or symlink must be named `pyxel`. Examples:

```bash
# Agent Skills default
mkdir -p ~/.agents/skills
test ! -e ~/.agents/skills/pyxel
ln -s ~/src/pyxel-skill ~/.agents/skills/pyxel

# Codex
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
test ! -e "${CODEX_HOME:-$HOME/.codex}/skills/pyxel"
ln -s ~/src/pyxel-skill "${CODEX_HOME:-$HOME/.codex}/skills/pyxel"

# Claude Code
mkdir -p ~/src ~/.claude/skills
test ! -e ~/.claude/skills/pyxel
ln -s ~/src/pyxel-skill ~/.claude/skills/pyxel
```

Restart the client after installing.

## Use

Ask for a Pyxel game or a Pyxel-game change. The skill should produce a playable slice, run `validate`, run the game headlessly, capture at least one frame, inspect the PNG, and report exact commands/results.

For release-level confidence, ask explicitly for strict mode or a proof bundle.

## Compatibility

| pyxel-skill | pyxel-mcp | Pyxel | Python |
|---|---|---|---|
| 1.1.0 | >= 1.0.0 | >= 2.9.6 | >= 3.10 |

## License

MIT. See `LICENSE`.
