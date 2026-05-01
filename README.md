# pyxel-skill

A [Claude Code](https://claude.com/claude-code) Skill that drives end-to-end production of playable, clearable, recognizable-sprite Pyxel games. Combines a phased workflow harness with topical knowledge files and an enforcement hook to prevent the agent from declaring "done" with placeholder garbage.

This skill assumes [`pyxel-mcp`](https://github.com/kitao/pyxel-mcp) is registered in your Claude Code MCP config — the skill orchestrates the workflow, while `pyxel-mcp` provides the verification verbs (run, capture, inspect, render audio).

## Status

v0.1.0 — initial release. Validation prompt: "make Donkey Kong". See `docs/retrospectives/` for actual run logs.

## Install

1. Clone this repo:

   ```bash
   git clone https://github.com/kitao/pyxel-skill.git
   ```

2. Symlink it into your Claude Code skills directory:

   ```bash
   ln -s "$(pwd)/pyxel-skill" ~/.claude/skills/pyxel
   ```

   (Or copy the directory if you prefer — symlink keeps you on the latest commit.)

3. Install the Stop hook (one-time per machine):

   ```bash
   ~/.claude/skills/pyxel/hooks/install.sh
   ```

   The hook is a non-blocking warning that fires at session end if the quality gate was skipped. It is idempotent.

4. Ensure `pyxel-mcp` is in your MCP config (`~/.claude/.mcp.json`):

   ```json
   {
     "mcpServers": {
       "pyxel": { "command": "uvx", "args": ["pyxel-mcp"] }
     }
   }
   ```

## Use

Activate the skill by asking Claude Code to make a Pyxel game:

> Make a Donkey Kong style platformer in Pyxel.

The skill orchestrates a 7-stage pipeline (visual-target → decomposer → scaffold → asset-planner → asset-gen → task-execution → quality-gate). Persistent state files (`PLAN.md`, `STRUCTURE.md`, `ASSETS.md`, `MEMORY.md`) survive context compaction so long sessions can resume cleanly.

## Repo layout

See `docs/superpowers/specs/2026-05-01-pyxel-harness-design.md` §4.1 for the canonical layout description. In short:

- `SKILL.md` — orchestrator
- `visual-target.md`, `decomposer.md`, `scaffold.md`, `asset-planner.md`, `asset-gen.md`, `task-execution.md`, `quality-gate.md` — 7 pipeline stages
- `quirks.md`, `test-harness.md`, `capture.md` — references loaded on demand by stages
- `knowledge/` — topical knowledge (pixel-art, background, game-feel, audio, patterns)
- `hooks/` — Stop hook + installer
- `docs/` — design docs, runtime architecture, validation, compatibility matrix

## License

MIT. See `LICENSE`.
