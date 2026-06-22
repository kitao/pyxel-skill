# pyxel-skill Architecture

`pyxel-skill` is a progressive-disclosure skill for building complete Pyxel games. It gives the agent a production workflow; `pyxel-mcp` supplies the observation tools.

## Role Split

- **Skill:** plan the game, decompose risky mechanics, maintain project state files, choose task-specific assertions, inspect visual artifacts, and decide whether the result satisfies the user's brief.
- **MCP:** run Pyxel headlessly, schedule inputs, capture snapshots, read Pyxel resources, render audio, diff frames, and expose Pyxel docs/resources.
- **Pyxel:** remains the engine and source of truth for APIs, examples, editors, packaging, and runtime behavior.

The skill intentionally does not define new MCP tools, mutate client configuration, or replace Pyxel documentation.

## Loading Model

`SKILL.md` is the entry point. It contains only the trigger, runtime requirements, pipeline map, resume rules, and anti-shortcut rules. Stage files are read just in time:

| Stage | File | Output |
|---|---|---|
| 1 | `visual-target.md` | visual direction and first `ASSETS.md` / `STRUCTURE.md` anchors |
| 2 | `decomposer.md` | `PLAN.md` with risks, milestones, and genre identity |
| 3 | `scaffold.md` | runnable `main.py`, structure notes, project marker |
| 4 | `asset-planner.md` | sprite/audio manifest |
| 5 | `asset-gen.md` | image-bank assets verified with `read_image` / `read_animation` |
| 6 | `task-execution.md` | gameplay implementation and milestone verification |
| 7 | `quality-gate.md` | proof bundle and `gate-report.json` |

Reference files (`test-harness.md`, `capture.md`, `quirks.md`, `knowledge/*`) are loaded only when a stage asks for them.

## Tool Surface

Requires `pyxel-mcp >= 1.0.0` with these 9 tools:

`run`, `validate`, `pyxel_info`, `read_palette`, `read_image`, `read_animation`, `read_tilemap`, `read_audio`, `diff_frames`.

No `judge_*` tools are part of the contract. Quality is asserted by the agent against observed values and visual artifacts.

## Persistent Game State

The generated game project owns these files:

- `PLAN.md`
- `STRUCTURE.md`
- `ASSETS.md`
- `MEMORY.md`

They survive context compaction and drive resume behavior. They are not repository metadata for `pyxel-skill` itself.
