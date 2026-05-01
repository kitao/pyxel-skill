# pyxel-skill v0.1.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the pyxel-skill Claude Code Skill repo at `/Users/takashi/repos/pyxel-skill` end-to-end per the design spec at `docs/superpowers/specs/2026-05-01-pyxel-harness-design.md`, ending with a tagged v0.1.0 that successfully drives a "make Donkey Kong" prompt to a clearable, recognizable-sprite Pyxel game.

**Architecture:** Single-repo Claude Code Skill. Orchestrator (`SKILL.md`) directs JIT-loading of 7 stage files (visual-target → quality-gate), 3 reference files (quirks/test-harness/capture), 5 knowledge files (pixel-art/background/game-feel/audio/patterns). Pyxel-specific Stop hook (`hooks/stop_check_bundle.py`) provides non-blocking enforcement of bundle integrity. The skill drives the existing `pyxel-mcp` MCP server (≥0.9.3) for verification verbs.

**Tech Stack:** Markdown (skill content), Python 3.10+ (Stop hook), bash (install.sh). git for branch/release. No build system; the skill is plain text + one Python script.

**Reference documents:**
- Spec: `docs/superpowers/specs/2026-05-01-pyxel-harness-design.md` (944 lines)
- godogen reference: `/tmp/godogen` (clone of `htdt/godogen`)
- v3-era drafts: archived to `archive/v3-drafts` branch in Task 1
- pyxel-mcp current `instructions.md`: `/Users/takashi/repos/pyxel-mcp/src/pyxel_mcp/instructions.md` (906 lines, source for knowledge file migration)

**Out of scope (separate plans):**
- pyxel-mcp 0.9.3 trim (`feat/v0.9.3-trim-instructions` branch, spec §10) — separate plan, can run in parallel after Task 28 unblocks the mcp release
- Codex / Gemini-CLI / non-Claude-Code agent compatibility — future work per spec §2

---

## Task 1: Archive v3-era drafts and start v5 branch

**Files:**
- Modify (commit on archive branch): `SKILL.md`, `visual-target.md`, `decomposer.md`, `scaffold.md`, `asset-planner.md`, `asset-gen.md`, `task-execution.md`, `test-harness.md`, `capture.md`, `quality-gate.md`, `quirks.md`
- Branch state changes only — no file content changes

- [ ] **Step 1: Verify current git state**

```bash
cd /Users/takashi/repos/pyxel-skill
git status
```

Expected: branch `feat/harness`, modified `SKILL.md`, 10 untracked `.md` files (visual-target through quirks), spec doc + plan dir present under `docs/superpowers/`.

- [ ] **Step 2: Confirm v5 spec doc + this plan are committed somewhere safe**

The spec and plan files should not be lost during the branch dance. Verify they exist:

```bash
ls /Users/takashi/repos/pyxel-skill/docs/superpowers/specs/2026-05-01-pyxel-harness-design.md
ls /Users/takashi/repos/pyxel-skill/docs/superpowers/plans/2026-05-01-pyxel-skill-v0.1.0-implementation.md
```

Both files must exist. If they don't, stop — the spec and plan are the input to all later tasks.

- [ ] **Step 3: Create archive branch with v3 drafts**

```bash
cd /Users/takashi/repos/pyxel-skill
git checkout -b archive/v3-drafts
git add SKILL.md visual-target.md decomposer.md scaffold.md \
        asset-planner.md asset-gen.md task-execution.md \
        test-harness.md capture.md quality-gate.md quirks.md
git commit -m "archive: v3-era draft files for reference"
```

Expected: clean commit on `archive/v3-drafts` containing the 11 v3-era files.

- [ ] **Step 4: Switch to main and create v5 working branch**

```bash
git checkout main
git checkout -b feat/harness-v5
```

Expected: on `feat/harness-v5`, branched from main. The v3 files are NOT present in this branch's working tree (they live only on `archive/v3-drafts`). Spec doc and this plan ARE present (they were already committed under `docs/superpowers/`).

- [ ] **Step 5: Verify clean state**

```bash
git status
ls
```

Expected: clean working tree. Top-level: `LICENSE`, `.gitignore`, `.claude/`, `docs/` (containing the spec + plan). No v3-era stage files.

- [ ] **Step 6: Commit branch checkpoint**

No content commit needed yet — the branch creation itself is the checkpoint. Move to Task 2.

---

## Task 2: Set up directory skeleton

**Files:**
- Create: `knowledge/`, `hooks/`, `docs/retrospectives/`, `docs/validation/` (directories only)

- [ ] **Step 1: Create knowledge directory**

```bash
cd /Users/takashi/repos/pyxel-skill
mkdir -p knowledge
touch knowledge/.gitkeep
```

`.gitkeep` keeps the directory tracked even before files exist.

- [ ] **Step 2: Create hooks directory**

```bash
mkdir -p hooks
touch hooks/.gitkeep
```

- [ ] **Step 3: Create docs subdirectories**

```bash
mkdir -p docs/retrospectives docs/validation
touch docs/retrospectives/.gitkeep docs/validation/.gitkeep
```

- [ ] **Step 4: Verify structure**

```bash
find . -type d -not -path './.git*' | sort
```

Expected output:
```
.
./.claude
./docs
./docs/retrospectives
./docs/superpowers
./docs/superpowers/plans
./docs/superpowers/specs
./docs/validation
./hooks
./knowledge
```

- [ ] **Step 5: Commit skeleton**

```bash
git add knowledge/.gitkeep hooks/.gitkeep docs/retrospectives/.gitkeep docs/validation/.gitkeep
git commit -m "chore: scaffold directory skeleton (knowledge, hooks, docs/{retrospectives,validation})"
```

---

## Task 3: Write `.gitignore`

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: Check if `.gitignore` already exists**

```bash
cat /Users/takashi/repos/pyxel-skill/.gitignore 2>&1
```

The repo already has one (per Task 1 ls output). Read it before overwriting.

- [ ] **Step 2: Write `.gitignore`**

If the existing file is one line (likely `.DS_Store` or similar), replace with the full set. Otherwise append missing entries.

```
# pyxel-skill .gitignore

# OS
.DS_Store
Thumbs.db

# Editor
.vscode/
.idea/
*.swp
*~

# Python (for hooks/)
__pycache__/
*.pyc
.pytest_cache/
.venv/
venv/

# Test / scratch
*.log
/tmp/
```

Write to `/Users/takashi/repos/pyxel-skill/.gitignore`.

- [ ] **Step 3: Verify**

```bash
cat /Users/takashi/repos/pyxel-skill/.gitignore
```

Expected: file contains all the entries above.

- [ ] **Step 4: Commit**

```bash
git add .gitignore
git commit -m "chore: expand .gitignore for editor / Python / scratch artifacts"
```

---

## Task 4: Write `LICENSE`

**Files:**
- Verify: `LICENSE` (MIT) — existing file from before v5

- [ ] **Step 1: Read existing LICENSE**

```bash
head -5 /Users/takashi/repos/pyxel-skill/LICENSE
```

Expected: standard MIT license header. If the file already says "MIT License" with copyright notice for Takashi Kitao, no change needed; skip remaining steps.

If it does not exist or is wrong, continue to Step 2.

- [ ] **Step 2: Write MIT LICENSE if missing**

```
MIT License

Copyright (c) 2026 Takashi Kitao

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 3: Commit only if changed**

```bash
git status -- LICENSE
```

If modified, commit:

```bash
git add LICENSE
git commit -m "chore: confirm MIT LICENSE for v5"
```

If unchanged, no commit.

---

## Task 5: Write `README.md`

**Files:**
- Create or replace: `README.md`

- [ ] **Step 1: Check existing README**

```bash
cat /Users/takashi/repos/pyxel-skill/README.md 2>&1
```

The current README is a v3-era stub. Replace entirely.

- [ ] **Step 2: Write the new README.md**

Create `/Users/takashi/repos/pyxel-skill/README.md` with this exact content:

````markdown
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
````

- [ ] **Step 3: Verify**

```bash
wc -l /Users/takashi/repos/pyxel-skill/README.md
```

Expected: ~70 lines.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: write v0.1.0 README"
```

---

## Task 6: Write `SKILL.md` orchestrator

**Files:**
- Create: `SKILL.md`

This is the file Claude Code's skill router loads when activation matches. It must contain the frontmatter (description triggers activation), the pipeline diagram, anti-shortcut rules, and resume detection. Spec §5 is the authoritative source.

- [ ] **Step 1: Write `SKILL.md`**

Create `/Users/takashi/repos/pyxel-skill/SKILL.md` with this content:

````markdown
---
name: pyxel
description: Build complete retro games with Pyxel through a verified, gated pipeline. TRIGGER when the user wants to make a Pyxel / retro / 8-bit / pixel-art game, or asks to recreate a classic arcade title. DO NOT TRIGGER on general Python work, on existing non-Pyxel projects, or when a different game engine (Pygame, Godot, Unity) is mentioned.
license: MIT
---

# pyxel — Retro Game Production Harness

Build playable, clearable, recognizable-sprite Pyxel games via a phased pipeline that prevents shortcut "done" declarations. Every stage gates the next; the agent cannot self-certify completion without observable artifacts.

## Required runtime

This skill assumes `pyxel-mcp` ≥ 0.9.3 is installed and registered as an MCP server reachable at the namespace `pyxel`. On activation, before reading any stage file, verify:

- `mcp__pyxel__pyxel_info` is callable.
- `mcp__pyxel__validate_script` is callable.

If absent, run:

```bash
uvx pyxel-mcp --version
```

If not installed, instruct the user to add to their `.mcp.json`:

```json
{
  "mcpServers": {
    "pyxel": { "command": "uvx", "args": ["pyxel-mcp"] }
  }
}
```

The skill cannot proceed without these tools. Bail with a clear message if Claude Code's permission prompt for `uvx` is denied.

## Pipeline

```
User request: "make a Pyxel game ..."
        |
        +-- PLAN.md exists? (Resume Detection — see below)
        |     |
        |     +-- yes: read PLAN.md / STRUCTURE.md / MEMORY.md / ASSETS.md, jump to Stage 6
        |     +-- no: continue
        |
        +-- Stage 1  visual-target  -> ASSETS.md "Art direction" + STRUCTURE.md "Vision"
        +-- Stage 2  decomposer     -> PLAN.md (Risk Tasks + Main Build + Win/Lose milestones)
        +-- Stage 3  scaffold       -> STRUCTURE.md complete + skeleton main.py + .pyxel-skill/ marker
        +-- Stage 4  asset-planner  -> ASSETS.md sprite manifest
        +-- Stage 5  asset-gen      -> _build_assets() populated, per-sprite verified
        |
        +-- Show user a concise plan summary (risk tasks if any, main build scope)
        |
        +-- Stage 6  task-execution
        |     +-- Risk Slice: implement each PLAN.md risk task in isolation, verify, commit
        |     +-- Main Build: implement remainder, verify, commit
        |     +-- (calls test-harness.md and capture.md as references when needed)
        |
        +-- Stage 7  quality-gate   -> flat stop-conditions list; FAIL -> loop back to phase that owns the failure
        |
        +-- Proof bundle present at screenshots/result/<N>/
        +-- Stop hook fires (best-effort assertion that bundle is well-formed)
        +-- Summary to user
```

Each stage file is read **only when entering that stage** (JIT loading). Reference files (`quirks.md`, `test-harness.md`, `capture.md`, and any `knowledge/*`) are loaded on demand from within stage files, not eagerly.

## Capabilities

| File | Purpose | When to read |
|------|---------|--------------|
| `visual-target.md` | Stage 1: art direction + Vision section | Pipeline start (no PLAN.md) |
| `decomposer.md` | Stage 2: PLAN.md authoring | After Stage 1 |
| `scaffold.md` | Stage 3: STRUCTURE.md + skeleton + marker | After Stage 2 |
| `asset-planner.md` | Stage 4: ASSETS.md sprite manifest | After Stage 3 |
| `asset-gen.md` | Stage 5: hex-string sprite implementation + verify | After Stage 4 |
| `task-execution.md` | Stage 6: gameplay implementation loop | After Stage 5 (or on resume) |
| `quality-gate.md` | Stage 7: stop-conditions + PASS/FAIL report | At end of Stage 6 |
| `quirks.md` | Pyxel API gotchas | When Pyxel behaves unexpectedly |
| `test-harness.md` | Milestone playthrough verification | Called from Stage 6 |
| `capture.md` | Proof bundle production | Called from Stage 6 / Stage 7 |
| `knowledge/pixel-art.md` | Sprite + palette + color hierarchy | Stage 4, Stage 5, Stage 7 |
| `knowledge/background.md` | Bg + parallax + screen layout | Stage 1, Stage 3, Stage 7 |
| `knowledge/game-feel.md` | Physics + jumps + hitboxes + camera + shake | Stage 6 |
| `knowledge/audio.md` | SE cookbook + MML + channel discipline | Stage 3, Stage 6 |
| `knowledge/patterns.md` | Title screen, scene SM, level/enemy, animation timing | Stage 3, Stage 6 |

## Persistent state

Four files at project root, written across stages, read on resume:

| File | First written by | Purpose |
|------|------------------|---------|
| `PLAN.md` | Stage 2 | Risk Tasks (Approach + Verify) + Main Build modules + Win/Lose milestone tables |
| `STRUCTURE.md` | Stage 3 | Architecture: modules, scene state machine, tuning constants, Vision (from Stage 1) |
| `ASSETS.md` | Stage 1 (Art direction line) → Stage 4 (sprite manifest) | Art direction + sprite manifest |
| `MEMORY.md` | Stage 6+ | Discoveries, gotchas, what worked / didn't |

If the conversation grows long, summarize relevant state into these files and continue from artifacts instead of conversational memory.

## Resume Detection

`ASSETS.md` is touched by **both** Stage 1 (writes the `**Art direction:**` line) and Stage 4 (appends the sprite manifest with `## Sprites` / `## Player` / etc. headings). Resume must inspect content, not just existence:

On entry, check (in order):

1. `PLAN.md` exists at project root → resume mode. Read PLAN / STRUCTURE / MEMORY / ASSETS, route to Stage 6 unless `screenshots/result/<latest>/gate-report.json` shows incomplete earlier stages.

2. `ASSETS.md` exists but `PLAN.md` does not:
   - If `ASSETS.md` contains any sprite-manifest heading (`## Player`, `## Sprites`, `## Hazard`, etc.) → re-enter Stage 2 (Stage 4 was started without Stage 2; reconcile: PLAN.md milestones must reference assets actually planned).
   - Else (only `**Art direction:**` line) → re-enter Stage 2.

3. `STRUCTURE.md` exists but `PLAN.md` and `ASSETS.md` do not → unusual. Treat as corrupted state; ask the user whether to discard and restart.

4. None exist → fresh pipeline, start at Stage 1.

## Anti-shortcut rules

These are the cheats this harness exists to catch. Do not commit any of them.

1. **Visual primacy.** When code says X happened but a captured frame shows Y, trust the capture.
2. **Trust media over code.** A passing `validate_script` and `run_and_capture` only certify the script does not crash. They do not certify gameplay.
3. **No procedural fallback.** `pyxel.rect(x, y, 16, 16, 8)` in place of a declared sprite means asset-gen was skipped. Go back. The `pyxel.rect()` calls for player/enemy bodies are a red flag.
4. **Bundle integrity.** A `screenshots/result/<N>/` bundle whose first 3 seconds are correct and the rest is static is FAIL, not partial pass.
5. **Bias toward failure.** If behavior is not clearly visible in the capture, treat as not-done. Hidden or inferred behavior does not count.
6. **Closed-loop input only.** Open-loop scripted input drifts past ~200 frames. Use `play_and_capture` with state observation between segments.
7. **No "looks fine".** Every verify is a specific predicate against an observed value, not a vibe check.
8. **No bundle, no done.** A `screenshots/result/<N>/` directory containing win-path.gif, lose-path.gif, frames, audio WAVs is the precondition for declaring "done". A green gate report without a bundle is FAIL.

## Quality gate is the contract

Done is whatever `quality-gate.md`'s stop conditions say is done. The agent cannot skip ahead, cannot self-certify, and cannot claim "done" with unaddressed FAILs. Re-enter whichever phase the FAIL points to, remediate, re-run the gate.

The Stop hook (`hooks/stop_check_bundle.py`) fires at session boundary as a non-blocking tripwire. It surfaces missing bundles or unaddressed gate FAILs to the user — it does not replace the agent running the gate.

## What is NOT this skill's job

- Generic Python work, library development, non-game scripts.
- Non-Pyxel game engines (Godot, Unity, Pygame).
- Pure pyxel-mcp connector usage. If a user only needs verification tools without the harness, they should invoke `pyxel-mcp` directly without this skill.

## Reference

- Pyxel API: fetch via `pyxel://api-reference` MCP resource.
- Pyxel examples: `pyxel://examples/<name>` MCP resources (e.g., `02_jump_game`, `09_shooter`).
- Pyxel default palette: `pyxel://palette/default` MCP resource.
- pyxel-mcp tool catalog: see its loaded `instructions`.
- Design rationale: `docs/superpowers/specs/2026-05-01-pyxel-harness-design.md`.
````

- [ ] **Step 2: Verify the file**

```bash
wc -l /Users/takashi/repos/pyxel-skill/SKILL.md
head -10 /Users/takashi/repos/pyxel-skill/SKILL.md
grep -c '^## ' /Users/takashi/repos/pyxel-skill/SKILL.md
```

Expected: ~140 lines, frontmatter present, ~10 H2 sections.

- [ ] **Step 3: Commit**

```bash
git add SKILL.md
git commit -m "feat(skill): write SKILL.md orchestrator (frontmatter, pipeline, anti-shortcut rules, resume detection)"
```

---

## Task 7: Write `visual-target.md` (Stage 1)

**Files:**
- Create: `visual-target.md`

Spec §7.1 is the source. Stage 1 outputs the **Art direction** line in ASSETS.md and a **Vision** subsection in STRUCTURE.md (window contract, palette budget plan, layout map, object enumeration, HUD, audio cues, win/lose definitions). Carry forward v3 visual-target.md content but rebrand REFERENCE.md → STRUCTURE.md/ASSETS.md per spec §9.1 rename map.

- [ ] **Step 1: Read the spec section and v3 source**

```bash
sed -n '/^### 7.1 visual-target/,/^### 7.2 /p' /Users/takashi/repos/pyxel-skill/docs/superpowers/specs/2026-05-01-pyxel-harness-design.md
git show archive/v3-drafts:visual-target.md > /tmp/v3-visual-target.md
cat /tmp/v3-visual-target.md
```

The v3 file describes 7 sections to write into REFERENCE.md. Translate each section per the rename map in spec §9.1.

- [ ] **Step 2: Write `visual-target.md`**

Create `/Users/takashi/repos/pyxel-skill/visual-target.md` with this content:

````markdown
# Stage 1: Visual Target

Anchor the art direction in text **before any code is written**. Every spatial and stylistic choice committed here becomes a downstream requirement: the asset planner enumerates objects from the Vision subsection, the test harness measures against milestones derived from win/lose definitions, and the quality gate compares output frames to the layout described here.

Pyxel runs in 16 colors at small resolutions. The visual target is a **structured text spec**, not an external image. Do not generate `reference.png`; do not invoke any AI image API.

## Inputs

- The user's natural-language brief.
- `knowledge/pixel-art.md` (palette + 3-layer hierarchy).
- `knowledge/background.md` (screen size derivation).
- `knowledge/audio.md` (channel discipline).

## Outputs

Two artifacts, both at project root:

1. **`ASSETS.md`** — create the file with one top-level heading and one **Art direction** line. Sprite manifest is filled by Stage 4; do not touch that here.

   ```markdown
   # Assets

   **Art direction:** <one-paragraph description of the visual identity, palette mood, and overall scene vibe>
   ```

2. **`STRUCTURE.md`** — create the file with one top-level heading and a **Vision** section containing the seven subsections below. Architecture details (modules, scene state machine, tuning constants) are filled by Stage 3.

   ```markdown
   # Architecture

   ## Vision

   ### Window contract
   ...

   ### Palette budget
   ...

   ### Layout
   ...

   ### Objects
   ...

   ### HUD
   ...

   ### Audio
   ...

   ### Win / lose conditions
   ...
   ```

## What goes in each Vision subsection

### Window contract

```
Screen: <W>x<H>  (e.g., 224x256 — portrait arcade aspect)
FPS:    30 or 60
Title:  "<game title shown in window bar>"
Background color (palette idx): <0–15>
```

Choose Pyxel's screen size from playfield content, not the other way around. Standard arcade-style portrait: 224x256 or 192x224. Standard side-scroller: 256x192 or 256x144. See `knowledge/background.md` "Screen & Text Layout" for the content-first sizing pattern.

### Palette budget

List the indices used and the role each plays. The 3-layer hierarchy (dark backgrounds, mid environment, bright interactive) from `knowledge/pixel-art.md` should be visible:

```
0  black     — background void / outline
1  navy      — background detail (sky / shadow)
3  green     — foliage / pickups
4  brown     — terrain / wood
8  red       — interactive (hazards, enemy projectiles)
10 yellow    — interactive (pickups, score)
14 pink      — characters (skin / accent)
15 peach     — characters (highlight)
```

A flat use of red on navy is a contrast failure and will FAIL the quality gate. Use 10-14 of the 16 colors.

### Layout

ASCII map at one cell per 8 px (or coarser if the screen is large). Mark static structure and the spawn position of each named object.

```
.................................   y=0
......BBB.HELP!.PP...............   y=8   B = boss, P = princess
......BBB.......PP...............
=================================   y=16  girder 0
.....l...........l...............   y=24  l = ladder
=================================   y=48  girder 1
.....l...........l...............
M================================   y=136 girder 4 (Mario start, M)
                                    y=144 (screen bottom)
```

Coordinates are exact — the decomposer reads them as numbers in Stage 2.

### Objects

For every distinct object in the layout, list once with:

```
- <name>:
  - represents: "<one-sentence description an outsider would identify>"
  - sprite size: <WxH> pixels
  - palette: <list of 3-5 palette indices used>
  - quantity in scene: <int> (e.g., 1 for player, "spawned by boss" for barrels)
  - initial position: (x, y)
  - states/frames: <e.g., "idle, walk1, walk2, jump, climb1, climb2">
```

The **represents** line is the asset-gen identity contract: a stranger shown the rendered sprite without context must be able to identify it as that thing. Single-color blobs do not satisfy this contract.

### HUD

Every text/UI element with screen position:

```
- score:     "1UP / <digits>"   at (4, 4),     color 8
- highscore: "HIGH / <digits>"  at (W/2-12, 4), color 7
- level:     "L=<dd>"           at (W-32, 4),  color 10
- bonus:     "BONUS <dddd>"     at (W-48, 12), color 10
- lives:     mini-Mario icons   at (4, 12),    color 14
- "HELP!" above princess         blinking, color 8
- "HOW HIGH CAN YOU GET?"        intro screen, color 10
```

### Audio

Every player-visible event needs SE. List each declared sound channel and what it triggers on:

```
ch0 (BGM melody):  loops while scene == PLAY
ch1 (BGM bass):    pairs with ch0
ch2 (BGM harmony): pairs with ch0
ch3 (SE):
  - SE jump:        on btnp(KEY_SPACE), ascending square wave
  - SE climb step:  on btn(UP/DOWN) every 8 frames while climbing
  - SE death:       on barrel collision, descending tone
  - SE win:         on princess reach, ascending arpeggio
```

BGM uses ch0–ch2; SE uses ch3 only. Volume 5–7 for SE so it cuts through BGM. Square or pulse tone for melodic SE; noise tone is inaudible over BGM and fails verification. See `knowledge/audio.md` for SE cookbook recipes.

### Win / lose conditions

```
Win condition:  player.y <= <int> AND |player.x - princess.x| < <int>
                 → scene = WIN within 30 frames
Lose condition: lives == 0
                 → scene = GAME_OVER within 30 frames
Death event:    barrel collision → lives -= 1, respawn at start, barrels cleared
```

These predicates feed the win/lose milestone tables that Stage 2 (decomposer) writes into PLAN.md.

## Anti-patterns in this stage

- **"Mario or Mario-like character"** — vague reference. The asset planner can't generate for vague references; commit to a specific look in `represents:`.
- **"Pretty background"** without enumerating *what* fills it. The background gets forgotten downstream and the result is plain navy.
- **Listing colors but not their role.** The contrast rule needs roles. Without them, palette hierarchy can't be checked.
- **Skipping HUD because "we'll add it later".** Layout coordinates change under HUD; plan it now.
- **Marking the screen as small (e.g., 128x128) and then trying to fit 4 platforms + ladders + HUD + DK + princess.** Pixel budget runs out. Pick screen from content (see `knowledge/background.md`).

## When this stage is done

- `ASSETS.md` exists with the `# Assets` heading and one `**Art direction:**` line.
- `STRUCTURE.md` exists with the `# Architecture` heading and a `## Vision` section containing all seven subsections above, populated.
- Move to Stage 2 (read `decomposer.md`).
````

- [ ] **Step 3: Verify**

```bash
wc -l /Users/takashi/repos/pyxel-skill/visual-target.md
grep -c '^### ' /Users/takashi/repos/pyxel-skill/visual-target.md
```

Expected: ~150 lines; ~10 H3 sections (the seven Vision subsections + a few others).

- [ ] **Step 4: Commit**

```bash
git add visual-target.md
git commit -m "feat(stage): write visual-target.md (Stage 1: Art direction + Vision authoring)"
```

---

## Task 8: Write `decomposer.md` (Stage 2)

**Files:**
- Create: `decomposer.md`

Spec §7.2 is the source. Stage 2 converts the Stage 1 vision into PLAN.md (Risk Tasks + Main Build + Win/Lose milestones + Audio Manifest pointer). Carry forward v3 risk taxonomy.

- [ ] **Step 1: Read spec and v3 source**

```bash
sed -n '/^### 7.2 decomposer/,/^### 7.3 /p' /Users/takashi/repos/pyxel-skill/docs/superpowers/specs/2026-05-01-pyxel-harness-design.md
git show archive/v3-drafts:decomposer.md > /tmp/v3-decomposer.md
cat /tmp/v3-decomposer.md
```

- [ ] **Step 2: Write `decomposer.md`**

Create `/Users/takashi/repos/pyxel-skill/decomposer.md` with this content:

````markdown
# Stage 2: Decomposer

Convert STRUCTURE.md "Vision" into a verifiable plan with risk isolation and milestone tables for the quality gate.

## Inputs

- `STRUCTURE.md` "Vision" subsection (from Stage 1).
- `ASSETS.md` "Art direction" (from Stage 1).
- The user's original brief.

## Output

`PLAN.md` at project root, with five sections in this order:

1. **Risk Tasks** — features that need isolation (omit entirely if no risks identified).
2. **Main Build** — modules + cross-cutting verify criteria.
3. **Win Path Milestones** — input/assert table.
4. **Lose Path Milestones** — input/assert table.
5. **Audio Manifest** — restated from STRUCTURE.md "Vision → Audio" for downstream consumption.

(Asset Manifest is forward-referenced — Stage 4 fills `ASSETS.md` directly.)

## Pyxel-specific risk taxonomy

These features fail unpredictably and produce ambiguous bugs when mixed with other systems. Each becomes a Risk Task implemented in isolation first.

| Feature | Why risky |
|---------|-----------|
| Variable-jump physics | Tuning gravity vs. initial velocity hits "can't reach platform" or "skips platform above" |
| Sloped platform collision | Y has to follow `y = lerp(y0, y1, (x-x0)/(x1-x0))` while walking |
| Ladder snap + transition | Off-by-one on platform transition causes either fall-through or refusal-to-mount |
| Object-on-tilted-girder rolling | Direction depends on slope sign; flip at edge or fall when running off; AI implementations frequently get the off-edge fall wrong |
| Multi-state animation transitions | walk → jump → land state machine with frame timing; easy to leave stuck-in-jump or flickering |
| Closed-loop input simulation | Open-loop key sequences drift over long playthroughs (200+ frames) |
| Headless audio determinism | Sounds defined but not heard in `render_audio` because the timing slot was not populated before the game loop start |
| Image bank initialization order | `pyxel.images[N].set` must run before any `blt`; AI sometimes puts sprite definitions inside `update()` |

Anything *not* in this list is Main Build — implement directly, no isolation.

## Verify criteria — required structure

Every task gets a `Verify:` field with **specific, observable** criteria. "Looks right" is not a criterion. Each criterion names the tool that observes it and the predicate.

```
Verify (jump physics):
  - inspect_state at frame 30 (after btnp KEY_SPACE at frame 5):
      assert player.y < player_initial_y - 16
  - inspect_state at frame 50:
      assert player.y == player_initial_y
      assert player.vy == 0

Verify (sloped girder walk):
  - play_and_capture inputs that hold KEY_RIGHT for 60 frames,
    inspect_state at frames 20, 40, 60:
      for each: assert abs(player.y - expected_slope_y(player.x)) < 2

Verify (ladder climb):
  - play_and_capture hold KEY_UP at ladder x for 60 frames:
      inspect_state milestones every 10 frames:
        assert player.y monotonically decreases
        assert player.y reaches platform_above.y - player_h within 60 frames
```

## Win Path Milestones table

```markdown
## Win Path Milestones

| Frame | Inputs (held until next row) | Asserts |
|-------|-----------------------------|---------|
| 30    | KEY_SPACE press (start)     | scene == "PLAY", player.x ≈ <start_x>, player.y ≈ <start_y> |
| 60    | KEY_RIGHT held              | player.x > <start_x> + 20 |
| 120   | KEY_UP at ladder_a x        | player.y < <floor_y> - 8 |
| 200   | (continuing climb)          | player.y < <floor_y> - 32 |
| ...   | ...                         | ... |
| 600   | KEY_UP near princess        | player.y < 32 |
| 660   | (no input)                  | scene == "WIN" |
```

Closed-loop note: the test harness reads observed values; if they don't match the planned trajectory within tolerance, the milestone FAILs. For paths longer than ~200 frames, the test harness will steer in segments (see `test-harness.md`).

## Lose Path Milestones table

```markdown
## Lose Path Milestones

| Frame | Inputs       | Asserts |
|-------|--------------|---------|
| 30    | KEY_SPACE    | scene == "PLAY", lives == 3 |
| 100   | (no input)   | a barrel exists somewhere on a girder below the boss |
| 200   | (no input)   | barrel.y >= player.y - 8 (barrel close to floor) |
| 240   | (no input)   | lives <= 2 (player got hit at least once) |
| 360   | (no input)   | lives == 0 |
| 420   | (no input)   | scene == "GAME_OVER" |
```

Standing still must lead to GAME_OVER within 10–14 seconds at the configured fps (≈ 300–420 frames at 30fps). Faster = unfair; slower = the lose path is poorly defined and won't reliably trigger. The quality gate enforces this window in stop condition #10.

## Output template

````markdown
# PLAN: <Title>

## Risk Tasks

### R1. <feature>
- **Why isolated:** <one sentence — what makes this algorithmically hard>
- **Approach:** <algorithmic strategy or key constraints — enough for the implementor to know *how*, not just *what*>
- **Verify:** <bulleted observable checks per the structure above>
- **Status:** pending | in-progress | done

### R2. ...

(Omit the entire "Risk Tasks" section if no risks identified.)

## Main Build

### Modules
- <list each main file/class to be implemented and its responsibility>

### Verify (cross-cutting)
- Movement direction matches player input
- Animation direction matches movement direction
- Physics objects respond to gravity and collision
- UI readable, no overflow or overlap
- No missing-asset placeholder rectangles
- <game-specific checks>
- Win path scene transition fires
- Lose path scene transition fires

## Win Path Milestones
<table per format above>

## Lose Path Milestones
<table per format above>

## Audio Manifest
<from STRUCTURE.md "Vision → Audio", restated here for quality_gate consumption>
````

## Anti-patterns in this stage

- **Verify lines that say "looks right", "feels good", "matches reference"** — these cannot be automated and the gate cannot enforce them.
- **Milestones with no `inputs` column** — without scripted inputs there's no playthrough.
- **Lose path with no death trigger** — if barrels are too slow / random / cannot actually hit a stationary player, the lose path can't be verified.
- **Single milestone per path** — the gate needs intermediate milestones to detect early divergence (degenerate "first 30 frames look fine then static" bundles).
- **Risk tasks without `Approach`** — the implementor will hit the same risky pitfall the isolation was meant to catch.

## When this stage is done

- `PLAN.md` exists at project root with all five sections populated.
- Risk Tasks (if any) each have Why / Approach / Verify / Status.
- Main Build has at least one Module and at least the cross-cutting Verify list.
- Both Win Path and Lose Path tables have at least 5 rows including the start frame and the terminating-scene frame.
- Audio Manifest has one row per declared SE / BGM channel.
- Move to Stage 3 (read `scaffold.md`).
````

- [ ] **Step 3: Verify**

```bash
wc -l /Users/takashi/repos/pyxel-skill/decomposer.md
grep -c '^## ' /Users/takashi/repos/pyxel-skill/decomposer.md
```

Expected: ~150 lines; ~10 H2 sections.

- [ ] **Step 4: Commit**

```bash
git add decomposer.md
git commit -m "feat(stage): write decomposer.md (Stage 2: PLAN.md authoring + risk taxonomy)"
```

---

## Task 9: Write `scaffold.md` (Stage 3)

**Files:**
- Create: `scaffold.md`

Spec §7.3 is the source. Stage 3 finishes STRUCTURE.md (modules, scene SM, constants), writes a runnable skeleton main.py (TITLE only, no gameplay), and creates `.pyxel-skill/` project marker.

- [ ] **Step 1: Read spec and v3 source**

```bash
sed -n '/^### 7.3 scaffold/,/^### 7.4 /p' /Users/takashi/repos/pyxel-skill/docs/superpowers/specs/2026-05-01-pyxel-harness-design.md
git show archive/v3-drafts:scaffold.md > /tmp/v3-scaffold.md
cat /tmp/v3-scaffold.md
```

- [ ] **Step 2: Write `scaffold.md`**

Create `/Users/takashi/repos/pyxel-skill/scaffold.md` with this content (the prose should follow the structure of v3-scaffold.md but with v5 file-naming, and add the `.pyxel-skill/` marker step):

````markdown
# Stage 3: Scaffold

Lock the architecture before writing gameplay logic. Output: STRUCTURE.md filled in completely (modules, scene state machine, tuning constants — Vision is already there from Stage 1) plus a runnable skeleton `main.py` and a `.pyxel-skill/` project marker.

## Inputs

- `PLAN.md` (from Stage 2): module list, win/lose conditions.
- `STRUCTURE.md` "Vision" (from Stage 1): window contract, palette plan, scene transitions.
- `knowledge/background.md` (screen size derivation, text layout).
- `knowledge/patterns.md` (scene state-machine template, title-screen recipe).
- `knowledge/audio.md` (channel allocation only — SE definitions come in Stage 5/6).

## Outputs

1. **`STRUCTURE.md`** — append the architectural sections below the existing `## Vision` section.
2. **`main.py`** — runnable skeleton at project root.
3. **`.pyxel-skill/`** — directory at project root containing `stage-marker` (text file with the current stage name) and `gate-snapshots/` (empty subdirectory). The Stop hook (`hooks/stop_check_bundle.py`) detects projects by the presence of this directory.

## Architecture contract

Every Pyxel game has the same outer shape:

```python
class App:
    def __init__(self):
        pyxel.init(W, H, title=TITLE, fps=FPS)
        self._build_assets()      # populate images / sounds before loop
        self._reset()
        pyxel.run(self.update, self.draw)

    def _build_assets(self): ...  # images[N].set, sounds[N].set/mml
    def _reset(self): ...         # initial state for TITLE scene
    def update(self): ...         # scene dispatch
    def draw(self):  ...          # scene dispatch

App()
```

Scenes go through a finite state machine. Minimal arcade game has 4–5:

```
TITLE  -- press_start -->  PLAY  -- die -->  GAME_OVER  -- press_start --> TITLE
                            PLAY  -- win -->  WIN        -- press_start --> TITLE
```

Some games add INTRO ("HOW HIGH CAN YOU GET?") between TITLE and PLAY.

## STRUCTURE.md sections to add

After the existing `## Vision` section, append:

```markdown
## Modules

- `main.py`
  - `App` class — entry point, scene dispatch, asset build.
  - `Player` class — physics, animation state, draw.
  - `<Hazard>` class (e.g., `Barrel`) — pattern + draw.
  - `<Boss>` class (if applicable) — simple state machine for spawn timer.
  - module-level constants (see Tuning).
  - module-level layout (`PLATFORMS`, `LADDERS`).

## Scene state machine

| State | Entry | Exit transitions |
|-------|-------|-----------------|
| TITLE | initial | btnp(SPACE) → PLAY (or INTRO) |
| INTRO | from TITLE | timer expiry → PLAY |
| PLAY  | from INTRO/TITLE | lives == 0 → GAME_OVER; win predicate → WIN |
| WIN   | from PLAY | btnp(SPACE) after delay → TITLE |
| GAME_OVER | from PLAY | btnp(SPACE) after delay → TITLE |

## Tuning (constants from PLAN.md / Vision)

```python
W, H = 224, 256
FPS = 30
GRAVITY = 0.4
JUMP_VY = -3.6
WALK_SPEED = 1.0
CLIMB_SPEED = 1.0
MAX_FALL_SPEED = 6.0
TITLE, INTRO, PLAY, WIN, GAME_OVER = 0, 1, 2, 3, 4
```

These are committed values. Changing them invalidates milestones in PLAN.md — re-lock the plan if physics constants shift.

## State persistence between scenes

The `App` instance owns:
- score, hi_score
- lives
- current_level
- player (instance recreated on level start)
- hazards list (cleared on level start, on death)
- frame counter (monotonic, used for animation timing)

## Verification

- `validate_script main.py` — clean.
- `run_and_capture main.py --frames=30` — TITLE scene captures (text visible, blink prompt working, BG color matches Vision).
```

## Skeleton `main.py` shape

```python
import pyxel

W, H = 224, 256
FPS = 30
TITLE_SCENE, INTRO, PLAY, WIN, GAME_OVER = 0, 1, 2, 3, 4
BG = 0  # black; replace with Vision-specified value

class App:
    def __init__(self):
        pyxel.init(W, H, title="<Title from Vision>", fps=FPS)
        self._build_assets()
        self._reset()
        pyxel.run(self.update, self.draw)

    def _build_assets(self):
        # populated in Stage 5
        pass

    def _reset(self):
        self.scene = TITLE_SCENE
        self.frame = 0
        self.score = 0
        self.hi_score = 0
        self.lives = 3

    def update(self):
        self.frame += 1
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        s = self.scene
        if s == TITLE_SCENE:
            self._update_title()
        elif s == INTRO:
            self._update_intro()
        elif s == PLAY:
            self._update_play()
        elif s == WIN:
            self._update_win()
        elif s == GAME_OVER:
            self._update_gameover()

    def draw(self):
        pyxel.cls(BG)
        s = self.scene
        if s == TITLE_SCENE:
            self._draw_title()
        elif s == INTRO:
            self._draw_intro()
        elif s == PLAY:
            self._draw_play()
        elif s == WIN:
            self._draw_win()
        elif s == GAME_OVER:
            self._draw_gameover()

    def _update_title(self):
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.scene = PLAY  # or INTRO if applicable

    def _draw_title(self):
        t = "<TITLE>"
        pyxel.text((W - len(t) * 4) // 2, H // 2 - 16, t, 7)
        if self.frame % 40 < 28:
            t2 = "PRESS SPACE"
            pyxel.text((W - len(t2) * 4) // 2, H // 2 + 16, t2, 10)

    # Other scene update/draw methods are stubs — populated in Stage 6.
    def _update_intro(self): pass
    def _draw_intro(self): pyxel.text(8, 8, "INTRO (stub)", 7)
    def _update_play(self): pass
    def _draw_play(self): pyxel.text(8, 8, "PLAY (stub)", 7)
    def _update_win(self): pass
    def _draw_win(self): pyxel.text(8, 8, "WIN (stub)", 7)
    def _update_gameover(self): pass
    def _draw_gameover(self): pyxel.text(8, 8, "GAME OVER (stub)", 7)


App()
```

The skeleton must run cleanly. Verify:

- `validate_script main.py` is clean (no syntax errors, no anti-pattern warnings).
- `run_and_capture main.py --frames=30` returns a non-empty image showing the TITLE text and blinking prompt.

## Project marker

Create `.pyxel-skill/` at project root:

```bash
mkdir -p .pyxel-skill/gate-snapshots
echo "stage-3-scaffold-complete" > .pyxel-skill/stage-marker
```

The Stop hook reads this directory to identify pyxel-skill projects. Do not commit `.pyxel-skill/gate-snapshots/` — add to `.gitignore` of the *generated* game project (not pyxel-skill itself):

```
# .gitignore for game projects scaffolded by pyxel-skill
.pyxel-skill/gate-snapshots/
screenshots/
```

## Anti-patterns in this stage

- **Putting gameplay code in scaffold.** The skeleton must be empty of gameplay; verifying scaffold means verifying scene transitions and scene rendering, not whether the player can jump.
- **Embedding magic numbers in update/draw without lifting them to module-level constants.** PLAN.md milestones reference constants by name; inlined numbers can't be cross-checked.
- **Coupling scene update with rendering.** Update reads input and changes state; draw reads state and renders. Mixed concerns make scene transitions hard to verify.

## When this stage is done

- `STRUCTURE.md` has Modules, Scene state machine, Tuning, State persistence, Verification sections appended.
- `main.py` runs and shows TITLE without errors (`validate_script` clean, `run_and_capture --frames=30` shows TITLE).
- `.pyxel-skill/stage-marker` exists and contains `stage-3-scaffold-complete`.
- Move to Stage 4 (read `asset-planner.md`).
````

- [ ] **Step 3: Verify**

```bash
wc -l /Users/takashi/repos/pyxel-skill/scaffold.md
```

Expected: ~200 lines.

- [ ] **Step 4: Commit**

```bash
git add scaffold.md
git commit -m "feat(stage): write scaffold.md (Stage 3: STRUCTURE.md + skeleton main.py + project marker)"
```

---

## Task 10: Write `asset-planner.md` (Stage 4)

**Files:**
- Create: `asset-planner.md`

Spec §7.4 is the source.

- [ ] **Step 1: Read spec and v3 source**

```bash
sed -n '/^### 7.4 asset-planner/,/^### 7.5 /p' /Users/takashi/repos/pyxel-skill/docs/superpowers/specs/2026-05-01-pyxel-harness-design.md
git show archive/v3-drafts:asset-planner.md > /tmp/v3-asset-planner.md
cat /tmp/v3-asset-planner.md
```

- [ ] **Step 2: Write `asset-planner.md`**

Create `/Users/takashi/repos/pyxel-skill/asset-planner.md` with content based on v3 asset-planner.md (Image bank layout / Identity contract / Palette discipline / Required asset categories / Hex string strategy / Anti-patterns / When this stage is done sections), modified to:

- Open with "Stage 4" header and Inputs / Outputs blocks.
- Reference `knowledge/pixel-art.md` for palette + 3-layer hierarchy + 3-color-per-material rules.
- Update the Output description: ASSETS.md exists with the `**Art direction:**` line (from Stage 1); this stage appends sprite manifest sections (`## Player`, `## Antagonist`, `## Hazard`, `## HUD`, etc.).
- Each sprite entry must include: bank/region, `represents:`, palette, min distinct color regions, silhouette density bound, frame relations (paired-frame diff target).

Full file content (~150 lines):

````markdown
# Stage 4: Asset Planner

Inventory every sprite the game needs, with image bank coordinates, palette plan, and identity contract. Catches "I'll add it later" before it becomes a missing-asset bug.

## Inputs

- `STRUCTURE.md` "Vision → Objects" (from Stage 1).
- `STRUCTURE.md` "Modules" (from Stage 3) — class names map to sprite categories.
- `PLAN.md` "Main Build → Modules" (from Stage 2).
- `knowledge/pixel-art.md` — 16-color palette, 3-layer hierarchy, 3-color-per-material rule, sprite size guidelines, sprite design process.

## Output

`ASSETS.md` at project root, **appended to** (do not overwrite the `**Art direction:**` line written by Stage 1). Add the sprite manifest sections below.

## Image bank layout

Pyxel's default has 3 image banks, each 256x256, storing 8-bit (palette index) pixels. Layout sprites in bank 0 in a grid pattern:

```
Image bank 0 layout (256x256):
  (0,   0)–(95,  15):   player walk cycle (6 × 16x16)
  (96,  0)–(127, 15):   hammer states (2 × 16x16)
  (128, 0)–(159, 31):   boss (32x32)
  (160, 0)–(175, 23):   princess (16x24)
  (0,  32)–(31,  47):   barrel rolling (2 × 16x16)
  (0,  48)–(7,   55):   score digit "0" through (72, 48)–(79, 55) digit "9"
  ...
```

Pack tightly. Reserve a clearly-marked "free" region for additions. **Avoid placing visible content at (0, 0)** — Pyxel tilemap cells default to tile (0, 0) and will flood the tilemap with that content if it is visible.

## Identity contract per asset

For every named asset, write:

```markdown
### player_walk_1

- **bank/region:** 0 / (0, 0, 16, 16)
- **represents:** "Mario in red cap and blue overalls, mid-stride, facing right. Visible: cap, eye dot, mustache silhouette, two arms (one extended), two legs (one forward)."
- **palette:** [0 outline, 8 cap, 12 overalls, 14 skin, 15 highlight, 7 buttons]
- **min distinct color regions:** 5 (cap / face / overalls / arms-or-legs / outline)
- **silhouette:** non-transparent pixels < 95% of 16x16 box, > 15% of box
- **frame relations:** paired with `player_walk_2`; paired-frame diff must be 5–50% of pixels
```

The `represents:` field is the asset-gen identity contract. After implementation, a stranger shown the rendered sprite without the label must be able to identify it as "Mario walking". The quality gate (#4) tests against this constraint via `inspect_sprite` (color count, fill ratio) and `inspect_animation` (per-frame diff).

## Palette discipline per asset

Each sprite uses 3–6 colors from the global palette. Patterns from `knowledge/pixel-art.md` "3-Color-Per-Material Rule":

| Material        | Shadow | Base    | Highlight |
|-----------------|--------|---------|-----------|
| Skin            | 4 (brown) | 15 (peach) | 7 (white) |
| Green creature  | 3 (green) | 11 (lime)  | 10 (yellow) |
| Blue creature   | 1 (navy)  | 6 (light blue) | 12 (cyan) |
| Red creature    | 2 (purple)| 8 (red)    | 9 (orange) |
| Metal           | 5 (dark blue) | 13 (gray) | 7 (white) |
| Wood / barrel   | 4 (brown) | 9 (orange) | 15 (peach) |
| Foliage         | 3 (green) | 11 (lime)  | 7 (white) |

Single-color sprites ("a brown rectangle") FAIL the identity contract.

## Required asset categories

For an arcade-style platformer like Donkey Kong, minimum manifest:

```markdown
## Player

- player_idle (16x16)
- player_walk_1 (16x16)
- player_walk_2 (16x16)
- player_jump (16x16)
- player_climb_1 (16x16)
- player_climb_2 (16x16)
- player_dead (16x16) — optional spinning frame

## Antagonist (boss)

- boss_idle (32x32)
- boss_throw_1 (32x32) — optional, animation when spawning hazard
- boss_throw_2 (32x32)

## Goal (princess)

- princess (16x24)

## Hazard (barrel)

- barrel_1 (16x16)
- barrel_2 (16x16) — second roll frame, must differ from barrel_1

## Power-up (optional)

- hammer_carry (16x16)
- hammer_swing (16x16)

## HUD

- life_icon (8x8)
- digit_0 .. digit_9 (8x8) — only if drawing custom score font

## Environment (optional, can be `pyxel.rect()` if hand-drawn)

- girder_tile (8x8 tileable)
- ladder_tile (8x8 tileable)
- rivet (4x4)
```

The princess and barrel are minimums; without them the game isn't the genre. Hammer can be deferred.

## Generation strategy: hex strings

Pyxel sprites are defined via:

```python
pyxel.images[0].set(x, y, [
    "0888880000000000",
    "8888888800000000",
    ...
])
```

Each character is a hex digit (0–f) representing palette index. Width = line length; height = list length. The `0` here is treated as palette color 0 unless `colkey=0` is passed in `blt()`, in which case 0 = transparent.

For Stage 5 (asset-gen), write strings line-by-line and verify incrementally with `inspect_sprite`.

## Anti-patterns in this stage

- **"I'll figure out the sprites while coding"** — leads to last-minute rectangle blobs.
- **Listing assets without `represents:`.** Stage 5 has no acceptance criterion; the gate FAILs check #4.
- **Listing assets without palette plan.** Result: every sprite is gray.
- **Reusing the same sprite for "walking" and "idle" without saying so.** Animation diff check FAILs.
- **Skipping outline color.** Sprites blend into background; contrast warnings trip in `inspect_palette`.

## When this stage is done

- `ASSETS.md` has full manifest with at least Player / Antagonist / Goal / Hazard / HUD sections populated.
- Each entry has `bank/region`, `represents`, `palette`, `min distinct color regions`, `silhouette`, `frame relations`.
- No two entries claim overlapping bank regions.
- Move to Stage 5 (read `asset-gen.md`).
````

- [ ] **Step 3: Verify**

```bash
wc -l /Users/takashi/repos/pyxel-skill/asset-planner.md
```

Expected: ~150 lines.

- [ ] **Step 4: Commit**

```bash
git add asset-planner.md
git commit -m "feat(stage): write asset-planner.md (Stage 4: ASSETS.md sprite manifest)"
```

---

## Task 11: Write `asset-gen.md` (Stage 5)

**Files:**
- Create: `asset-gen.md`

Spec §7.5 is the source. Stage 5 implements `_build_assets()` per ASSETS.md and verifies each sprite with `inspect_sprite` and `inspect_animation`. Carry forward v3 worked example (`player_walk_1` 16x16 hex).

- [ ] **Step 1: Read spec and v3 source**

```bash
sed -n '/^### 7.5 asset-gen/,/^### 7.6 /p' /Users/takashi/repos/pyxel-skill/docs/superpowers/specs/2026-05-01-pyxel-harness-design.md
git show archive/v3-drafts:asset-gen.md > /tmp/v3-asset-gen.md
cat /tmp/v3-asset-gen.md
```

- [ ] **Step 2: Write `asset-gen.md`**

Create `/Users/takashi/repos/pyxel-skill/asset-gen.md` with content covering:

- Stage header + Inputs / Outputs.
- Per-asset loop (1–5 per spec §7.5).
- Sprite identity heuristics mapping to actual `inspect_sprite` / `inspect_animation` fields (color_count, fill_ratio, paired-frame diff).
- Worked example: `player_walk_1` 16x16 hex (port from v3 verbatim).
- Bank organization tip (regions dict).
- End-of-stage verification (`inspect_bank`, `inspect_animation` per pair).
- Anti-patterns (sprites in update(), procedural placeholders, bulk-edit-then-bulk-verify, missing colkey=0).
- When this stage is done.

Target ~180 lines, prose follows the same structure as v3-asset-gen.md but with v5 file references and pyxel-mcp tool field names.

Key heuristic mapping (must be accurate per spec §7.5):

```markdown
- **Color region count:** `inspect_sprite` returns `color_count` as a dict {palette_idx: pixel_count}. Count `len(color_count.keys())` and assert it ≥ ASSETS.md `min distinct color regions`.
- **Bounding-box density:** `inspect_sprite` returns `fill_ratio` (non-transparent pixels / total). Assert 0.15 ≤ `fill_ratio` ≤ 0.95.
- **Frame pair diff:** for paired frames (walk_1 / walk_2), call `inspect_animation` with `frame_count=2` at the pair's bank position. The harness computes per-frame diff automatically; assert `diff_ratio` is 5–50%. Do NOT compute diff yourself by reading raw `pixels` arrays — `inspect_animation` does it.
```

Worked example block (port verbatim from v3 archive):

```python
# Inside _build_assets():
pyxel.images[0].set(0, 0, [
    "0008888880000000",   #     ████
    "0088888888000000",   #    ██████
    "008f44ff44f00000",   #   skin/face with outline & mouth
    "008f4ff4ff4f0000",   #   eye details
    "0008f4444f000000",   #
    "0008cccccccc0000",   #   overalls (12=cyan)
    "008c87887878c000",   #   buttons (8=red dots)
    "008cccccccccc000",   #
    "0088cc8800cc8800",   #   arms swing forward
    "008c08000080cc00",   #
    "0080000000000000",   #
    "00cccc0000cccc00",   #   legs separated (one fwd, one bk)
    "00cccc0000cccc00",   #
    "0044440000444400",   #   shoes (4=brown)
    "0044440000444400",   #
    "0000000000000000",
])
```

(Use the same prose framing as v3 to preserve battle-tested language: "16x16 is enough room for cap, face, eyes, mustache hint, overalls with two buttons, arm in distinguishable position, two separated legs, and shoes. A 'Mario-shaped blob' with one or two colors does not satisfy the contract.")

- [ ] **Step 3: Verify**

```bash
wc -l /Users/takashi/repos/pyxel-skill/asset-gen.md
grep -c 'inspect_sprite\|inspect_animation' /Users/takashi/repos/pyxel-skill/asset-gen.md
```

Expected: ~180 lines; ≥ 4 references to the verify tools.

- [ ] **Step 4: Commit**

```bash
git add asset-gen.md
git commit -m "feat(stage): write asset-gen.md (Stage 5: hex sprite implementation + per-sprite verify)"
```

---

## Task 12: Write `task-execution.md` (Stage 6)

**Files:**
- Create: `task-execution.md`

Spec §7.6 is the source.

- [ ] **Step 1: Read spec and v3 source**

```bash
sed -n '/^### 7.6 task-execution/,/^### 7.7 /p' /Users/takashi/repos/pyxel-skill/docs/superpowers/specs/2026-05-01-pyxel-harness-design.md
git show archive/v3-drafts:task-execution.md > /tmp/v3-task-execution.md
cat /tmp/v3-task-execution.md
```

- [ ] **Step 2: Write `task-execution.md`**

Create `/Users/takashi/repos/pyxel-skill/task-execution.md` (~180 lines) covering:

- Stage header + Inputs / Outputs / References (test-harness, capture, quirks).
- Per-task loop (9 steps per spec §7.6):
  1. Read task definition (PLAN.md), confirm Verify is observable.
  2. Read STRUCTURE.md, identify class/function gaining the change.
  3. Read current source.
  4. Implement smallest change that makes the task observable.
  5. `validate_script` clean.
  6. `run_and_capture` at relevant frame — sanity render.
  7. Run task's specific Verify procedure (likely `play_and_capture` + `inspect_state`).
  8. If FAIL — read state, find divergence, fix. Don't move on.
  9. If PASS — update PLAN.md (mark task done with verified-by note), append MEMORY.md if non-obvious, commit.
- Phases: Risk Slice (per-PLAN-risk implementation, isolation, validate, carry forward only the validated pattern) and Main Build (lock scene ownership, implement vertical slices).
- Visual primacy block (carry from v3): three concrete divergence cases.
- Anti-shortcut rules restated: no "looks fine", don't skip lose-path, don't lower thresholds, no commenting out failing assertions, don't trust subprocess returncode alone.
- Closed-loop input: pattern for paths > 200 frames (call test-harness in segments).
- Per-task implementation checklist (6 items: minimal scope, validate clean, run_and_capture sane, verify predicates met, PLAN.md updated, MEMORY.md updated).
- References to read:
  - `test-harness.md` before running win/lose milestone playthroughs.
  - `capture.md` before producing intermediate captures or final bundle.
  - `quirks.md` whenever Pyxel behaves unexpectedly.
  - `knowledge/game-feel.md` (physics, jumps, hitboxes, camera, screen shake, hitstop).
  - `knowledge/audio.md` (SE per event).
  - `knowledge/patterns.md` (level/enemy archetypes, animation timing).
- Anti-patterns: implementing all tasks before verifying any, skipping risk tasks, editing physics constants mid-task without re-verifying, adding features mid-task.
- When this stage is done: every PLAN.md task marked done with verified-by notes, MEMORY.md has gotchas, proof bundle exists at `screenshots/result/<N>/`. Move to Stage 7.

The exact wording can follow v3 task-execution.md closely; the primary updates are:
- v3 references to "Phase 6" → "Stage 6".
- Add references to `knowledge/*.md` (not in v3).
- Add an explicit Stop hook awareness paragraph: "the Stop hook (`hooks/stop_check_bundle.py`) fires at session end and warns on missing bundle — do not rely on it to enforce; run the gate explicitly."

- [ ] **Step 3: Verify**

```bash
wc -l /Users/takashi/repos/pyxel-skill/task-execution.md
grep -c 'knowledge/' /Users/takashi/repos/pyxel-skill/task-execution.md
```

Expected: ~180 lines; ≥ 3 references to knowledge files.

- [ ] **Step 4: Commit**

```bash
git add task-execution.md
git commit -m "feat(stage): write task-execution.md (Stage 6: gameplay implementation loop)"
```

---

## Task 13: Write `quality-gate.md` (Stage 7)

**Files:**
- Create: `quality-gate.md`

Spec §7.7 is the source. This is the most enforcement-heavy stage.

- [ ] **Step 1: Read spec**

```bash
sed -n '/^### 7.7 quality-gate/,/^## 8\./p' /Users/takashi/repos/pyxel-skill/docs/superpowers/specs/2026-05-01-pyxel-harness-design.md
git show archive/v3-drafts:quality-gate.md > /tmp/v3-quality-gate.md
cat /tmp/v3-quality-gate.md
```

- [ ] **Step 2: Write `quality-gate.md`**

Create `/Users/takashi/repos/pyxel-skill/quality-gate.md` (~150 lines) covering:

- Stage header + Inputs (PLAN.md, STRUCTURE.md, ASSETS.md, MEMORY.md, screenshots/result/<N>/).
- Output: `screenshots/result/<N>/gate-report.json` with structured PASS/FAIL per check.
- Stop conditions (flat list, 12 items per spec §7.7):

  | # | Check | How (concrete pyxel-mcp calls) | FAIL routes to |
  |---|-------|-------------------------------|----------------|
  | 1 | All four state files present | `os.path.exists` for PLAN.md / STRUCTURE.md / ASSETS.md / MEMORY.md, all non-empty | the owning phase |
  | 2 | Script validates | `validate_script main.py` — clean | task-execution |
  | 3 | Smoke run | `run_and_capture main.py --frames=30` non-empty image, no crash | scaffold / task-execution |
  | 4 | Asset identity | per ASSETS.md entry: `inspect_sprite` reports `len(color_count.keys()) ≥ min`, `0.15 ≤ fill_ratio ≤ 0.95`. Paired frames: `inspect_animation frame_count=2` reports per-frame diff in 5–50%. The harness computes diff automatically — no caller-side math. | asset-gen |
  | 5 | Win path | `play_and_capture` with PLAN.md win-path inputs reaches `scene == "WIN"` by final-milestone frame | task-execution or PLAN.md |
  | 6 | Lose path | `play_and_capture` with PLAN.md lose-path inputs (typically `KEY_SPACE` once at frame 30, then no input) reaches `scene == "GAME_OVER"` by final-milestone frame | task-execution or PLAN.md |
  | 7 | Audio renders | per audio manifest entry: `render_audio` returns non-empty notes, peak > minimum threshold | asset-gen / scaffold |
  | 8 | Palette hierarchy | `inspect_palette` reports `Hierarchy score: 2/2` | asset-planner / asset-gen |
  | 9 | Contrast | `inspect_palette` low-contrast warnings ≤ 1 | asset-planner / asset-gen |
  | 10 | Difficulty floor | Lose path triggers GAME_OVER within 10–14 seconds at the configured fps (≈ 300–420 frames at 30fps; ≈ 600–840 frames at 60fps). Compute the frame window at run time from STRUCTURE.md `FPS` constant. | task-execution / decomposer |
  | 11 | Layout balance | `inspect_layout` reports H-balance ≥ 70% on **TITLE** scene (TITLE has text and produces a stable balance metric). For text-less PLAY scenes, run `inspect_screen` on a representative frame and assert no quadrant is empty. | scaffold |
  | 12 | Proof bundle | `screenshots/result/<N>/` exists with win-path.gif, lose-path.gif, frames/, audio/ — see `capture.md` | capture (in task-execution) |

- gate-report.json schema (one row per check):

  ```json
  {
    "attempt": 1,
    "fps": 30,
    "checks": [
      {"id": 1, "label": "State files", "result": "PASS", "evidence": "all 4 files present"},
      {"id": 2, "label": "Validate", "result": "PASS"},
      ...
      {"id": 5, "label": "Win path", "result": "FAIL", "evidence": "scene at frame 660 = PLAY (expected WIN)", "fail_route": "task-execution"}
    ],
    "summary": {"pass": 11, "fail": 1, "total": 12}
  }
  ```

- Anti-shortcut rules restated for the agent at gate time (5 items — see spec §7.7).
- "What happens on FAIL": route to the phase named in the check's `fail_route`. Do not retry the gate without remediation.
- "When this gate PASSes": report bundle path to user, stop. Done.

- [ ] **Step 3: Verify**

```bash
wc -l /Users/takashi/repos/pyxel-skill/quality-gate.md
grep -c '^| [0-9]' /Users/takashi/repos/pyxel-skill/quality-gate.md
```

Expected: ~150 lines; 12 numbered table rows.

- [ ] **Step 4: Commit**

```bash
git add quality-gate.md
git commit -m "feat(stage): write quality-gate.md (Stage 7: 12 stop conditions + gate-report.json schema)"
```

---

## Task 14: Write `quirks.md` reference

**Files:**
- Create: `quirks.md`

Spec §8.1 is the source. Carry from v3 with godogen size discipline ("Keep this file small and high-signal").

- [ ] **Step 1: Read spec and v3 source**

```bash
sed -n '/^### 8.1 quirks/,/^### 8.2 /p' /Users/takashi/repos/pyxel-skill/docs/superpowers/specs/2026-05-01-pyxel-harness-design.md
git show archive/v3-drafts:quirks.md > /tmp/v3-quirks.md
cat /tmp/v3-quirks.md
wc -l /tmp/v3-quirks.md
```

- [ ] **Step 2: Write `quirks.md`**

Create `/Users/takashi/repos/pyxel-skill/quirks.md`. Open with the size discipline note (verbatim from spec §8.1):

```markdown
# Pyxel Quirks

Keep this file small and high-signal. Each item below has bitten real implementations and shows up as ambiguous bugs.

**Inclusion rule.** Add only repeated, non-obvious issues that would have prevented real confusion in `scaffold`, `asset-gen`, `task-execution`, `capture`, or any `knowledge/` file. If an item is already in `pyxel-mcp`'s `instructions.md` Error Recovery section, it does not belong here. If it is answerable by `pyxel://api-reference`, it does not belong here.
```

Then carry the curated v3 list. **Prune duplicates with pyxel-mcp instructions.md.** The v3 quirks.md has 17 items; spec §8.1 lists ~16 expected items. Read `/Users/takashi/repos/pyxel-mcp/src/pyxel_mcp/instructions.md` and remove any v3 quirk that is already covered there (Essential Tips, Error Recovery, Tilemap Gotchas).

Items to keep (per spec §8.1):
- Coordinates (0, 0) top-left, Y-down; `pyxel.cls` first in draw; draw order is paint order.
- `blt` without `colkey` makes transparent color opaque; negative `w`/`h` flips.
- `pyxel.sin/cos` take degrees, not radians.
- `btnp` vs `btn` semantics; headless mode uses `set_btn` / `set_btnv`.
- Image bank: `set` before `pyxel.run`; bank is 256x256; layout in ASSETS.md.
- Tilemap (0, 0) trap.
- 4 audio channels; BGM ch0–2, SE ch3; SE volume 5–7; noise tone too quiet over BGM.
- `pyxel.gen_bgm` first 4 args required (Pyxel 2.9+).
- MML volumes `V0`–`V100` vs `set()` API `0`–`7`.
- Headless `SDL_AUDIODRIVER=dummy`.
- Animation: `frame_count // 4 % 2`, not `frame_count % 2`.
- `inspect_state` does not auto-expand deep nesting; flatten state to top-level App attrs.
- `pyxel.quit()` requests exit but does not force-exit since 2.8 — `while True:` inside `update()` hangs.
- (Add 2-3 more only if they are genuinely non-obvious and not covered in instructions.md.)

Each entry is one short paragraph (3-5 lines). Total target: ~80 lines.

Close with a Feedback Loop section (verbatim from godogen `bevy/skills/godogen/quirks.md`):

```markdown
## Feedback Loop

Quirks are curated manually in this skill. Add only repeated, non-obvious issues that would have prevented real confusion in a stage file (`scaffold`, `asset-gen`, `task-execution`, `capture`) or in a knowledge file. Remove items that have stopped biting after engine or skill changes.
```

- [ ] **Step 3: Verify**

```bash
wc -l /Users/takashi/repos/pyxel-skill/quirks.md
grep -c '^## \|^- ' /Users/takashi/repos/pyxel-skill/quirks.md
```

Expected: ~80 lines; ≤ 16 bullet items (size discipline check).

- [ ] **Step 4: Commit**

```bash
git add quirks.md
git commit -m "feat(ref): write quirks.md (curated Pyxel gotchas with godogen size discipline)"
```

---

## Task 15: Write `test-harness.md` reference

**Files:**
- Create: `test-harness.md`

Spec §8.2 is the source. Called from task-execution Stage 6.

- [ ] **Step 1: Read spec and v3 source**

```bash
sed -n '/^### 8.2 test-harness/,/^### 8.3 /p' /Users/takashi/repos/pyxel-skill/docs/superpowers/specs/2026-05-01-pyxel-harness-design.md
git show archive/v3-drafts:test-harness.md > /tmp/v3-test-harness.md
cat /tmp/v3-test-harness.md
```

- [ ] **Step 2: Write `test-harness.md`**

Create `/Users/takashi/repos/pyxel-skill/test-harness.md` (~120 lines), structure follows v3 with simplification:

- Header: "Reference: Milestone Playthrough Verification". Called from task-execution and quality-gate.
- Win-path execution: build input schedule from PLAN.md table; `play_and_capture` with milestone frames; `inspect_state` per milestone; aggregate per-milestone PASS/FAIL.
- Lose-path execution: empty inputs (or just KEY_SPACE at frame 30 to enter PLAY); observe state; assert lives decrement and final scene == GAME_OVER.
- Stall and crash monitoring: state hash unchanged across 60 consecutive frames despite scheduled inputs → FAIL with "no progress between frame X and frame Y; expected motion in attribute Z". Exception trace → FAIL with "script crashed at frame N".
- Closed-loop steering for paths > 200 frames: at each milestone, read observed state, compute next input segment.
- Test fixture considerations: `pyxel.btnp/btn` flow naturally with `set_btn`. Seed RNG with `pyxel.rseed(42)` for repeatability if random spawns are involved.

Anti-patterns + when-this-is-done sections per v3.

- [ ] **Step 3: Verify**

```bash
wc -l /Users/takashi/repos/pyxel-skill/test-harness.md
```

Expected: ~120 lines.

- [ ] **Step 4: Commit**

```bash
git add test-harness.md
git commit -m "feat(ref): write test-harness.md (milestone playthrough — called from Stage 6)"
```

---

## Task 16: Write `capture.md` reference

**Files:**
- Create: `capture.md`

Spec §8.3 is the source.

- [ ] **Step 1: Read spec and v3 source**

```bash
sed -n '/^### 8.3 capture/,/^## 9\./p' /Users/takashi/repos/pyxel-skill/docs/superpowers/specs/2026-05-01-pyxel-harness-design.md
git show archive/v3-drafts:capture.md > /tmp/v3-capture.md
cat /tmp/v3-capture.md
```

- [ ] **Step 2: Write `capture.md`**

Create `/Users/takashi/repos/pyxel-skill/capture.md` (~120 lines):

- Header: "Reference: Proof Bundle Production". Called from task-execution (intermediate captures) and quality-gate (final bundle).
- Bundle structure: `screenshots/result/<N>/` with win-path.gif, lose-path.gif, frames/, audio/, notes.md.
- Per-bundle file requirements:
  - **Win-path GIF:** ≥ 600 frames at 30 fps (~20 seconds); shows traversal start to goal; ends on WIN. Bundle whose first 5 seconds look right then static for 20 is FAIL.
  - **Lose-path GIF:** ≥ 360 frames; shows hazard hitting player and lives decrementing; ends on GAME_OVER.
  - **Frame snapshots:** title.png, play_start.png, mid_game.png, win.png, game_over.png — capture at scene transitions.
  - **Audio renders:** one .wav per audio manifest entry (BGM ch0/1/2, SE jump/climb/death/win/etc).
  - **notes.md:** brief summary with timestamp, bundle attempt number, win/lose path duration, audio summary.
- Concrete invocation patterns:
  ```bash
  record_gameplay main.py --inputs '<win-path inputs from PLAN.md>' --duration 720 --scale 2 \
    > screenshots/result/1/win-path.gif
  record_gameplay main.py --inputs '[{"frame":30,"keys":["KEY_SPACE"]},{"frame":32,"keys":[]}]' \
    --duration 480 --scale 2 \
    > screenshots/result/1/lose-path.gif
  capture_frames main.py --frames="30,90,180,360,720" --scale=2
  render_audio main.py --sound_index=10 --output_wav_path=screenshots/result/1/audio/se_jump.wav
  ```
- Anti-patterns: bundle < 60 frames, skipping audio, frames without GIF, reusing stale bundle, middle 80% same frame (use `compare_frames` to verify motion).
- When this is done: bundle directory exists with all required artifacts; counter `<N>` is the next integer above the previous bundle.

- [ ] **Step 3: Verify**

```bash
wc -l /Users/takashi/repos/pyxel-skill/capture.md
```

Expected: ~120 lines.

- [ ] **Step 4: Commit**

```bash
git add capture.md
git commit -m "feat(ref): write capture.md (proof bundle production)"
```

---

## Knowledge migration coordination (Tasks 17-21)

The five knowledge files migrate content from `pyxel-mcp/src/pyxel_mcp/instructions.md`. The coordinated `pyxel-mcp 0.9.3 trim` plan (sibling: `2026-05-01-pyxel-mcp-0.9.3-trim-implementation.md`) deletes those sections from the live file once it runs. To make Tasks 17-21 robust against execution ordering, **always extract from the `pre-v0.9.3-trim` git tag** that the pyxel-mcp plan creates as its first task.

If you are running these tasks before the pyxel-mcp plan has executed, the tag does not yet exist. In that case, fall back to the live file. The shell snippet at the start of each task handles both cases:

```bash
# Resolve the source: prefer the pre-trim tag (canonical, immutable), fall back to live file.
SRC=/tmp/pyxel-mcp-instructions-pretrim.md
git -C /Users/takashi/repos/pyxel-mcp show pre-v0.9.3-trim:src/pyxel_mcp/instructions.md > "$SRC" 2>/dev/null \
  || cp /Users/takashi/repos/pyxel-mcp/src/pyxel_mcp/instructions.md "$SRC"
ls -la "$SRC"
```

Each task below uses `$SRC` as the source path for `awk` extraction. **Always run the resolver block first in the same shell** before the extraction commands.

---

## Task 17: Migrate `knowledge/pixel-art.md`

**Files:**
- Create: `knowledge/pixel-art.md`

Source: pyxel-mcp `instructions.md` sections per spec §10.1 (Color Palette & Hierarchy + Pixel Art Rules subsections), via `pre-v0.9.3-trim` tag — see "Knowledge migration coordination" block above.

- [ ] **Step 1: Extract source content (use the resolver from the coordination block above)**

```bash
SRC=/tmp/pyxel-mcp-instructions-pretrim.md
git -C /Users/takashi/repos/pyxel-mcp show pre-v0.9.3-trim:src/pyxel_mcp/instructions.md > "$SRC" 2>/dev/null \
  || cp /Users/takashi/repos/pyxel-mcp/src/pyxel_mcp/instructions.md "$SRC"

awk '/^## Color Palette & Hierarchy/,/^## Background Design/' "$SRC" > /tmp/k-pixel-art.md
sed -i '' '$ d' /tmp/k-pixel-art.md  # drop the trailing "## Background Design" line
cat /tmp/k-pixel-art.md
```

- [ ] **Step 2: Compose `knowledge/pixel-art.md`**

Create `/Users/takashi/repos/pyxel-skill/knowledge/pixel-art.md`. Structure:

```markdown
# Knowledge: Pixel Art

Used by Stage 4 (asset-planner), Stage 5 (asset-gen), and Stage 7 (quality-gate threshold reference).

## 16-color default palette

(content from instructions.md "## Color Palette & Hierarchy" section)

## 3-Layer Color Hierarchy

(content from instructions.md "### 3-Layer Color Hierarchy")

The quality gate (#8) requires `inspect_palette` to report `Hierarchy score: 2/2`. The hierarchy layers are:
1. Background (dark): 0, 1, 5
2. Environment (mid): 3, 4, 13
3. Interactive (bright): 8, 10, 11

Score 2/2 means all three layers are represented. Score 1/2 = two layers; score 0/2 = one layer (uniform tone).

## Pixel Art Rules

(content from instructions.md "## Pixel Art Rules" + all 6 subsections: 3-Color-Per-Material Rule, Outline Strategy, Sprite Size Guidelines, Anti-Patterns, Sprite Design Process, Sprite Sheet Organization)

## Reference

- Pyxel default palette URI: `pyxel://palette/default` (MCP resource).
- For animated sprite frame counts, see `knowledge/patterns.md` "Animation Timing".
```

Each "(content from instructions.md ...)" block is a verbatim copy from the source. Cross-link adjustments:
- Replace any `inspect_sprite` / `inspect_palette` mentions with the correct field names per the spec (color_count, fill_ratio, Hierarchy score) — use the field-name table in spec §7.5 / §7.7 #4 / §7.7 #8.
- Add forward references to the quality gate's checks #4, #8, #9 where the rules are enforced.

Target ~150 lines.

- [ ] **Step 3: Verify**

```bash
wc -l /Users/takashi/repos/pyxel-skill/knowledge/pixel-art.md
grep -c '^## ' /Users/takashi/repos/pyxel-skill/knowledge/pixel-art.md
```

Expected: ~150 lines; 4 H2 sections.

- [ ] **Step 4: Commit**

```bash
git rm knowledge/.gitkeep
git add knowledge/pixel-art.md
git commit -m "feat(knowledge): migrate pixel-art knowledge from pyxel-mcp instructions.md"
```

---

## Task 18: Migrate `knowledge/background.md`

**Files:**
- Create: `knowledge/background.md`

Source: pyxel-mcp `instructions.md` sections "## Background Design" (with subsections Genre Background Recipes, Parallax Scrolling) + "## Screen & Text Layout" (with Text Positioning).

- [ ] **Step 1: Extract source content (use the resolver from the coordination block above Task 17)**

```bash
SRC=/tmp/pyxel-mcp-instructions-pretrim.md
git -C /Users/takashi/repos/pyxel-mcp show pre-v0.9.3-trim:src/pyxel_mcp/instructions.md > "$SRC" 2>/dev/null \
  || cp /Users/takashi/repos/pyxel-mcp/src/pyxel_mcp/instructions.md "$SRC"

awk '/^## Background Design/,/^## Title Screen Design/' "$SRC" > /tmp/k-background-1.md
sed -i '' '$ d' /tmp/k-background-1.md
awk '/^## Screen & Text Layout/,/^## Title Screen Design/' "$SRC" > /tmp/k-background-2.md
sed -i '' '$ d' /tmp/k-background-2.md
cat /tmp/k-background-1.md
cat /tmp/k-background-2.md
```

- [ ] **Step 2: Compose `knowledge/background.md`**

Create `/Users/takashi/repos/pyxel-skill/knowledge/background.md`:

```markdown
# Knowledge: Background and Layout

Used by Stage 1 (visual-target — screen size derivation), Stage 3 (scaffold — text layout), and Stage 7 (quality-gate threshold reference for layout balance).

## Background Design

(content from instructions.md "## Background Design", including subsections "### Genre Background Recipes" and "### Parallax Scrolling")

## Screen and Text Layout

(content from instructions.md "## Screen & Text Layout" + "### Text Positioning")

## Quality gate connection

The quality gate (#11) requires `inspect_layout` to report H-balance ≥ 70% on the TITLE scene. For TITLE scenes that lack text (logo-only), the gate falls back to `inspect_screen` on a representative frame and asserts no quadrant is empty.

## Reference

- For title-screen-specific composition, see `knowledge/patterns.md` "Title Screen Design".
```

Target ~120 lines.

- [ ] **Step 3: Verify**

```bash
wc -l /Users/takashi/repos/pyxel-skill/knowledge/background.md
```

Expected: ~120 lines.

- [ ] **Step 4: Commit**

```bash
git add knowledge/background.md
git commit -m "feat(knowledge): migrate background + screen-layout knowledge from pyxel-mcp instructions.md"
```

---

## Task 19: Migrate `knowledge/game-feel.md`

**Files:**
- Create: `knowledge/game-feel.md`

Source: pyxel-mcp `instructions.md` "## Visual Feedback" (+ Screen Shake + Hitstop subsections) + "## Game Feel Constants" (+ Platformer Physics + Variable Jump Height + Forgiveness Mechanics + Hitbox Design + Camera).

- [ ] **Step 1: Extract source content (use the resolver from the coordination block above Task 17)**

```bash
SRC=/tmp/pyxel-mcp-instructions-pretrim.md
git -C /Users/takashi/repos/pyxel-mcp show pre-v0.9.3-trim:src/pyxel_mcp/instructions.md > "$SRC" 2>/dev/null \
  || cp /Users/takashi/repos/pyxel-mcp/src/pyxel_mcp/instructions.md "$SRC"

awk '/^## Visual Feedback/,/^## Sound Effects Cookbook/' "$SRC" > /tmp/k-feel-1.md
awk '/^## Game Feel Constants/,/^## Animation Timing/' "$SRC" > /tmp/k-feel-2.md
sed -i '' '$ d' /tmp/k-feel-1.md
sed -i '' '$ d' /tmp/k-feel-2.md
```

- [ ] **Step 2: Compose `knowledge/game-feel.md`**

Create `/Users/takashi/repos/pyxel-skill/knowledge/game-feel.md`:

```markdown
# Knowledge: Game Feel

Used by Stage 6 (task-execution).

## Visual Feedback

(content from instructions.md "## Visual Feedback")

### Screen Shake

(content from instructions.md "### Screen Shake")

### Hitstop (Freeze Frames)

(content from instructions.md "### Hitstop (Freeze Frames)")

## Game Feel Constants

(content from instructions.md "## Game Feel Constants" + all 5 subsections: Platformer Physics, Variable Jump Height, Forgiveness Mechanics, Hitbox Design, Camera)

## Reference

- Animation timing is in `knowledge/patterns.md` "Animation Timing".
- Audio feedback (SE per event) is in `knowledge/audio.md` "Sound Effects Cookbook".
```

Target ~200 lines.

- [ ] **Step 3: Verify**

```bash
wc -l /Users/takashi/repos/pyxel-skill/knowledge/game-feel.md
```

Expected: ~200 lines.

- [ ] **Step 4: Commit**

```bash
git add knowledge/game-feel.md
git commit -m "feat(knowledge): migrate game-feel + visual-feedback knowledge from pyxel-mcp instructions.md"
```

---

## Task 20: Migrate `knowledge/audio.md`

**Files:**
- Create: `knowledge/audio.md`

Source: pyxel-mcp `instructions.md` sections "### MML Composition Guide" + "### Quick BGM" + "## Sound Effects Cookbook" (+ Jump / Coin / Hit / Game Over) + the design portion of "### Audio Channel Management" (BGM/SE allocation rationale).

- [ ] **Step 1: Extract source content (use the resolver from the coordination block above Task 17)**

```bash
SRC=/tmp/pyxel-mcp-instructions-pretrim.md
git -C /Users/takashi/repos/pyxel-mcp show pre-v0.9.3-trim:src/pyxel_mcp/instructions.md > "$SRC" 2>/dev/null \
  || cp /Users/takashi/repos/pyxel-mcp/src/pyxel_mcp/instructions.md "$SRC"

awk '/^### MML Composition Guide/,/^## Color Palette/' "$SRC" > /tmp/k-audio-1.md
awk '/^## Sound Effects Cookbook/,/^## Game Patterns/' "$SRC" > /tmp/k-audio-2.md
sed -i '' '$ d' /tmp/k-audio-1.md
sed -i '' '$ d' /tmp/k-audio-2.md
```

- [ ] **Step 2: Compose `knowledge/audio.md`**

Create `/Users/takashi/repos/pyxel-skill/knowledge/audio.md`:

```markdown
# Knowledge: Audio

Used by Stage 3 (scaffold — channel allocation) and Stage 6 (task-execution — SE definitions per event).

## Channel allocation

Pyxel has 4 audio channels (0–3). Convention:
- BGM on ch0–ch2 (3-channel composition).
- SE on ch3 only.

`play(N, ...)` on the BGM melody channel interrupts BGM. `playm(0)` assigns music tracks to channels starting from ch0. SE volume must be 5–7 (out of 7) to cut through BGM.

Tone discipline:
- Square (`s`) and pulse (`p`) tones for melodic SE.
- Noise (`n`) is too quiet over BGM for melodic SE; reserve for percussion or hits.

## MML Composition Guide

(content from instructions.md "### MML Composition Guide", including the 3-channel template and Genre moods table)

## Quick BGM via gen_bgm

(content from instructions.md "### Quick BGM")

## Sound Effects Cookbook

(content from instructions.md "## Sound Effects Cookbook" + all 4 subsections: Jump, Coin / Collect, Hit / Damage, Game Over)
```

Target ~180 lines.

- [ ] **Step 3: Verify**

```bash
wc -l /Users/takashi/repos/pyxel-skill/knowledge/audio.md
```

Expected: ~180 lines.

- [ ] **Step 4: Commit**

```bash
git add knowledge/audio.md
git commit -m "feat(knowledge): migrate audio knowledge from pyxel-mcp instructions.md (MML, SE cookbook, channel discipline)"
```

---

## Task 21: Migrate `knowledge/patterns.md`

**Files:**
- Create: `knowledge/patterns.md`

Source: instructions.md "## Title Screen Design" + "## Game Patterns" (Platformer / Shooter / Scene Management) + "### Level Design" + "### Enemy Design" + "## Animation Timing" (+ State-Based Animator).

- [ ] **Step 1: Extract source content (use the resolver from the coordination block above Task 17)**

```bash
SRC=/tmp/pyxel-mcp-instructions-pretrim.md
git -C /Users/takashi/repos/pyxel-mcp show pre-v0.9.3-trim:src/pyxel_mcp/instructions.md > "$SRC" 2>/dev/null \
  || cp /Users/takashi/repos/pyxel-mcp/src/pyxel_mcp/instructions.md "$SRC"

awk '/^## Title Screen Design/,/^## Visual Feedback/' "$SRC" > /tmp/k-patterns-1.md
awk '/^## Game Patterns/,/^## Game Feel Constants/' "$SRC" > /tmp/k-patterns-2.md
awk '/^## Animation Timing/,/^## Quality Checklist/' "$SRC" > /tmp/k-patterns-3.md
sed -i '' '$ d' /tmp/k-patterns-1.md
sed -i '' '$ d' /tmp/k-patterns-2.md
sed -i '' '$ d' /tmp/k-patterns-3.md
```

- [ ] **Step 2: Compose `knowledge/patterns.md`**

Create `/Users/takashi/repos/pyxel-skill/knowledge/patterns.md`:

```markdown
# Knowledge: Patterns

Used by Stage 3 (scaffold — scene state machine, title-screen recipe) and Stage 6 (task-execution — level/enemy archetypes, animation timing).

## Title Screen Design

(content from /tmp/k-patterns-1.md)

## Game Patterns

(content from /tmp/k-patterns-2.md, including Platformer, Shooter, Scene Management)

### Level Design

(content from instructions.md "### Level Design")

### Enemy Design

(content from instructions.md "### Enemy Design")

## Animation Timing

(content from /tmp/k-patterns-3.md, including the Animation Timing table and State-Based Animator example)
```

Target ~250 lines.

- [ ] **Step 3: Verify**

```bash
wc -l /Users/takashi/repos/pyxel-skill/knowledge/patterns.md
```

Expected: ~250 lines.

- [ ] **Step 4: Commit**

```bash
git add knowledge/patterns.md
git commit -m "feat(knowledge): migrate patterns knowledge from pyxel-mcp instructions.md (title screen, scene SM, level/enemy, animation)"
```

---

## Task 22: Write `hooks/stop_check_bundle.py` (TDD)

**Files:**
- Create: `hooks/stop_check_bundle.py`
- Create: `hooks/test_stop_check_bundle.py`

The Stop hook is a Python script. It reads stdin (Claude Code Stop hook event format), checks for bundle integrity, prints a JSON response to stdout. **Never blocks** — always returns `{}` to allow stop. Writes warnings to stderr.

Modeled on godogen's `shared/hooks/stop_post_task_gate.py` (Telegram push) but with bundle-check semantics instead of push.

- [ ] **Step 1: Read godogen's hook for reference shape**

```bash
cat /tmp/godogen/shared/hooks/stop_post_task_gate.py
```

- [ ] **Step 2: Write the failing test**

Create `/Users/takashi/repos/pyxel-skill/hooks/test_stop_check_bundle.py`:

```python
"""Tests for hooks/stop_check_bundle.py — pyxel-skill Stop hook."""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

HOOK = Path(__file__).parent / "stop_check_bundle.py"


def run_hook(event: dict, cwd: Path) -> tuple[str, str, int]:
    """Run the hook as a subprocess with given event on stdin and cwd."""
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(event),
        capture_output=True,
        text=True,
        cwd=str(cwd),
    )
    return proc.stdout, proc.stderr, proc.returncode


def test_no_op_when_not_a_pyxel_skill_project(tmp_path: Path) -> None:
    """Hook silently returns {} when .pyxel-skill/ marker is absent."""
    out, err, rc = run_hook({"cwd": str(tmp_path)}, tmp_path)
    assert rc == 0
    assert json.loads(out) == {}
    assert err == ""


def test_warns_when_marker_present_but_no_bundle(tmp_path: Path) -> None:
    """Hook prints a warning when .pyxel-skill/ exists but no screenshots/result/."""
    (tmp_path / ".pyxel-skill").mkdir()
    out, err, rc = run_hook({"cwd": str(tmp_path)}, tmp_path)
    assert rc == 0
    assert json.loads(out) == {}
    assert "no proof bundle" in err.lower()


def test_warns_when_bundle_lacks_video(tmp_path: Path) -> None:
    """Hook warns if latest screenshots/result/<N>/ has no win-path.gif."""
    (tmp_path / ".pyxel-skill").mkdir()
    bundle = tmp_path / "screenshots" / "result" / "1"
    bundle.mkdir(parents=True)
    out, err, rc = run_hook({"cwd": str(tmp_path)}, tmp_path)
    assert rc == 0
    assert json.loads(out) == {}
    assert "win-path" in err.lower() or "incomplete" in err.lower()


def test_warns_when_gate_report_has_failures(tmp_path: Path) -> None:
    """Hook warns if gate-report.json shows unaddressed FAILs."""
    (tmp_path / ".pyxel-skill").mkdir()
    bundle = tmp_path / "screenshots" / "result" / "1"
    bundle.mkdir(parents=True)
    (bundle / "win-path.gif").write_bytes(b"GIF89a")
    (bundle / "gate-report.json").write_text(json.dumps({
        "attempt": 1,
        "fps": 30,
        "checks": [{"id": 5, "label": "Win path", "result": "FAIL", "evidence": "x"}],
        "summary": {"pass": 11, "fail": 1, "total": 12},
    }))
    out, err, rc = run_hook({"cwd": str(tmp_path)}, tmp_path)
    assert rc == 0
    assert json.loads(out) == {}
    assert "fail" in err.lower()


def test_silent_pass_on_clean_bundle(tmp_path: Path) -> None:
    """Hook silently returns {} when bundle is well-formed and gate report is all-PASS."""
    (tmp_path / ".pyxel-skill").mkdir()
    bundle = tmp_path / "screenshots" / "result" / "1"
    bundle.mkdir(parents=True)
    (bundle / "win-path.gif").write_bytes(b"GIF89a")
    (bundle / "lose-path.gif").write_bytes(b"GIF89a")
    (bundle / "gate-report.json").write_text(json.dumps({
        "attempt": 1,
        "fps": 30,
        "checks": [{"id": i, "label": f"check {i}", "result": "PASS"} for i in range(1, 13)],
        "summary": {"pass": 12, "fail": 0, "total": 12},
    }))
    out, err, rc = run_hook({"cwd": str(tmp_path)}, tmp_path)
    assert rc == 0
    assert json.loads(out) == {}
    # Some informational messages OK on stderr; no warnings/errors.
    assert "warn" not in err.lower()
    assert "fail" not in err.lower()


def test_never_blocks_on_unexpected_input(tmp_path: Path) -> None:
    """Hook returns {} (non-blocking) even on malformed input."""
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input="not valid json",
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )
    assert proc.returncode == 0
    # Either {} or some error JSON, but rc must be 0 to avoid blocking stop.
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd /Users/takashi/repos/pyxel-skill
python -m pytest hooks/test_stop_check_bundle.py -v
```

Expected: 6 tests, all FAIL with "FileNotFoundError" or similar (the hook script does not exist yet).

- [ ] **Step 4: Implement `hooks/stop_check_bundle.py`**

Create `/Users/takashi/repos/pyxel-skill/hooks/stop_check_bundle.py`:

```python
#!/usr/bin/env python3
"""pyxel-skill Stop hook: warn (don't block) on missing/incomplete proof bundle.

Best-effort. The hook never blocks Claude Code from stopping. It silently no-ops
when the cwd is not a pyxel-skill project (no .pyxel-skill/ marker).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def repo_root_from(cwd_str: str) -> Path:
    """Return the cwd as a Path. Caller already passes a usable directory."""
    return Path(cwd_str).resolve()


def is_pyxel_skill_project(root: Path) -> bool:
    return (root / ".pyxel-skill").is_dir()


def latest_bundle(root: Path) -> Path | None:
    results = root / "screenshots" / "result"
    if not results.is_dir():
        return None
    numbered: list[tuple[int, Path]] = []
    for child in results.iterdir():
        if not child.is_dir():
            continue
        try:
            numbered.append((int(child.name), child))
        except ValueError:
            continue
    if not numbered:
        return None
    numbered.sort(key=lambda pair: pair[0])
    return numbered[-1][1]


def warn(msg: str) -> None:
    print(f"[pyxel-skill] WARN: {msg}", file=sys.stderr)


def main() -> None:
    # Always print {} on stdout to be non-blocking. Even if input is malformed.
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        print(json.dumps({}))
        return

    cwd = event.get("cwd", ".")
    root = repo_root_from(cwd)

    if not is_pyxel_skill_project(root):
        # Not a pyxel-skill project; silent no-op.
        print(json.dumps({}))
        return

    bundle = latest_bundle(root)
    if bundle is None:
        warn("no proof bundle found at screenshots/result/<N>/. The quality gate may have been skipped.")
        print(json.dumps({}))
        return

    win_gif = bundle / "win-path.gif"
    if not win_gif.is_file():
        warn(f"bundle {bundle.name} is incomplete: missing win-path.gif.")

    gate_report = bundle / "gate-report.json"
    if gate_report.is_file():
        try:
            data = json.loads(gate_report.read_text())
            fail_count = data.get("summary", {}).get("fail", 0)
            if fail_count > 0:
                failed_checks = [c for c in data.get("checks", []) if c.get("result") == "FAIL"]
                ids = ", ".join(str(c.get("id")) for c in failed_checks)
                warn(f"gate report shows {fail_count} unaddressed FAIL(s) (check IDs: {ids}).")
        except (json.JSONDecodeError, ValueError):
            warn(f"gate-report.json in {bundle.name} is not valid JSON.")

    print(json.dumps({}))


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Make the script executable**

```bash
chmod +x /Users/takashi/repos/pyxel-skill/hooks/stop_check_bundle.py
```

- [ ] **Step 6: Run tests to verify all pass**

```bash
cd /Users/takashi/repos/pyxel-skill
python -m pytest hooks/test_stop_check_bundle.py -v
```

Expected: 6 PASS.

- [ ] **Step 7: Commit**

```bash
git add hooks/stop_check_bundle.py hooks/test_stop_check_bundle.py
git rm hooks/.gitkeep
git commit -m "feat(hook): add stop_check_bundle.py with non-blocking bundle integrity check"
```

---

## Task 23: Write `hooks/install.sh`

**Files:**
- Create: `hooks/install.sh`

Idempotent installer that adds the Stop hook to `~/.claude/settings.json`.

- [ ] **Step 1: Inspect current settings.json schema**

```bash
cat ~/.claude/settings.json 2>&1 | head -30
```

The hook entry shape under `hooks.Stop` is a list of objects with `command` (script path). The installer must:
- Read existing `~/.claude/settings.json`.
- If the key `hooks.Stop` does not exist, create it.
- If a hook with `command` matching the absolute path of `stop_check_bundle.py` already exists, no-op (idempotent).
- Otherwise append the new hook.
- Print a one-line summary of action taken.

- [ ] **Step 2: Write `hooks/install.sh`**

Create `/Users/takashi/repos/pyxel-skill/hooks/install.sh`:

```bash
#!/usr/bin/env bash
# pyxel-skill Stop hook installer.
#
# Idempotent: appends an entry to ~/.claude/settings.json's hooks.Stop list
# referencing the absolute path of stop_check_bundle.py. Skips if the entry
# already exists.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_PATH="$SCRIPT_DIR/stop_check_bundle.py"
SETTINGS="${CLAUDE_SETTINGS:-$HOME/.claude/settings.json}"

if [[ ! -f "$HOOK_PATH" ]]; then
    echo "ERROR: hook script not found at $HOOK_PATH" >&2
    exit 1
fi

if [[ ! -x "$HOOK_PATH" ]]; then
    chmod +x "$HOOK_PATH"
fi

# Ensure settings.json exists with at least an empty object.
mkdir -p "$(dirname "$SETTINGS")"
if [[ ! -f "$SETTINGS" ]]; then
    echo '{}' > "$SETTINGS"
fi

# Use jq for safe JSON edits. Fail gracefully if jq is missing.
if ! command -v jq >/dev/null 2>&1; then
    echo "ERROR: jq is required. Install with: brew install jq  (or apt install jq)" >&2
    exit 1
fi

# Check whether our hook is already installed.
ALREADY_INSTALLED=$(jq -r --arg path "$HOOK_PATH" \
    '(.hooks // {}) | (.Stop // []) | map(select(.command == $path)) | length' \
    "$SETTINGS")

if [[ "$ALREADY_INSTALLED" -gt 0 ]]; then
    echo "[pyxel-skill] hook already installed at: $HOOK_PATH"
    exit 0
fi

# Append the new hook entry.
TMP="$(mktemp)"
jq --arg path "$HOOK_PATH" \
    '.hooks //= {} | .hooks.Stop //= [] | .hooks.Stop += [{"command": $path}]' \
    "$SETTINGS" > "$TMP"
mv "$TMP" "$SETTINGS"

echo "[pyxel-skill] installed Stop hook: $HOOK_PATH"
echo "[pyxel-skill] to disable, edit $SETTINGS and remove the entry."
```

- [ ] **Step 3: Make executable and run a smoke test**

```bash
chmod +x /Users/takashi/repos/pyxel-skill/hooks/install.sh
# Smoke test in a sandbox so we don't pollute the user's real settings.
SANDBOX="$(mktemp -d)"
echo '{}' > "$SANDBOX/settings.json"
CLAUDE_SETTINGS="$SANDBOX/settings.json" /Users/takashi/repos/pyxel-skill/hooks/install.sh
cat "$SANDBOX/settings.json"
# Run twice to verify idempotency.
CLAUDE_SETTINGS="$SANDBOX/settings.json" /Users/takashi/repos/pyxel-skill/hooks/install.sh
cat "$SANDBOX/settings.json"
rm -rf "$SANDBOX"
```

Expected: first run installs, second run reports "already installed", final settings.json has exactly one Stop hook entry.

- [ ] **Step 4: Commit**

```bash
git add hooks/install.sh
git commit -m "feat(hook): add idempotent install.sh for Stop hook (uses jq, sandboxed via CLAUDE_SETTINGS)"
```

---

## Task 24: Write `hooks/README.md`

**Files:**
- Create: `hooks/README.md`

- [ ] **Step 1: Write `hooks/README.md`**

Create `/Users/takashi/repos/pyxel-skill/hooks/README.md`:

````markdown
# pyxel-skill Hooks

This directory contains the Claude Code Stop hook used by `pyxel-skill`. The hook is a non-blocking tripwire that warns when the quality gate appears to have been skipped.

## Files

| File | Purpose |
|------|---------|
| `stop_check_bundle.py` | The Stop hook itself. Reads `cwd` from the Stop event, checks for `.pyxel-skill/` project marker, walks `screenshots/result/<latest>/` for proof bundle integrity, and warns to stderr if the bundle is missing or `gate-report.json` shows FAILs. Always exits 0 with `{}` on stdout (non-blocking). |
| `test_stop_check_bundle.py` | pytest suite for the hook (6 cases). Run: `python -m pytest hooks/`. |
| `install.sh` | Idempotent installer. Adds an entry to `~/.claude/settings.json` under `hooks.Stop`. Requires `jq`. |
| `README.md` | This file. |

## Install

```bash
hooks/install.sh
```

The installer reads `$HOME/.claude/settings.json` (or `$CLAUDE_SETTINGS` if set, useful for testing) and appends an entry. Running it twice is safe.

## Uninstall

Edit `~/.claude/settings.json` and remove the entry under `hooks.Stop` whose `command` matches the absolute path of `stop_check_bundle.py`.

## Why a Stop hook

`pyxel-skill`'s quality gate (Stage 7) is the contract for "done". The agent is expected to run the gate and address all FAILs before declaring completion. Empirically, agents skip steps when allowed to. The Stop hook is a session-boundary tripwire that surfaces a missed gate to the user as a warning — it does **not** block the session and does **not** replace the agent running the gate.

## Behavior

| Project state | Hook output |
|---------------|-------------|
| cwd has no `.pyxel-skill/` directory | silent no-op |
| `.pyxel-skill/` exists, no `screenshots/result/` | warns "no proof bundle found" |
| `screenshots/result/<N>/` exists, no `win-path.gif` | warns "bundle is incomplete" |
| `gate-report.json` exists with FAILs | warns "gate report shows unaddressed FAIL(s)" |
| All clean | silent |

In every case the hook prints `{}` on stdout and exits 0. It cannot block Claude Code from terminating.

## Testing

```bash
cd /Users/takashi/repos/pyxel-skill
python -m pytest hooks/test_stop_check_bundle.py -v
```

Six tests cover: no-marker no-op, missing-bundle warning, incomplete-bundle warning, FAIL-in-gate-report warning, clean-pass silence, malformed-input non-blocking.
````

- [ ] **Step 2: Commit**

```bash
git add hooks/README.md
git commit -m "docs(hook): write hooks/README.md (rationale, install, behavior table)"
```

---

## Task 25: Write `docs/architecture.md`

**Files:**
- Create: `docs/architecture.md`

The architecture doc is a runtime reference for contributors and future Claude sessions. It is **derived from but not a copy of** the design spec — focus on what is shipping, not the rationale (which lives in the spec).

- [ ] **Step 1: Write `docs/architecture.md`**

Create `/Users/takashi/repos/pyxel-skill/docs/architecture.md`:

````markdown
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
````

- [ ] **Step 2: Verify**

```bash
wc -l /Users/takashi/repos/pyxel-skill/docs/architecture.md
```

Expected: ~150 lines.

- [ ] **Step 3: Commit**

```bash
git add docs/architecture.md
git commit -m "docs: write architecture.md (runtime reference; design rationale lives in spec)"
```

---

## Task 26: Write `docs/validation/dk-reference.md`

**Files:**
- Create: `docs/validation/dk-reference.md`

This is the canonical validation prompt + expected schema. Used in Task 28 (end-to-end validation) and as the regression test for future skill changes.

- [ ] **Step 1: Write `docs/validation/dk-reference.md`**

Create `/Users/takashi/repos/pyxel-skill/docs/validation/dk-reference.md`:

````markdown
# Donkey Kong Validation Reference

Canonical validation prompt for `pyxel-skill` v0.1.0 and beyond.

## Why DK

Donkey Kong is a single-screen platformer with these properties that exercise the harness end-to-end:

1. **Recognizable cast**: Mario, DK boss, princess, barrel, ladder, girder. A blob test reviewer can identify each from a screenshot — the asset identity contract has teeth.
2. **Multi-state animation**: Mario walks, jumps, climbs. Animation timing matters.
3. **Vertical traversal with hazards**: barrels rolling down inclined girders, ladders to climb. Win path requires platform/ladder logic; lose path requires barrel-collision logic.
4. **Win and lose conditions**: reach princess at top → WIN; collide with barrels until lives==0 → GAME_OVER. Both paths can be scripted.
5. **Audio-rich**: jump SE, climb SE, death SE, win SE, plus optional BGM.

A skill that can produce a clearable, recognizable DK is robust enough to handle most arcade-style games. Other validation prompts (shmup, puzzle) can be added in future releases.

## The prompt

> Make a Donkey Kong style platformer in Pyxel. Single screen, portrait orientation. Mario climbs ladders to reach the princess at the top while dodging barrels rolled by Donkey Kong on a girder above.

## Expected pipeline path

Stage 1 → 2 → 3 → 4 → 5 → 6 → 7 (no resume; PLAN.md does not exist on first run).

## Expected artifacts

After a successful run:

```
<project-root>/
├── main.py                          # Pyxel game source
├── PLAN.md                          # Stage 2 output
├── STRUCTURE.md                     # Stage 1 + Stage 3 output
├── ASSETS.md                        # Stage 1 + Stage 4 output
├── MEMORY.md                        # Stage 6 output (may be empty)
├── .pyxel-skill/
│   └── stage-marker
└── screenshots/
    └── result/
        └── 1/
            ├── gate-report.json     # Stage 7 output, all 12 checks PASS
            ├── win-path.gif         # 600+ frames, ends on WIN scene
            ├── lose-path.gif        # 360+ frames, ends on GAME_OVER scene
            ├── frames/
            │   ├── title.png
            │   ├── play_start.png
            │   ├── mid_game.png
            │   ├── win.png
            │   └── game_over.png
            ├── audio/
            │   ├── bgm_ch0.wav
            │   ├── bgm_ch1.wav
            │   ├── bgm_ch2.wav
            │   ├── se_jump.wav
            │   ├── se_climb.wav
            │   ├── se_death.wav
            │   └── se_win.wav
            └── notes.md
```

## Win path schedule (canonical)

Encoded in PLAN.md after Stage 2. The schedule below is the expected shape, not a literal milestone count — exact frames depend on tuning.

| Frame | Inputs                  | Asserts                                                              |
|-------|-------------------------|----------------------------------------------------------------------|
| 30    | KEY_SPACE               | scene == "PLAY", lives == 3, player.x ≈ start_x, player.y ≈ start_y  |
| 60    | KEY_RIGHT held          | player.x > start_x + 20                                              |
| 120   | KEY_UP at ladder_a      | player.y < floor_y - 8 (climbing)                                    |
| 200   | (continuing climb)      | player.y < floor_y - 32                                              |
| 280   | KEY_RIGHT held on ladder top | player.x > 100                                                  |
| 360   | KEY_UP at ladder_b      | player.y < floor_y - 64                                              |
| 480   | KEY_UP at ladder_c      | player.y < floor_y - 96                                              |
| 600   | KEY_UP near princess    | player.y < 32                                                        |
| 660   | (no input)              | scene == "WIN"                                                       |

## Lose path schedule (canonical)

| Frame | Inputs       | Asserts                                                  |
|-------|--------------|----------------------------------------------------------|
| 30    | KEY_SPACE    | scene == "PLAY", lives == 3                              |
| 100   | (no input)   | a barrel exists somewhere on a girder                    |
| 200   | (no input)   | barrel.y >= player.y - 8                                 |
| 240   | (no input)   | lives <= 2                                               |
| 360   | (no input)   | lives == 0                                               |
| 420   | (no input)   | scene == "GAME_OVER"                                     |

Frame 420 (≈ 14 seconds at 30fps) is the upper bound. Faster lose-path completion is fine.

## Asset minimums

ASSETS.md after Stage 4 must contain:

- Player: `idle`, `walk_1`, `walk_2`, `jump`, `climb_1`, `climb_2` (6 sprites, 16x16).
- Antagonist: at least `boss_idle` (32x32).
- Goal: `princess` (16x24).
- Hazard: `barrel_1`, `barrel_2` (16x16, paired-frame diff 5–50%).
- HUD: `life_icon` (8x8).

If `inspect_animation` reports a paired-frame diff outside 5–50% on any pair, gate check #4 FAILs.

## Quality gate expected output

`screenshots/result/1/gate-report.json` should show:

- `summary.pass` == 12, `summary.fail` == 0.
- All 12 checks individually PASS per the `quality-gate.md` table.

## Out-of-scope for v0.1.0 DK

- Multiple levels (the original game has 4 stages; we accept 1 level for v0.1.0).
- Hammer power-up (optional asset, can be deferred).
- Cinema sequences (DK climbing the building, princess "HELP!" blinking is OK).
- Multiplayer / hi-score persistence.

## Iteration record

Each end-to-end validation run is logged at `docs/retrospectives/YYYY-MM-DD-dk.md`. The retro documents:

- Prompt verbatim used.
- Pipeline path actually taken (resume detected? skipped a stage?).
- Where the agent diverged from this reference.
- What was fixed in the skill source.
- What stays as a known limitation.
````

- [ ] **Step 2: Verify**

```bash
wc -l /Users/takashi/repos/pyxel-skill/docs/validation/dk-reference.md
```

Expected: ~150 lines.

- [ ] **Step 3: Commit**

```bash
git rm docs/validation/.gitkeep
git add docs/validation/dk-reference.md
git commit -m "docs(validation): write Donkey Kong reference (canonical validation prompt + expected artifacts)"
```

---

## Task 27: Write `docs/compatibility-matrix.md`

**Files:**
- Create: `docs/compatibility-matrix.md`

- [ ] **Step 1: Write `docs/compatibility-matrix.md`**

Create `/Users/takashi/repos/pyxel-skill/docs/compatibility-matrix.md`:

````markdown
# pyxel-skill Compatibility Matrix

Known-working combinations of pyxel-skill, pyxel-mcp, and the underlying Pyxel engine.

## Pinning policy

The `Required runtime` block in `SKILL.md` lists the **floor** version of pyxel-mcp that pyxel-skill expects. The actual tested combinations are recorded here.

When a new pyxel-skill release is tagged, append a new row with the validated versions and the date of validation. Do not delete old rows — they are useful for users on older toolchains.

## Matrix

| pyxel-skill | pyxel-mcp | Pyxel engine | Python | Validated on  | Validation prompt | Notes                                                        |
|-------------|-----------|--------------|--------|---------------|-------------------|--------------------------------------------------------------|
| 0.1.0       | 0.9.3     | 2.8.7        | 3.14   | 2026-05-01    | DK                | Initial release. macOS Darwin 25.3.0 + uv 0.10.7 + Pyxel 2.8.7 in `.venv`. |

## Floor / ceiling guidance

- **pyxel-mcp floor:** 0.9.3 — required because earlier versions still carry the design knowledge in `instructions.md` that pyxel-skill v0.1.0+ migrated to `knowledge/`. Earlier pyxel-mcp versions still work as a tool host but pollute context.
- **pyxel-mcp ceiling:** open. New versions are presumed compatible until proven otherwise.
- **Pyxel engine floor:** 2.8.7 — earlier versions lack `pyxel.gen_bgm` (added 2.9.0 syntax change) and `pyxel.set_btnv` headless input (used by pyxel-mcp's `play_and_capture`).
- **Pyxel engine ceiling:** open.
- **Python floor:** 3.10 (uses `from __future__ import annotations` plus 3.10+ syntax in hooks; pyxel-mcp itself requires ≥3.10).

## Reporting compatibility issues

If pyxel-skill produces broken output on a newer pyxel-mcp or Pyxel engine, file an issue with:

- Versions of pyxel-skill, pyxel-mcp, Pyxel, Python.
- The validation prompt used.
- The contents of `screenshots/result/<N>/gate-report.json` (or note that no bundle was produced).
- The contents of `MEMORY.md` (gotchas the agent recorded during the run).

A new row is added to the matrix once the issue is diagnosed and either pyxel-skill is updated or the version pair is documented as incompatible.
````

- [ ] **Step 2: Commit**

```bash
git add docs/compatibility-matrix.md
git commit -m "docs: write compatibility-matrix (pyxel-skill ↔ pyxel-mcp ↔ Pyxel engine + Python pin)"
```

---

## Task 28: End-to-end DK validation

**Files:**
- Create: `docs/retrospectives/2026-05-01-dk.md` (after the run)

This is the integration test for v0.1.0. The skill must drive a "make Donkey Kong" prompt through the full pipeline successfully. **Do not** ship v0.1.0 if this fails.

- [ ] **Step 1: Pre-flight checks**

```bash
# pyxel-skill is on the v5 branch with all files in place.
cd /Users/takashi/repos/pyxel-skill
git status                                                  # clean
ls SKILL.md visual-target.md decomposer.md scaffold.md \
   asset-planner.md asset-gen.md task-execution.md \
   quality-gate.md quirks.md test-harness.md capture.md     # all present
ls knowledge/pixel-art.md knowledge/background.md \
   knowledge/game-feel.md knowledge/audio.md \
   knowledge/patterns.md                                    # all present
ls hooks/stop_check_bundle.py hooks/install.sh \
   hooks/README.md                                          # all present
ls docs/architecture.md docs/validation/dk-reference.md \
   docs/compatibility-matrix.md                             # all present

# pyxel-mcp 0.9.3 is shipped (see separate plan; this task is blocked on that).
uvx pyxel-mcp --version                                     # should print 0.9.3 or later
```

If `uvx pyxel-mcp --version` is < 0.9.3, **stop**. Complete the pyxel-mcp 0.9.3 trim plan (separate doc) and ship it before continuing here.

- [ ] **Step 2: Symlink the skill into the active Claude Code skills directory**

```bash
ln -sfn /Users/takashi/repos/pyxel-skill ~/.claude/skills/pyxel
ls -la ~/.claude/skills/pyxel
```

Expected: symlink pointing to the repo.

- [ ] **Step 3: Install the Stop hook**

```bash
/Users/takashi/repos/pyxel-skill/hooks/install.sh
```

Expected: "installed Stop hook: ..." (first time) or "already installed" (subsequent).

- [ ] **Step 4: Create a fresh game-project working directory**

```bash
TEST_DIR="$HOME/tmp/pyxel-skill-dk-validation-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"
git init
echo "$TEST_DIR"  # remember this path; you'll use it below
```

- [ ] **Step 5: Run the validation prompt**

In a fresh Claude Code session, in `$TEST_DIR`, ask:

> Make a Donkey Kong style platformer in Pyxel. Single screen, portrait orientation. Mario climbs ladders to reach the princess at the top while dodging barrels rolled by Donkey Kong on a girder above.

The skill should activate (its `description` matches the prompt), read `SKILL.md`, and begin Stage 1.

Let it run end-to-end. Do not interrupt. The full pipeline is expected to take 1–4 hours of agent time.

- [ ] **Step 6: When the agent reports completion, verify the gate report**

```bash
cat "$TEST_DIR/screenshots/result/1/gate-report.json" | jq '.summary'
```

Expected: `{ "pass": 12, "fail": 0, "total": 12 }`.

If `summary.fail > 0`:
- Open `gate-report.json` and read each FAIL entry's `evidence`.
- Map the FAIL to the phase via the `fail_route` in each check.
- This is iteration data — record what failed and why.

- [ ] **Step 7: Verify proof bundle integrity**

```bash
ls "$TEST_DIR/screenshots/result/1/"
```

Expected: `gate-report.json`, `win-path.gif`, `lose-path.gif`, `frames/`, `audio/`, `notes.md`.

```bash
# Confirm GIFs are non-trivial.
file "$TEST_DIR/screenshots/result/1/win-path.gif"
ls -lh "$TEST_DIR/screenshots/result/1/win-path.gif"   # should be > 100 KB
ls -lh "$TEST_DIR/screenshots/result/1/lose-path.gif"  # should be > 50 KB
ls "$TEST_DIR/screenshots/result/1/audio/" | wc -l     # ≥ 5 .wav files
```

- [ ] **Step 8: Manual review**

Open the GIFs in a browser or image viewer. Verify:

- **win-path.gif**: Mario is recognizable (red cap, blue overalls — not a rectangle). Mario climbs ladders, traverses girders, reaches the princess. The clip ends on a WIN scene.
- **lose-path.gif**: A barrel rolls down, hits Mario, lives decrement, eventually GAME_OVER.
- **frames/title.png**: TITLE screen has pixel-art title text and a blinking PRESS prompt; not a plain black screen.

If any of these fail subjectively, this is iteration data — record in the retro and fix in the skill source.

- [ ] **Step 9: Write the retrospective**

Create `/Users/takashi/repos/pyxel-skill/docs/retrospectives/2026-05-01-dk.md`:

```markdown
# 2026-05-01 — DK validation run

## Prompt

> Make a Donkey Kong style platformer in Pyxel. Single screen, portrait orientation. Mario climbs ladders to reach the princess at the top while dodging barrels rolled by Donkey Kong on a girder above.

## Outcome

- Gate report: <PASS / N FAIL>
- Win-path GIF duration: <seconds>
- Lose-path GIF duration: <seconds>
- Asset count vs DK reference minimum: <ratio>
- Subjective recognizability (Mario / DK / princess / barrel): <good / mediocre / poor>

## Pipeline path observed

<list the order of stages the agent actually invoked, with any divergence>

## Where the agent diverged from `docs/validation/dk-reference.md`

<bulleted list of specific divergences — milestone frame numbers, asset inclusions, scene composition>

## Fixes applied to the skill source

<list of commits made to pyxel-skill in response to this run>

## Known limitations accepted for v0.1.0

<list of issues observed but accepted as out-of-scope>

## Next steps

<what to do before tagging v0.1.0 — could be empty if the run is clean>
```

- [ ] **Step 10: Commit the retrospective**

```bash
cd /Users/takashi/repos/pyxel-skill
git rm docs/retrospectives/.gitkeep
git add docs/retrospectives/2026-05-01-dk.md
git commit -m "docs(retrospective): record 2026-05-01 DK validation run"
```

- [ ] **Step 11: Iterate if needed**

If the validation surfaced issues that can be fixed in the skill source (not the agent's output):
- Apply fixes to the relevant skill file(s).
- Commit each fix with a clear message: `fix(stage|knowledge|hook): <what changed>`.
- Re-run the validation in a NEW `$TEST_DIR` (do not reuse the previous one — bundles must be fresh).
- Update the retro with a new section: `## Iteration N`.

When the run is clean (gate all-PASS, GIFs subjectively good), proceed to Task 29.

---

## Task 29: Tag v0.1.0

**Files:**
- (no file changes; tagging only)

- [ ] **Step 1: Final pre-tag check**

```bash
cd /Users/takashi/repos/pyxel-skill
git status                # clean
git log --oneline -20     # all commits since start of feat/harness-v5
```

Verify the latest DK retrospective is committed and reports a clean run.

- [ ] **Step 2: Merge to main**

```bash
git checkout main
git merge feat/harness-v5 --no-ff -m "Merge feat/harness-v5: pyxel-skill v0.1.0"
```

- [ ] **Step 3: Tag**

```bash
git tag -a v0.1.0 -m "pyxel-skill v0.1.0 — initial release. Validated against Donkey Kong prompt 2026-05-01."
git push origin main --tags
```

- [ ] **Step 4: Verify tag is published**

```bash
git tag | grep v0.1.0
git ls-remote --tags origin | grep v0.1.0
```

Expected: tag exists locally and on origin.

- [ ] **Step 5: Update auto-memory**

After this plan is fully executed, update `~/.claude/projects/-Users-takashi-repos-pyxel-mcp/memory/project_pyxel_skill_harness.md` with:

- v0.1.0 release date.
- DK validation outcome reference.
- Move the project from "Active Project" status to "Released" or remove the active marker, depending on whether further work is anticipated immediately.

---

## Self-review checklist

After plan generation (already complete; this section is a validation pass on the plan itself):

**Spec coverage:**
- [x] §4 Architecture — Tasks 6 (SKILL.md), 7-13 (stages), 14-16 (references), 17-21 (knowledge), 22-24 (hooks), 25-27 (docs).
- [x] §5 SKILL.md contents — Task 6 covers all six required sections.
- [x] §6 Pyxel-specific deviations — embedded in Tasks 7-13 (each stage's content reflects the deviation rules).
- [x] §7.1-7.7 stage specifications — Tasks 7-13 each port the corresponding §7 subsection.
- [x] §8 reference files — Tasks 14-16.
- [x] §9 migration — Task 1 (archive), Tasks 7-13 + 14-16 (carry-forward with rebrand per §9.1 rename map).
- [x] §10 pyxel-mcp 0.9.3 trim — **out of scope for this plan; separate plan.**
- [x] §11 Implementation order — Tasks 1-29 follow the spec §11.1 step ordering with pyxel-mcp 0.9.3 ship deferred to its own plan but blocking Task 28.
- [x] §12 open questions — accepted as iterative ("やりながら調整"); Task 28 retro records actual answers.
- [x] §13 risks — mitigated by Task 28 (end-to-end validation) before tagging.

**Placeholder scan:**
- "(content from instructions.md ...)" patterns in Tasks 17-21 are templates that the executing agent must replace with actual extracted content. The Steps in those tasks include the `awk`/`sed` extraction commands and the verification line counts to detect under-population. Acceptable.
- Task 12 (task-execution.md), Task 15 (test-harness.md), Task 16 (capture.md) describe content "follow v3 structure with v5 file names" without including the full prose. This is intentional — porting that volume of text into the plan would triple its length without adding value. The executing agent reads the v3 archive (commands provided) and writes the new file using v5 references. Acceptable.

**Type consistency:**
- Stage file names consistent across all tasks: `visual-target.md`, `decomposer.md`, `scaffold.md`, `asset-planner.md`, `asset-gen.md`, `task-execution.md`, `quality-gate.md`.
- Field names from pyxel-mcp tools used consistently: `color_count`, `fill_ratio`, `Hierarchy score: X/2`, `inspect_animation` does paired-frame diff automatically.
- Persistent state files: `PLAN.md`, `STRUCTURE.md`, `ASSETS.md`, `MEMORY.md` everywhere.
- Project marker: `.pyxel-skill/` everywhere (created by Task 9, checked by Task 22, mentioned in Task 24/25).
- Bundle path: `screenshots/result/<N>/` everywhere.
- Gate report: `screenshots/result/<N>/gate-report.json` everywhere.

---

## Plan complete

This plan has 29 tasks covering pyxel-skill v0.1.0 end-to-end. The plan is self-contained with respect to the design spec — every spec section maps to one or more tasks.

**Out of scope (separate plan needed):**
- pyxel-mcp 0.9.3 trim (§10 of the spec). Task 28 is blocked on that release shipping. Recommended to write the pyxel-mcp 0.9.3 plan and execute it in parallel with Tasks 1-27 of this plan, then run Task 28 once both are complete.
