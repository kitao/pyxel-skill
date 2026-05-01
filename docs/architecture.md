# pyxel-skill Runtime Architecture

A concise reference to the shipping shape of `pyxel-skill`. For design rationale and the journey through alternatives, see `docs/superpowers/specs/2026-05-01-pyxel-harness-design.md`.

## Overview

`pyxel-skill` is a Claude Code Skill that orchestrates production of complete Pyxel games via a 7-stage workflow. The skill itself contains no executable game code — it directs Claude through reading stage instructions, writing artifacts (game source files + persistent state files), and verifying artifacts using `pyxel-mcp`'s tools.

## Components

### Orchestrator

`SKILL.md` — the file Claude Code's skill router activates on. Contains the trigger description, pipeline ASCII, anti-shortcut rules, resume-detection logic, and the capabilities table that points at every other file.

### Stages (read in pipeline order)

| Stage | File | Output artifacts |
|-------|------|------------------|
| 1 | `visual-target.md` | `ASSETS.md` `**Art direction:**` line; `STRUCTURE.md` `## Vision` section |
| 2 | `decomposer.md` | `PLAN.md` (Risk Tasks + Main Build + Win/Lose milestones + Audio Manifest) |
| 3 | `scaffold.md` | `STRUCTURE.md` Modules/Scenes/Tuning sections + skeleton `main.py` + `.pyxel-skill/` marker |
| 4 | `asset-planner.md` | `ASSETS.md` sprite manifest with identity contracts |
| 5 | `asset-gen.md` | `_build_assets()` populated; per-sprite verified via `inspect_sprite` / `inspect_animation` |
| 6 | `task-execution.md` | gameplay code; PLAN.md tasks marked done; MEMORY.md gotchas captured |
| 7 | `quality-gate.md` | `screenshots/result/<N>/gate-report.json` with PASS/FAIL per check |

### References (loaded on demand)

- `quirks.md` — Pyxel API gotchas. Loaded when behavior is surprising. Curated under godogen's "Keep this file small and high-signal" rule.
- `test-harness.md` — milestone playthrough. Loaded from Stage 6 before running win/lose path verification.
- `capture.md` — proof bundle production. Loaded from Stage 6/7 before producing intermediate or final captures.

### Knowledge (topical, JIT-loaded)

- `knowledge/pixel-art.md` — palette + 3-layer hierarchy + 3-color-per-material + sprite size guidelines.
- `knowledge/background.md` — bg tiers + parallax + screen size derivation + text layout.
- `knowledge/game-feel.md` — physics + variable jump + coyote/buffer + hitbox + camera + screen shake + hitstop.
- `knowledge/audio.md` — channel discipline + MML composition + SE cookbook + gen_bgm patterns.
- `knowledge/patterns.md` — title screen + scene state machine + level/enemy archetypes + animation timing.

### Hook

`hooks/stop_check_bundle.py` — Claude Code Stop hook. Non-blocking tripwire that warns at session end if `.pyxel-skill/` project marker exists but proof bundle is missing or `gate-report.json` shows unaddressed FAILs.

`hooks/install.sh` — idempotent installer that adds the hook to `~/.claude/settings.json` under `hooks.Stop`.

## Data flow

```
User brief
    ↓
[Stage 1] visual-target  ──→  ASSETS.md (Art direction)
                          ──→  STRUCTURE.md (Vision)
    ↓
[Stage 2] decomposer  ──→  PLAN.md
    ↓
[Stage 3] scaffold  ──→  STRUCTURE.md (Modules/Scenes/Tuning)
                    ──→  main.py (skeleton)
                    ──→  .pyxel-skill/ (project marker)
    ↓
[Stage 4] asset-planner  ──→  ASSETS.md (sprite manifest)
    ↓
[Stage 5] asset-gen  ──→  main.py:_build_assets() (hex sprites)
                     ──→  pyxel-mcp inspect_sprite / inspect_animation per sprite
    ↓
[Stage 6] task-execution  ──→  main.py (gameplay)
                          ──→  MEMORY.md (gotchas)
                          ←──  test-harness.md / capture.md (references)
    ↓
[Stage 7] quality-gate  ──→  screenshots/result/<N>/gate-report.json
    ↓
[Stop hook]  warns if bundle/gate state is incomplete
```

## Persistent state

Four files at the **game project root** (not the pyxel-skill repo):

- `PLAN.md` — Stage 2 → updated by Stage 6.
- `STRUCTURE.md` — Stage 1 (Vision) → Stage 3 (Modules etc.).
- `ASSETS.md` — Stage 1 (Art direction) → Stage 4 (manifest).
- `MEMORY.md` — Stage 6+ — discoveries and gotchas.

These survive context compaction. Resume detection (in `SKILL.md`) inspects them to determine where to re-enter the pipeline.

## Dependencies

- **`pyxel-mcp`** ≥ 0.9.3 (PyPI), registered in `~/.claude/.mcp.json` under namespace `pyxel`. Provides verification verbs.
- **`pyxel`** ≥ 2.8.7 (engine; pulled in by pyxel-mcp's dependencies).
- **Python** ≥ 3.10 (for the Stop hook).
- **`jq`** (for `hooks/install.sh`).

## See also

- `docs/superpowers/specs/2026-05-01-pyxel-harness-design.md` — design rationale and alternatives considered.
- `docs/superpowers/plans/2026-05-01-pyxel-skill-v0.1.0-implementation.md` — the implementation plan that produced this layout.
- `docs/validation/dk-reference.md` — Donkey Kong validation prompt + expected behavior.
- `docs/compatibility-matrix.md` — pyxel-skill ↔ pyxel-mcp ↔ Pyxel engine known-working pairs.
