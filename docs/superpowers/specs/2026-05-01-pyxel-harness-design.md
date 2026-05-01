# Pyxel Harness Design (v5)

- **Date:** 2026-05-01
- **Author:** Takashi Kitao (drafted with Claude Opus 4.7)
- **Status:** Draft for review
- **Target repos:** `kitao/pyxel-skill` (new), `kitao/pyxel-mcp` (concurrent 0.9.3)
- **Reference design:** `htdt/godogen` (`/tmp/godogen` checkout)

## 1. Goal

Build a Claude Code Skill (`pyxel-skill`) that, combined with the existing `pyxel-mcp` MCP server, lets an AI agent produce **playable, clearable, recognizable-sprite** retro games end-to-end from a natural-language brief — with workflow-level enforcement that resists the agent's tendency to declare "done" prematurely.

The skill is modeled on `htdt/godogen` but **adapted to Pyxel's actual constraints, not slavishly transplanted**. Function-equivalence trumps shape-equivalence (per direct user instruction).

### Validation criterion

A representative test prompt — "make Donkey Kong" — driven through the skill must yield a project where:

1. The script runs without crashing under `pyxel-mcp`'s `run_and_capture`.
2. A scripted win-path input sequence reaches `scene == WIN`.
3. A scripted lose-path (e.g., stand still) reaches `scene == GAME_OVER`.
4. A blind reviewer shown a frame snapshot can identify the player sprite as "a person" (not a colored rectangle), the antagonist as "a boss", and the goal as "a princess/damsel".
5. Audio renders contain non-empty notes for declared SE entries.
6. A `screenshots/result/{N}/` proof bundle exists with a video that shows behavior across its full duration (not "first 3s correct, rest static").

## 2. Non-goals

- **Not** a competitor to `htdt/godogen`. The two skills cover different engine ecosystems (3D-capable Bevy/Godot vs. retro 2D Pyxel) and different asset pipelines (gen-AI image+3D vs. hand-coded hex sprites).
- **Not** an asset-generation pipeline. Pyxel sprites are hex strings, not Gemini/Grok images. The `import_sprite` experiment was already removed (see auto-memory: AI sprite generation produces unstable quality; CC0 palette conversion loses original artistic intent).
- **Not** a wrapper around AI image generation. The "visual target" stage outputs a structured text spec, not `reference.png`.
- **Not** a mechanism to also build pyxel-mcp's own quality features. pyxel-mcp remains an independent MCP server, completable in isolation by users who only want verification tools.
- **Not** Codex / non-Claude-Code-agent compatible at v0.1.0. godogen supports a `--agent codex` render path; pyxel-skill v0.1.0 targets Claude Code only. Codex / Gemini-CLI / Copilot-CLI compatibility is a future-issue candidate, gated on user demand.

## 3. Background

### 3.1 What's broken

`pyxel-mcp` 0.9.3 (current PyPI release) gives the agent ~13 verification tools (run/inspect/audio render/etc.). In repeated dispatched-subagent experiments, even with these tools available, single-call asks like "make Donkey Kong" produce **unplayable garbage**:

- Blob-shaped sprites (single-color rectangles in place of declared characters).
- Jump-through-floor physics (gravity/collision broken).
- Bosses that don't actually spawn hazards, hazards that don't reach the floor.
- "Looks fine" declarations after looking at one screenshot of the title screen.

Tools alone do not enforce quality. **Workflow does.**

### 3.2 Why a separate skill repo (not extending pyxel-mcp)

Two-repo split, decided in prior session:

- **`pyxel-mcp`** — the verbs (run, inspect, capture, render audio) + Pyxel API/quirks technical reference. Independent product; some users will want only this. Distributed via PyPI / Official MCP Registry.
- **`pyxel-skill`** — the production harness (workflow + design knowledge + enforcement). Distributed as a Claude Code Skill, installed under `~/.claude/skills/pyxel/`.

Splitting prevents pyxel-mcp from bloating with workflow knowledge that's irrelevant to direct-tool users, and lets the skill iterate on workflow without forcing pyxel-mcp releases.

### 3.3 Why model on godogen

`htdt/godogen` solves the same class of problem for Godot/Bevy:

- 4 persistent state files (`PLAN.md`, `STRUCTURE.md`, `MEMORY.md`, `ASSETS.md`) that survive context compaction.
- Stage-by-stage progressive loading — only the current stage's instruction file enters context.
- Risk Slice / Main Build separation in task execution.
- Capture-first proof bundle as the contract for "done".
- A separate `Stop` hook for the post-task delivery (Telegram push in godogen).

These ideas all transplant cleanly. **What we change** is detailed in §6.

### 3.4 Why this is happening now

A v3 draft pass already exists (current `feat/harness` branch in `pyxel-skill`, plus `feat/quality-harness` worktree in `pyxel-mcp`). v3 had:

- 9 stages (test-harness and capture promoted to stages, not references).
- 5 persistent state files (separate `REFERENCE.md` from `ASSETS.md`).
- Tier 1 / 2 / 3 quality gate hierarchy.
- No knowledge/ split — all design knowledge inlined into stage files or living in pyxel-mcp's `instructions.md`.

User review converged on a slimmer design (v5, this spec) that is closer to godogen's shape. v3 drafts contain reusable Pyxel-specific knowledge but cannot be merged as-is; see §9 (Migration).

## 4. Architecture overview

### 4.1 Repo layout

Two structurally distinct file types live at repo root: **stages** (sequential pipeline files, JIT-loaded by SKILL.md) and **references** (cross-cut documentation pulled by stages on demand). To make this distinction explicit without forcing path churn on every doc reference, the layout uses inline annotations:

```
pyxel-skill/
├── SKILL.md                       Orchestrator: frontmatter, pipeline, anti-shortcut rules, gate contract
│
│   # === Stages (read in pipeline order) ===
├── visual-target.md               Stage 1: art direction + Vision section
├── decomposer.md                  Stage 2: PLAN.md
├── scaffold.md                    Stage 3: STRUCTURE.md + skeleton main.py + .pyxel-skill/ marker
├── asset-planner.md               Stage 4: ASSETS.md sprite manifest
├── asset-gen.md                   Stage 5: hex-string sprites + per-asset verify loop
├── task-execution.md              Stage 6: gameplay implementation loop
├── quality-gate.md                Stage 7: stop-conditions + structured PASS/FAIL report
│
│   # === References (loaded on demand by stages) ===
├── quirks.md                      Pyxel API gotchas (JIT-loaded when surprised)
├── test-harness.md                Milestone playthrough (called from task-execution Stage 6)
├── capture.md                     Proof bundle production (called from task-execution / quality-gate)
│
│   # === Topical knowledge (loaded by stage as needed) ===
├── knowledge/
│   ├── pixel-art.md              Sprite + palette + color hierarchy
│   ├── background.md             Background tiers, parallax, screen layout
│   ├── game-feel.md              Physics, jumps, hitboxes, camera, screen shake, hitstop
│   ├── audio.md                  SE cookbook + MML/gen_bgm patterns + channel discipline
│   └── patterns.md               Title screen, scene SM, level/enemy design, animation timing
│
│   # === Hooks (Pyxel-specific harness enforcement) ===
├── hooks/
│   ├── stop_check_bundle.py      Stop hook: assert proof bundle integrity / quality-gate state
│   ├── install.sh                merges hook config into ~/.claude/settings.json (idempotent)
│   └── README.md                  hook rationale + uninstall instructions
│
│   # === Docs (contributor-facing) ===
├── docs/
│   ├── architecture.md           Runtime architecture (companion to this design spec)
│   ├── retrospectives/           Per-test-run retros (`YYYY-MM-DD-<title>.md`)
│   ├── validation/
│   │   └── dk-reference.md      Donkey Kong validation: input event list + asserted state schema
│   └── compatibility-matrix.md   pyxel-mcp ↔ pyxel-skill ↔ Pyxel engine version pairings
├── README.md
├── LICENSE
└── .gitignore
```

> **Why annotations rather than sub-directories** (e.g., `stages/`, `references/`): all stage files cross-reference each other (`task-execution.md` reads `test-harness.md` etc.). Putting them under different subdirectories would force every cross-reference to use a relative path. godogen also keeps these flat at one level. This is a deliberate functional choice, not a deviation worth flagging in §6.

### 4.2 Pipeline (textual)

The SKILL.md orchestrator presents this as an ASCII diagram. Conditional branches (resume detection, risk slice vs. main build, gate-FAIL loopback) are shown explicitly.

```
User request: "make a Pyxel game …"
        |
        +-- PLAN.md exists?
        |     |
        |     +-- yes: read PLAN.md / STRUCTURE.md / MEMORY.md / ASSETS.md, jump to Stage 6
        |     +-- no: continue
        |
        +-- Stage 1  visual-target  →  ASSETS.md "Art direction" + STRUCTURE.md "Vision" subsection
        +-- Stage 2  decomposer     →  PLAN.md (Risk Tasks + Main Build + Win/Lose milestones)
        +-- Stage 3  scaffold       →  STRUCTURE.md (Scenes, Constants/Tuning subsections) + skeleton main.py
        +-- Stage 4  asset-planner  →  ASSETS.md (sprite manifest with represents/palette/region)
        +-- Stage 5  asset-gen      →  pyxel.images[N].set(...) calls verified per-asset
        |
        +-- Stage 6  task-execution
        |     +-- Risk Slice: implement each PLAN.md risk task in isolation, verify, commit
        |     +-- Main Build: implement remainder, verify, commit
        |     +-- (calls test-harness.md and capture.md as references when needed)
        |
        +-- Stage 7  quality-gate   →  flat stop-conditions list; FAIL → loop back to phase that owns the failure
        |
        +-- proof bundle present
        +-- Stop hook fires (best-effort assertion that bundle is well-formed)
        +-- summary to user
```

### 4.3 Persistent state files

Four files at project root, written across stages, read on resume:

| File          | First written by   | Purpose                                                                               |
|---------------|--------------------|---------------------------------------------------------------------------------------|
| `PLAN.md`     | Stage 2 decomposer | Risk Tasks (with Approach + Verify) + Main Build modules + Win/Lose milestone tables  |
| `STRUCTURE.md`| Stage 3 scaffold   | Architecture: modules, scene state machine, tuned constants, Vision (from Stage 1)    |
| `ASSETS.md`   | Stage 1 visual-target | Art direction (Stage 1) + sprite manifest (Stage 4) + per-sprite identity contract |
| `MEMORY.md`   | Stage 6 onward     | Discoveries, gotchas, what worked / didn't                                            |

**Why no separate `REFERENCE.md` / `VISION.md` / `SCENES.md` / `TUNING.md`** (v3 had these, v5 collapses):

- `REFERENCE.md`'s 7 sections in v3 split cleanly: window contract + scene transitions go in `STRUCTURE.md` (where they belong with architecture); palette/object/HUD/audio go in `ASSETS.md` (where they belong with the asset manifest); win/lose conditions go in `PLAN.md` (where they belong with milestones).
- A separate file for art direction creates a synchronization burden — the asset-planner must already read `ASSETS.md`, so putting art direction at the top of `ASSETS.md` (godogen pattern) keeps it co-located with downstream consumers.
- 4 state files matches godogen exactly. Cognitive load for the agent (which file holds what) is lower with fewer files.

### 4.4 Stages: what enters context when

The orchestrator (SKILL.md) directs the agent to read each stage file **only when entering that stage** (JIT loading). This keeps context budget for the actual work. Reference files (`quirks.md`, `test-harness.md`, `capture.md`, `knowledge/*`) are loaded on demand from within stage files.

| #  | File                  | Output                                              | pyxel-mcp tools used                                                       |
|----|-----------------------|-----------------------------------------------------|----------------------------------------------------------------------------|
| 1  | `visual-target.md`    | ASSETS.md "Art direction" + STRUCTURE.md "Vision"   | (none — text-only)                                                         |
| 2  | `decomposer.md`       | PLAN.md                                             | (none — text-only)                                                         |
| 3  | `scaffold.md`         | STRUCTURE.md complete + skeleton main.py            | `validate_script`, `run_and_capture`                                       |
| 4  | `asset-planner.md`    | ASSETS.md sprite manifest                           | `inspect_palette` (palette budget feasibility)                             |
| 5  | `asset-gen.md`        | `_build_assets()` populated, per-sprite verified    | `validate_script`, `inspect_sprite`, `inspect_bank`, `inspect_animation`   |
| 6  | `task-execution.md`   | gameplay code, MEMORY.md updates                    | all gameplay tools (run/play/inspect/state)                                |
| 7  | `quality-gate.md`     | structured PASS/FAIL report                         | all                                                                        |

### 4.5 Knowledge files: 5, demand-loaded

| File                     | Loaded from                                                                  | Contains                                                                |
|--------------------------|------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| `knowledge/pixel-art.md` | asset-planner, asset-gen, **quality-gate** (palette / contrast thresholds)   | 16-color palette, 3-layer hierarchy, 3-color-per-material, sprite sizes; gate threshold rationale |
| `knowledge/background.md`| visual-target, scaffold, **quality-gate** (layout-balance threshold)         | bg tiers, parallax, screen size derivation, text layout; gate threshold rationale |
| `knowledge/game-feel.md` | task-execution                                                               | platformer physics, variable jump, coyote/buffer, hitbox, camera, screen shake, hitstop |
| `knowledge/audio.md`     | scaffold (channel allocation), task-execution (SE)                           | SE cookbook, MML composition, gen_bgm patterns, channel discipline      |
| `knowledge/patterns.md`  | scaffold (scene SM), task-execution (level/enemy)                            | title-screen recipe, scene state-machine template, level zoning, enemy archetypes, animation timing |

The split is intentional: **load only what you need at this stage**. A Stage 1 visual-target step does not need `game-feel.md`. A Stage 6 physics-tuning task does not need `pixel-art.md` (the sprites are already done).

### 4.6 Hook: bundle integrity check (Pyxel-specific)

godogen's `Stop` hook is best-effort Telegram push (no enforcement). pyxel-skill's `Stop` hook plays a different role: **last-line check that the agent did not skip the gate**.

#### Hook contract

When the Claude Code session terminates and the cwd is a pyxel-skill project (detected by the presence of a marker file — see §4.6.2 below):

1. If `screenshots/result/<N>/` does not exist → write a non-blocking warning to stderr; do not block stop.
2. If the latest `<N>/` exists but lacks `win-path.gif` (or whatever PLAN.md defines as the proof bundle contract) → warning.
3. If `quality-gate.md`'s structured report exists at `screenshots/result/<N>/gate-report.json` and shows unaddressed FAILs → warning.
4. Otherwise no-op.

The hook **never blocks**. It is a tripwire for the user, not a process gatekeeper. The actual gate is in `quality-gate.md` (the agent must run it itself before declaring done).

#### Project marker

A pyxel-skill project is identified by a `.pyxel-skill/` directory at project root.

- **Who creates it:** `scaffold.md` (Stage 3) creates `.pyxel-skill/` as part of its outputs (alongside `STRUCTURE.md` and skeleton `main.py`). The directory contains:
  - `stage-marker` — current stage name (e.g., `stage-6-task-execution`).
  - `gate-snapshots/` — historical `gate-report.json` files keyed by attempt number.
- **What the hook does:** the hook reads the git toplevel of the cwd, checks for `.pyxel-skill/`, and no-ops silently if the directory is absent. This keeps the hook from tripping on every Claude Code session in unrelated repos.
- **Why scaffold owns it (not visual-target):** scaffold is the first stage that writes code to the project (skeleton main.py); creating the marker there guarantees the marker is present whenever `pyxel.init()` is callable.

#### Hook installation flow

`hooks/install.sh` is run **once per host machine** by the user, after they place the `pyxel-skill` repo at `~/.claude/skills/pyxel/` (via symlink or copy). It:

1. Reads `~/.claude/settings.json`.
2. Appends an entry to `hooks.Stop` referencing the absolute path of `~/.claude/skills/pyxel/hooks/stop_check_bundle.py`. Detects and skips if an entry with the same script path already exists (idempotent).
3. Prints the new effective Stop-hook list and a one-line "to disable: edit settings.json and remove this entry" reminder.

The skill itself **does not** auto-install the hook on activation. Hook permission is a user-controlled trust boundary — automatic merge would be inappropriate. Skill activation may print a one-line warning if `~/.claude/settings.json` lacks the hook entry.

#### Why a hook at all (vs. trusting the agent to run the gate)

The whole motivation for this skill is that the agent **does** skip steps when allowed. The gate stage is the contract. The hook enforces "you did not skip the gate" at session boundary. Without it, an agent that gives up mid-way and reports "done" gets a free pass. With it, the user sees a warning the moment that happens.

This is a deliberate Pyxel-specific deviation from godogen and is justified by the failure-mode evidence (see §3.1).

### 4.7 docs/

- `architecture.md` — runtime architecture for contributors / future Claude sessions reading the skill source.
- `retrospectives/YYYY-MM-DD-<title>.md` — per-test-run retros. Required template: prompt used, observed pipeline path, where the agent diverged, what was fixed in the skill source, what stays as a known limit.
- `validation/dk-reference.md` — Donkey Kong reference test. Concrete input event list + expected state schema for win and lose paths. Used to A/B test skill changes.
- `compatibility-matrix.md` — table of pyxel-skill version × pyxel-mcp version × Pyxel engine version known-working combinations.

## 5. SKILL.md contents (orchestrator)

This is the file that `using-superpowers` resolves when the skill activates. Required sections:

### 5.1 Frontmatter

```yaml
---
name: pyxel
description: Build complete retro games with Pyxel through a verified, gated pipeline. TRIGGER when the user wants to make a Pyxel / retro / 8-bit / pixel-art game, or asks to recreate a classic arcade title. DO NOT TRIGGER on general Python work, on existing non-Pyxel projects, or when a different game engine (Pygame, Godot, Unity) is mentioned.
license: MIT
---
```

The `description` field is what the skill router matches against. Keep it specific; broad triggers cause spurious activation in unrelated Pyxel sessions.

### 5.2 Required runtime declaration

```markdown
## Required runtime

This skill assumes `pyxel-mcp` ≥ {{MCP_VERSION_FLOOR}} is installed and
registered as an MCP server reachable at the namespace `pyxel`.
On activation, before reading any stage file, verify via the MCP
listing:
- `mcp__pyxel__pyxel_info` is callable.
- `mcp__pyxel__validate_script` is callable.

If absent, install:

    uvx pyxel-mcp --version    # check
    # If not installed, instruct the user to add to .mcp.json:
    {
      "mcpServers": {
        "pyxel": { "command": "uvx", "args": ["pyxel-mcp"] }
      }
    }

The skill cannot proceed without these tools.
```

> **`{{MCP_VERSION_FLOOR}}` is a placeholder.** The concrete value is set during the writing-plans / release phase: it must be the pyxel-mcp version that has the trimmed `instructions.md` and the cross-link (§10), which is currently planned as `0.9.3` but subject to user confirmation per `feedback_versioning.md`. Step ordering in §11.1 ensures pyxel-mcp `{{MCP_VERSION_FLOOR}}` is published to PyPI before pyxel-skill v0.1.0 is tagged.

### 5.3 Pipeline (ASCII)

The diagram from §4.2, with explicit "Resume Detection", "Risk Slice + Main Build", "FAIL → re-enter phase" branches.

### 5.4 Anti-shortcut Rules

These are inherited from v3 (battle-tested wording) and supplemented:

1. **Visual primacy.** When code says X happened but a captured frame shows Y, trust the capture.
2. **Trust media over code.** A passing `validate_script` and `run_and_capture` only certify the script does not crash. They do not certify gameplay.
3. **No procedural fallback.** `pyxel.rect(x, y, 16, 16, 8)` in place of a declared sprite means asset-gen was skipped. Go back.
4. **Bundle integrity.** A bundle whose first 3 seconds are correct and the rest is static is FAIL, not partial pass.
5. **Bias toward failure.** If behavior is not clearly visible in capture, treat as not-done.
6. **Closed-loop input only.** Open-loop scripted input drifts past ~200 frames. Use `play_and_capture` with state observation between segments.
7. **No "looks fine".** Every verify is a specific predicate against an observed value, not a vibe check.
8. **No bundle, no done.** A `screenshots/result/<N>/` directory containing win-path.gif, lose-path.gif, frames, audio WAVs is the precondition for declaring "done". A green gate report without a bundle is FAIL. (godogen treats the bundle as a Stop Condition; we elevate it to anti-shortcut-rule level because the agent's failure mode is to claim "everything works" without producing the bundle.)

### 5.5 Quality Gate Contract

Restate that done = quality-gate.md says PASS, with proof bundle, and that any FAIL routes back to the owning phase. The agent cannot self-certify.

### 5.6 Resume Detection block

`ASSETS.md` is touched by **both** Stage 1 (writes the `**Art direction:**` line) and Stage 4 (appends the sprite manifest with `## Sprites` / `## Player` / etc. headings). Resume must inspect the file's contents, not just its existence:

```markdown
On entry, check (in order):

1. `PLAN.md` exists at project root → resume mode. Read PLAN / STRUCTURE / MEMORY / ASSETS,
   route to Stage 6 unless `screenshots/result/<latest>/gate-report.json` shows incomplete earlier stages.

2. `ASSETS.md` exists but `PLAN.md` does not:
   - If `ASSETS.md` contains any sprite-manifest heading (`## Player`, `## Sprites`, `## Hazard`, etc.)
     → Stage 4 was started without Stage 2; an unusual order. Re-enter Stage 2 (decomposer)
       and reconcile: PLAN.md milestones must reference assets actually planned in ASSETS.md.
   - If `ASSETS.md` contains only the `**Art direction:**` line and no sprite headings
     → Stage 1 done, Stage 2 not started. Re-enter Stage 2 (decomposer).

3. `STRUCTURE.md` exists but `PLAN.md` and `ASSETS.md` (with `**Art direction:**`) do not
   → unusual. Treat as corrupted state; ask the user whether to discard and restart.

4. None exist → fresh pipeline, start at Stage 1.
```

### 5.7 What is NOT this skill's job

A short list of negatives (general Python, non-Pyxel engines, MCP-without-skill use) that prevents over-activation.

## 6. Pyxel-specific deviations from godogen (with justification)

This section is a contract: any future skill change that re-aligns with godogen on these points must explicitly re-justify.

### 6.1 No `reference.png` / no AI image generation in Stage 1

**godogen:** Stage 1 calls `asset_gen.py image --model gemini ...` to produce `reference.png`, an in-game-screenshot mockup that anchors all downstream art.

**pyxel-skill:** Stage 1 outputs structured text ("Art direction" line in `ASSETS.md` + "Vision" subsection in `STRUCTURE.md`) describing palette, layout, and per-object identity. No image is generated.

**Why:**
- Pyxel sprites are 8x8 to 32x32 hex strings. A 1K AI-generated mockup down-scaled to 16x16 produces muddy garbage and does not predict what hex strings produce.
- Pyxel's 16-color default palette diverges from any AI-generated image's color distribution; mapping is lossy and confusing.
- Empirical evidence from prior `import_sprite` experiment in pyxel-mcp: AI-generated CC0 conversions lose original artistic intent (Arne16 green → Pyxel brown was the failure case). The tool was deleted.
- The structured text spec is more actionable for hex-string authoring than an image.

### 6.2 No `asset-gen.py` CLI / no Gemini/Grok/Tripo3D budget / no budget-gated stages

**godogen:** Stage 4 spends a user-provided dollar budget on Gemini images, Grok textures, Tripo3D GLB models. `asset_gen.py` is a Python CLI with cost tracking. Crucially, godogen's pipeline (`bevy/skills/godogen/SKILL.md` Pipeline section) makes Stage 4-5 **conditional on budget being provided**:

```
+- If budget provided (and no asset tables in ASSETS.md):
|   +- Plan and generate assets ...
```

Without a budget, godogen skips asset planning/generation entirely and the agent uses procedural primitives.

**pyxel-skill:** Stage 5 is hex-string authoring. Each sprite is `pyxel.images[N].set(x, y, [hex_strings])`. No external API. No budget. The "cost" is verification time (`inspect_sprite` per sprite, `inspect_bank` overall, `inspect_animation` for paired frames). **Stages 4 and 5 are unconditional** — the budget-gated branch in godogen's pipeline simply does not exist for pyxel-skill.

**Why:**
- Pyxel's image bank is direct palette-index pixel data. Gemini/Grok cannot output palette-indexed pixel art at the scales Pyxel uses.
- Manual hex authoring with `inspect_sprite` verification empirically produces better-aligned sprites than any AI-image conversion attempt to date.
- Eliminates external API dependency, API key management, and per-run cost.
- **Why no skip path:** Pyxel sprites are free, fast to author, and required for any non-trivial game (procedural `pyxel.rect()` placeholders are explicitly listed as anti-shortcut violation #3 in §5.4). There is no scenario where skipping Stage 5 is acceptable. Removing the conditional simplifies the orchestrator and removes an escape hatch the agent could exploit.

### 6.3 Quality Gate as a stage (Stage 7), not just a final-bundle requirement

**godogen:** No dedicated quality_gate stage. Stop conditions are inlined in `task-execution.md` and the proof-bundle contract in `capture.md`. The shared `Stop` hook is for Telegram push, not enforcement.

**pyxel-skill:** Stage 7 (`quality-gate.md`) is a distinct phase with a stop-conditions list, FAIL → phase-owner mapping, and structured PASS/FAIL report at `screenshots/result/<N>/gate-report.json`. Plus a Stop hook (§4.6) that warns if the gate was skipped.

**Why:**
- Empirical evidence: a Pyxel agent given freedom to self-certify will declare "done" with garbage. godogen's domain (Godot/Bevy with full 3D rendering, AI-generated assets) catches more issues at compile/scene-load time; Pyxel's hex strings always "compile" — every wrong sprite is a valid `pyxel.images[N].set()` call.
- An explicit gate stage gives the agent a documented, named place to stop and verify, instead of trusting it to remember the rules.
- The hook is a non-blocking tripwire, not a hard stop. It does not replace the agent running the gate; it surfaces failures to the user when the agent skipped it.

### 6.4 Stop conditions are flat (not Tier 1/2/3)

**v3 draft:** Tier 1 (must all pass) / Tier 2 (3 of 4 must pass) / Tier 3 (informational).

**v5:** Flat list of stop conditions in `quality-gate.md`. Each has a phase owner.

**Why:**
- godogen uses a flat list and has not run into the failure modes Tier 2 was meant to soft-allow.
- Tier 2 in v3 included palette hierarchy and contrast checks — these are real but should be hard-required, not "3 of 4". A game with bad contrast is broken.
- Hierarchy was over-engineering; the agent does not need three priority levels, it needs a list of "did you do this".

### 6.5 Five knowledge files (vs. godogen's zero)

**godogen:** Engine-specific knowledge lives in a separate skill (`bevy-help`, `godot-api`) and in the `quirks.md` file.

**pyxel-skill:** A `knowledge/` directory with five topical files (pixel-art, background, game-feel, audio, patterns). Each is JIT-loaded by the stage that needs it.

**Why:**
- pyxel-mcp's current `instructions.md` is 906 lines, of which roughly 600 are design knowledge (color hierarchy, game feel constants, level design, audio cookbook). This knowledge was forced into the MCP server's instructions because there was nowhere else to put it. It pollutes context for users who only want the verbs.
- A separate skill module (`pyxel-help` analogous to `bevy-help`) is overkill — the knowledge does not need version-specific runtime tooling like Bevy's rustdoc. It is documentation, period.
- Inlining knowledge into stage files (v3 approach) makes the stage files huge and forces re-loading the same content across stages.
- Five topical files are loaded on demand. Total knowledge surface stays bounded. Not every stage needs every file.

### 6.6 Two repos (skill + MCP server), not one bundle

**godogen:** Single source repo, publishes runtime files to a fresh game repo via `publish.sh`.

**pyxel-skill + pyxel-mcp:** Two independent repos with independent release cycles. Skill installs to `~/.claude/skills/pyxel/` (manual symlink or copy). MCP server installs via `uvx pyxel-mcp`.

**Why:**
- pyxel-mcp predates this skill. It already has PyPI users, Official MCP Registry presence, and works as a standalone product. Folding it into the skill repo would force its users to either install Claude Code or accept a breaking distribution change.
- The skill has different update cadence (workflow tweaks happen often) than the MCP server (the verbs are stable). Independent repos let each move at its own pace.
- Compatibility is managed via `docs/compatibility-matrix.md` (the skill states which pyxel-mcp range it expects).

### 6.7 Skill activation auto-installs the runtime (with permission prompts respected)

**godogen:** User runs `setup_bevy_docs.sh` and `publish.sh` manually; setup is documented in `setup.md`.

**pyxel-skill:** When the skill activates and detects pyxel-mcp is missing, it issues `uvx pyxel-mcp --version` (and falls back to printing install instructions if Claude Code's permission prompt is denied). It does not silently install. It does not bail without explanation.

**Why:**
- Pyxel users are typically more casual than Bevy/Godot users (target audience is hobbyist game-makers and learners). Automatic install with permission prompt has lower friction than "follow setup.md before activating".
- The agent must respect Claude Code's permission prompt. If denied, bail with a clear message; do not work around the denial.

### 6.8 `scene-generation` stage collapsed into `scaffold`

**godogen:** Two distinct stages — `scaffold.md` creates the project shell (`Cargo.toml`, `src/main.rs`, `src/lib.rs`, root plugin module, `assets/`, `STRUCTURE.md`, `.gitignore`), and `scene-generation.md` separately handles **code-first world construction** (entity spawning, camera setup, scene root, the playable scene's runtime composition).

**pyxel-skill:** A single `scaffold.md` (Stage 3) that produces both the project shell (`main.py` skeleton, `STRUCTURE.md`) **and** the scenes/tuning sections inside `STRUCTURE.md`. There is no separate `scene-generation.md`. Per-scene update/draw functions are stubbed in `scaffold.md`'s skeleton main.py and filled out by Stage 6 task-execution.

**Why:**
- Bevy projects are inherently multi-file (`Cargo.toml` / `src/main.rs` / `src/lib.rs` / `src/game/mod.rs` / scene modules). Separating "project skeleton creation" from "scene composition" reflects Bevy's actual file boundaries — different files own different concerns.
- Pyxel projects are typically single-file (`main.py`). The "project shell" and the "scene root" both live in the same `App` class in the same file. There is no physical artifact that distinguishes them — both are functions on the same class.
- Forcing a separate `scene-generation.md` stage when both stages would write to the same file breaks the "one stage owns one file" invariant and creates unclear authorship.
- Confirmed in prior session as v5 outline ("STRUCTURE.md 内に scenes/tuning セクション").

### 6.9 `quirks.md` size discipline carried forward, content limits enforced

**godogen:** `bevy/skills/godogen/quirks.md` opens with an explicit discipline note: "Keep this file small and high-signal." It carries ~9 items, all confirmed real-world Bevy gotchas. The file ends with a "Feedback Loop" section: "Add only repeated, non-obvious issues that would have prevented real confusion."

**pyxel-skill:** v3-era `quirks.md` has 17 items; v5 carry-forward in §8.1 lists ~16 items. Without an explicit discipline rule, the file risks growing into a generic Pyxel API catalog and duplicating content already in `pyxel-mcp`'s tool docs.

**Why we adopt godogen's discipline rule verbatim:**
- The `quirks.md` value is in finding *the one specific surprise* fast, not in being a comprehensive reference. Long quirks files become unread.
- pyxel-mcp's `instructions.md` already documents tool-output gotchas (truncation, error recovery). `quirks.md` should not duplicate.
- The Pyxel API reference is one URL away (`pyxel://api-reference` MCP resource). `quirks.md` is for *non-obvious* behavior that the API reference does not flag.

**Concrete inclusion rule for v5 quirks.md** (port verbatim from godogen's Feedback Loop):

> Add only **repeated, non-obvious** issues that would have prevented real confusion in a stage file (`scaffold`, `asset-gen`, `task-execution`, `capture`) or in a knowledge file. If an item appears in pyxel-mcp's `instructions.md` Error Recovery section, it does not belong here. If it can be answered by reading `pyxel://api-reference`, it does not belong here.

This rule is also surfaced in §8.1.

## 7. Stage-by-stage specification

This section gives the **purpose, output, key content** of each stage file. Detailed prose-level content (the actual file body) is the writing-plans / implementation phase output.

> **Carry-forward rebrand requirement:** when porting v3 stage content into v5 stage files, anti-patterns and Verify examples must be rebranded per the v3 → v5 rename map in §9.1. v3 references to `REFERENCE.md` become `STRUCTURE.md` "Vision" subsections or `ASSETS.md` rows; v3 Tier 1/2/3 wording becomes flat stop-conditions.

### 7.1 visual-target.md (Stage 1)

**Purpose:** Anchor art direction in text before any code is written. Every spatial and stylistic choice committed here becomes a downstream requirement.

**Outputs:**
- New "Art direction" line at the top of `ASSETS.md`.
- New "Vision" subsection in `STRUCTURE.md` (window contract, palette budget plan, layout map, object enumeration, HUD, audio cues, win/lose definitions).

**Required content (from v3 visual-target.md, minus REFERENCE.md framing):**
- Window contract (W, H, FPS, title, BG color)
- Palette budget (which 16-color indices are used, what role each plays — must reflect 3-layer hierarchy from `knowledge/pixel-art.md`)
- ASCII layout map at one cell per 8 px
- Object enumeration with `represents:` identity contract per object
- HUD elements (text + position + color)
- Audio cues (BGM channels, SE per event, channel allocation)
- Win / lose conditions as predicates

**Anti-patterns (carry forward from v3):**
- "Mario-like character" — vague references; commit to a specific look.
- Plain background; gets forgotten downstream.
- Listing colors without roles.

**Loads from knowledge/:** `pixel-art.md` (palette + hierarchy), `background.md` (screen size derivation), `audio.md` (channel discipline).

### 7.2 decomposer.md (Stage 2)

**Purpose:** Convert the Stage 1 vision into a verifiable plan with risk isolation and milestone tables for the gate.

**Output:** `PLAN.md`.

**Required structure:**
- Risk Tasks section: each with `Why isolated`, `Approach`, `Verify`, `Status`.
- Main Build section: modules + cross-cutting verify criteria.
- Win Path Milestones table: Frame | Inputs | Asserts.
- Lose Path Milestones table: Frame | Inputs | Asserts.
- Audio Manifest (restated from Stage 1 for downstream consumption).
- Asset Manifest pointer (forward reference to ASSETS.md filled by Stage 4).

**Pyxel-specific risk taxonomy** (carry from v3, prune for v5):
- Variable-jump physics
- Sloped platform collision
- Ladder snap + scene-transition timing
- Object-on-tilted-girder rolling (DK-specific, generalizes to "moving hazard with terrain interaction")
- Multi-state animation transitions
- Closed-loop input simulation (any path > 200 frames)
- Headless audio determinism (sounds defined but timing slot empty before game loop start)
- Image bank initialization order (`pyxel.images[N].set` after `pyxel.run` is too late)

**Anti-patterns:**
- "Looks right" verify lines.
- Single milestone per path (need intermediates to catch early divergence).
- Risk tasks without `Approach`.
- Lose path with no death trigger.

**Loads from knowledge/:** none required directly. Risk taxonomy is canonical here.

### 7.3 scaffold.md (Stage 3)

**Purpose:** Lock architecture before any gameplay code. Skeleton main.py runs and shows TITLE.

**Outputs:**
- `STRUCTURE.md` filled with: Modules, Scene state machine, Constants/Tuning subsection, Vision subsection (from Stage 1), Verification commands.
- Skeleton `main.py` (compiles, runs, shows TITLE with blinking prompt).

**Required STRUCTURE.md content:**
- Module list (single-file games are common; split only when justified).
- Scene state machine table (TITLE | INTRO | PLAY | WIN | GAME_OVER, transitions).
- Constants block (W, H, FPS, GRAVITY, JUMP_VY, WALK_SPEED, CLIMB_SPEED, MAX_FALL).
- Update / draw dispatch shape (scene → update_X / draw_X dispatch).
- State persistence (what App owns: score, hi_score, lives, current_level, frame, etc.).

**Skeleton main.py contract:**
- `App.__init__` calls `pyxel.init`, `_build_assets()` (empty stub), `_reset()`, `pyxel.run(self.update, self.draw)`.
- TITLE renders with placeholder background and blinking "PRESS SPACE".
- All scenes have stubs; no gameplay logic.
- Verifies clean under `validate_script` and `run_and_capture` at frame 30.

**Anti-patterns:**
- Gameplay code in scaffold.
- Magic numbers in update/draw without lifting to constants.
- Mixing update (state) and draw (render) concerns.

**Loads from knowledge/:** `background.md` (screen size derivation, text layout), `patterns.md` (scene state-machine template, title-screen recipe), `audio.md` (channel allocation only).

### 7.4 asset-planner.md (Stage 4)

**Purpose:** Inventory every sprite the game needs, with bank coordinates, palette plan, identity contract.

**Output:** `ASSETS.md` with sprite manifest.

**Required content per asset:**
- Bank/region (`0 / (0, 0, 16, 16)`)
- `represents:` — single-sentence identity description an outsider could use to identify the rendered sprite blind. **The contract for asset-gen and the gate.**
- `palette:` — 3-6 palette indices used, each tagged with role (outline / cap / overalls / etc.).
- `min distinct color regions:` — integer; failure floor for asset-gen.
- `silhouette:` — bounded; non-transparent pixels < 95% of box.
- `frame relations:` — paired with `<other>`; must differ in 5–50% of pixels.

**Image bank layout:**
- Default: bank 0, 256x256, 8-bit palette indices.
- Pack tightly with a marked "free" region.
- Reserve `(0, 0)` as transparent-equivalent if tilemap is used (avoid (0, 0) trap).

**Required asset categories** (genre-specific; for arcade platformer):
- Player: idle, walk_1, walk_2, jump, climb_1, climb_2 (minimum 5 distinct sprites).
- Antagonist: idle + optional throw_1/throw_2.
- Goal/damsel: 1 sprite.
- Hazard: minimum 2 frames with differing pixels.
- HUD: life icon, optional digit_0–digit_9.
- Environment: tile-able girder/floor, ladder.

**Anti-patterns:**
- "I'll figure out the sprites while coding."
- Asset entries without `represents:`.
- Palette plan missing.
- Reusing the same sprite for "walking" and "idle".

**Loads from knowledge/:** `pixel-art.md` (palette, 3-color-per-material, sprite size guidelines, sprite design process).

### 7.5 asset-gen.md (Stage 5)

**Purpose:** Implement and verify each `ASSETS.md` entry as `pyxel.images[N].set(x, y, [hex_strings])` calls in `_build_assets()`.

**Output:** `_build_assets()` populated; all entries in ASSETS.md have a working `inspect_sprite` showing the declared pixels.

**Per-asset loop:**
1. Write hex-string sprite data into `_build_assets()`.
2. `validate_script` (catches hex-string syntax errors).
3. `inspect_sprite` at the asset's bank coordinates.
4. Read pixels — does silhouette match `represents:`? Are color regions distinguishable?
5. If FAIL — rewrite. Don't move on.

**Sprite identity heuristics** (what `inspect_sprite` lets you check):
- Color region count ≥ ASSETS.md minimum.
- Bounding box density: 15% < density < 95%.
- Edge contrast for outlined sprites.
- Frame pair diff: 5% < diff < 50%.

**Bank organization tip:** use a regions dict matching ASSETS.md, e.g.:

```python
REGIONS = {"player_walk_1": (0, 0), ...}
def _build_assets(self):
    img = pyxel.images[0]
    img.set(*REGIONS["player_walk_1"], [...])
```

**End-of-stage verification:**
- `inspect_bank --image_index=0` — visual scan.
- `inspect_animation` per paired frame.

**Anti-patterns:**
- Sprite definitions in `update()` (run every frame, OR run after `pyxel.run()` starts and is too late).
- `pyxel.rect(x, y, w, h, c)` placeholders in draw (asset-gen was skipped).
- Bulk-edit then bulk-verify (catch one bad sprite before writing 10).
- Missing `colkey=0` in `blt()` calls.

**Loads from knowledge/:** `pixel-art.md` (3-color-per-material, sprite design process).

**Carry forward from v3:** the v3 archive's `asset-gen.md` contains a worked `player_walk_1` 16x16 hex-string example demonstrating the per-asset pattern (cap, face, eyes, mustache, overalls, two buttons, separated legs, shoes). Port that example verbatim into either `knowledge/pixel-art.md` (Sprite Design Process subsection) or v5 `asset-gen.md` to avoid losing it during the migration.

### 7.6 task-execution.md (Stage 6)

**Purpose:** Implement gameplay logic against PLAN.md and STRUCTURE.md, verifying each task before moving on.

**Output:** Working gameplay code; PLAN.md tasks marked done with verified-by notes; MEMORY.md gotchas captured.

**Per-task loop:**
1. Read task definition (PLAN.md), confirm Verify is observable.
2. Read STRUCTURE.md, identify class/function gaining the change.
3. Read current source.
4. Implement the smallest change that makes the task observable.
5. `validate_script` — must be clean.
6. `run_and_capture` at relevant frame — sanity render.
7. Run task's specific Verify procedure (likely `play_and_capture` + `inspect_state` at milestone frames).
8. If FAIL — read captured state, find divergence, fix. Don't move on.
9. If PASS — update PLAN.md, append MEMORY.md if non-obvious gotcha discovered, commit.

**Phases:**
- **Risk Slice** — implement each PLAN.md risk task in isolation. Keep code small. Carry only the validated pattern into Main Build.
- **Main Build** — everything else. Lock scene ownership first, then implement vertical slices.

**Visual primacy** (carry from v3):
- "I drew the player at (40, 100)" but screenshot shows nothing — likely `colkey` issue, layer ordering, or `cls` order.
- "Score increments on barrel-jump" but `inspect_state` shows score == 0 — collision check never fires.
- "Mario climbs" but `play_and_capture` with KEY_UP shows stuck — strict bound (`==` vs `<=`).

**References:**
- `test-harness.md` — read before running milestone playthrough verification.
- `capture.md` — read before producing intermediate captures or final bundle.
- `quirks.md` — read whenever Pyxel behaves unexpectedly.

**Loads from knowledge/:** `game-feel.md` (physics, jumps, hitboxes, camera, screen shake, hitstop), `audio.md` (SE per event), `patterns.md` (level/enemy archetypes, animation timing).

### 7.7 quality-gate.md (Stage 7)

**Purpose:** Final acceptance check. PASS gates "done"; FAIL routes back to phase owner.

**Output:** `screenshots/result/<N>/gate-report.json` with structured PASS/FAIL per check.

**Stop conditions (flat list)** — all must pass:

| # | Check                        | How                                                                                           | FAIL routes to            |
|---|------------------------------|-----------------------------------------------------------------------------------------------|---------------------------|
| 1 | All four state files present | PLAN.md, STRUCTURE.md, ASSETS.md, MEMORY.md exist and non-empty                               | the owning phase           |
| 2 | Script validates             | `validate_script` clean                                                                       | task-execution             |
| 3 | Smoke run                    | `run_and_capture` at frame 30, non-empty image, no crash                                      | task-execution / scaffold  |
| 4 | Asset identity               | Per ASSETS.md entry: `inspect_sprite` reports `len(color_count.keys()) ≥ ASSETS.md minimum` AND `0.15 ≤ fill_ratio ≤ 0.95`. For paired frames: `inspect_animation` reports per-frame pixel diff in 5-50% (the harness computes this automatically; no caller-side diff math needed) | asset-gen                  |
| 5 | Win path                     | `play_and_capture` with PLAN.md win-path inputs reaches `scene == WIN` by final-milestone frame | task-execution or PLAN.md |
| 6 | Lose path                    | `play_and_capture` with PLAN.md lose-path inputs reaches `scene == GAME_OVER` by the final-milestone frame. Lose-path inputs are typically minimal (`KEY_SPACE` once at frame 30 to enter PLAY, then no further input; the player stands still and is killed by hazards). The exact schedule comes from PLAN.md's "Lose Path Milestones" `Inputs` column.   | task-execution or PLAN.md |
| 7 | Audio renders                | For every entry in audio manifest: `render_audio` returns non-empty notes, peak > threshold    | asset-gen / scaffold       |
| 8 | Palette hierarchy            | `inspect_palette` reports hierarchy score 2/2                                                 | asset-planner / asset-gen  |
| 9 | Contrast                     | `inspect_palette` low-contrast warnings ≤ 1                                                   | asset-planner / asset-gen  |
| 10| Difficulty floor             | Lose path triggers GAME_OVER within 10–14 seconds at the configured fps (≈ 300–420 frames at 30fps; ≈ 600–840 frames at 60fps). Too fast = unfair; too slow = the lose path is poorly defined and won't reliably trigger | task-execution / decomposer |
| 11| Layout balance               | `inspect_layout` reports H-balance ≥ 70% on **TITLE** scene (TITLE always has text and produces a stable balance metric). For text-less PLAY scenes, run `inspect_screen` on a representative frame and assert that no quadrant is empty. | scaffold                   |
| 12| Proof bundle                 | `screenshots/result/<N>/` with win-path.gif, lose-path.gif, frames, audio WAVs                | capture (in task-execution)|

**Anti-shortcut rules (restated for the agent at gate time):**
- "It compiles and runs, looks fine" — checks #2 and #3 only certify no-crash.
- "I added a sprite" — without `inspect_sprite` matching `represents`, the sprite is unverified.
- "Bundle exists" — without playthrough completion (#5 and #6), the bundle could be a 30-frame loop.
- "Audio plays" — without `render_audio` returning non-empty notes (#7), the slot may be empty.
- **Adjusting milestones to fit** — if the game can't reach WIN by the planned frame, fix the game, not the milestone. Backward edits to PLAN.md require re-running #5 and #6.

**Loads from knowledge/:** `pixel-art.md` (rationale for hierarchy 2/2 and contrast threshold), `background.md` (rationale for H-balance ≥ 70% and quadrant density). The gate also references PLAN.md (milestones), STRUCTURE.md (constants), and ASSETS.md (sprite identity contract) as project-specific artifacts.

## 8. Reference files

### 8.1 quirks.md

Carry forward from v3 with **curation under godogen's size-discipline rule** (see §6.9). The file opens with the discipline note from godogen, ported verbatim:

> Keep this file small and high-signal. Each item below has bitten real implementations and shows up as ambiguous bugs.
>
> Inclusion rule: Add only repeated, non-obvious issues that would have prevented real confusion in `scaffold`, `asset-gen`, `task-execution`, `capture`, or any `knowledge/` file. If an item is already in `pyxel-mcp`'s `instructions.md` Error Recovery section, it does not belong here. If it is answerable by `pyxel://api-reference`, it does not belong here.

Items below are the v3 carry-forward set with redundant entries pruned. Each is a real Pyxel gotcha that has bitten implementations:

- Coordinates: (0,0) top-left, Y-down.
- `pyxel.cls` first in draw.
- Draw order is paint order.
- `blt` without `colkey` makes transparent color opaque.
- Negative w/h flips.
- `pyxel.sin/cos` take degrees.
- `btnp` vs `btn`.
- Image bank: `set` before `pyxel.run`.
- Tilemap (0, 0) trap.
- 4 audio channels; BGM ch0–2, SE ch3; SE volume 5–7; noise tone too quiet over BGM.
- `pyxel.gen_bgm` first 4 args required.
- MML volumes V0-V100 vs `set()` API 0-7.
- Headless `SDL_AUDIODRIVER=dummy`.
- Animation: `frame_count // 4 % 2` not `frame_count % 2`.
- `inspect_state` does not auto-expand deep nesting.
- `pyxel.quit()` requests exit; in 2.8+ does not force-exit.

### 8.2 test-harness.md

Carry forward from v3 with simplification. Called from task-execution. Contains:

- Win-path execution (build input schedule from PLAN.md table; `play_and_capture` with milestone frames; `inspect_state` per milestone).
- Lose-path execution (typically empty inputs; observe lives decrement; assert GAME_OVER at final milestone).
- Stall and crash monitoring (state hash unchanged → FAIL; exception trace → FAIL).
- Closed-loop steering for paths > 200 frames.

### 8.3 capture.md

Carry forward from v3. Called from task-execution at end and from quality-gate for the bundle check.

- Bundle structure: `screenshots/result/<N>/` with win-path.gif, lose-path.gif, frames/, audio/, notes.md.
- Win-path GIF requirements: full duration showing traversal, ends on WIN.
- Lose-path GIF requirements: shows hazard hitting player, ends on GAME_OVER.
- Frame snapshots at scene transitions.
- Audio rendering per audio manifest entry.
- notes.md template.

## 9. Migration: existing v3-era artifacts

### 9.1 pyxel-skill repo (`/Users/takashi/repos/pyxel-skill`)

Current state on `feat/harness` branch:
- Modified: `SKILL.md` (v3-era draft).
- Untracked: 10 `.md` files (visual-target, decomposer, scaffold, asset-planner, asset-gen, task-execution, test-harness, capture, quality-gate, quirks).

**Decision:** Reset `feat/harness` to clean state, then re-write per this v5 spec via the writing-plans skill. v3 content is **mined** for Pyxel-specific knowledge (risk taxonomy, sprite identity heuristics, scene SM, quirks list) but the file structure and many headers change.

**Rationale:** v3's structural assumptions (9 stages, 5 state files, Tier 1/2/3 gate) diverge enough from v5 that incremental editing is more error-prone than re-write with reference to v3 as source material.

**Procedure:**

```bash
# 1. From feat/harness with the v3-era files (10 untracked + modified SKILL.md), archive.
git checkout -b archive/v3-drafts
git add SKILL.md visual-target.md decomposer.md scaffold.md \
        asset-planner.md asset-gen.md task-execution.md \
        test-harness.md capture.md quality-gate.md quirks.md
git commit -m "archive: v3-era draft files for reference"

# 2. Switch to a clean working branch off main.
git checkout main
git checkout -b feat/harness-v5

# 3. Apply v5 spec via writing-plans → executing-plans.
```

The branch `feat/harness` itself can be deleted after archiving (`git branch -D feat/harness`); it is not the working branch for v5.

**Why explicit archive:** `git stash` does not preserve untracked files by default (`-u` would, but interleaves with reset state). Explicit commit on a dedicated branch makes v3 content recoverable indefinitely.

**v3 → v5 rename map** (when the writing-plans phase carries forward content from v3 archive):

| v3 reference                              | v5 destination                                                |
|-------------------------------------------|---------------------------------------------------------------|
| `REFERENCE.md` Window contract            | `STRUCTURE.md` "Vision → Window contract" subsection          |
| `REFERENCE.md` Palette budget             | `STRUCTURE.md` "Vision → Palette budget" subsection           |
| `REFERENCE.md` Layout map                 | `STRUCTURE.md` "Vision → Layout" subsection                   |
| `REFERENCE.md` Object enumeration         | `ASSETS.md` `## Sprites` plus identity contract               |
| `REFERENCE.md` HUD                        | `STRUCTURE.md` "Vision → HUD" subsection                      |
| `REFERENCE.md` Audio cues                 | `STRUCTURE.md` "Vision → Audio" subsection (manifest restated in `PLAN.md` for gate consumption) |
| `REFERENCE.md` Win/lose conditions        | `PLAN.md` Win Path Milestones / Lose Path Milestones tables   |
| Tier 1 / 2 / 3 references in v3 quality-gate.md | Flat stop-conditions list in v5 `quality-gate.md` (this spec §7.7) |
| v3 anti-pattern referencing `REFERENCE.md`| Rewrite to reference `STRUCTURE.md` / `ASSETS.md` per the rows above |

### 9.2 pyxel-mcp `feat/quality-harness` worktree

Current state:
- v3-era design doc at `docs/superpowers/specs/2026-05-01-quality-harness-design.md` (commit 2789017).
- `skills/` directory with 10 markdown files (already moved to pyxel-skill repo).
- `_resources/skills.py` deleted (skill is not an MCP Resource).

**Decision:** Discard `feat/quality-harness` worktree. Cut a fresh `feat/v0.9.3-trim-instructions` branch from main for the concurrent pyxel-mcp work (§10).

**Rationale:** The worktree's design doc is v3-era and would need full rewrite. The skills/ duplication has already been consolidated into pyxel-skill. A clean branch from main is simpler than rebasing.

**Procedure:**
1. From `pyxel-mcp` main, `git worktree remove .worktrees/quality-harness`.
2. `git branch -D feat/quality-harness` (after confirming nothing valuable lives there).
3. `git checkout -b feat/v0.9.3-trim-instructions` for the §10 work.

## 10. Concurrent pyxel-mcp 0.9.3 changes

This work happens in parallel with pyxel-skill v0.1.0 development. Different branch, different release, different repo.

### 10.1 Trim `instructions.md`

The current 906-line `instructions.md` mixes tool catalog with design knowledge. Move design knowledge to `pyxel-skill/knowledge/`, retaining only the tool-doc parts. The migration is keyed by **markdown section heading** (resilient against future edits), not by line number.

**Keep in `pyxel-mcp` instructions.md (technical reference only):**

| Heading                                | Why keep                                             |
|----------------------------------------|------------------------------------------------------|
| `## Workflow`                          | Tool list with usage rules                           |
| `### Error Recovery`                   | Per-tool failure hints                               |
| `### Reading Tool Output`              | Per-tool result interpretation                       |
| `### Output Format`                    | Analysis / Suggestions sections                      |
| `### Testing Input-Dependent Logic`    | `play_and_capture` API docs                          |
| `### Debugging Game Logic`             | `inspect_state` API docs                             |
| `### Letting the User Play`            | Pyxel runtime invocation                             |
| `## Pyxel Reference`                   | URL list                                             |
| `## Pyxel Reference via MCP Resources` | Resource URI list                                    |
| `## Essential Tips`                    | Pure Pyxel API quirks                                |
| `### Pyxel 2.9 APIs Worth Knowing`     | API docs                                             |
| `### Beyond Defaults`                  | API extension table                                  |
| `### Audio Channel Management`         | **Trim:** keep technical `playm()` / `Channel()` notes; move BGM/SE allocation rationale to `knowledge/audio.md` |
| `### Tilemap Gotchas`                  | (0, 0) trap is a Pyxel API quirk                     |

**Move to `pyxel-skill/knowledge/`:**

| Heading                                | Target file                  |
|----------------------------------------|------------------------------|
| `### MML Composition Guide`            | `knowledge/audio.md`         |
| `### Quick BGM`                        | `knowledge/audio.md`         |
| `## Color Palette & Hierarchy` + `### 3-Layer Color Hierarchy` | `knowledge/pixel-art.md` |
| `## Pixel Art Rules` + all subsections (`### 3-Color-Per-Material Rule`, `### Outline Strategy`, `### Sprite Size Guidelines`, `### Anti-Patterns`, `### Sprite Design Process`, `### Sprite Sheet Organization`) | `knowledge/pixel-art.md` |
| `## Background Design` + `### Genre Background Recipes` + `### Parallax Scrolling` | `knowledge/background.md` |
| `## Screen & Text Layout` + `### Text Positioning` | `knowledge/background.md` |
| `## Title Screen Design`               | `knowledge/patterns.md`      |
| `## Visual Feedback` + `### Screen Shake` + `### Hitstop (Freeze Frames)` | `knowledge/game-feel.md` |
| `## Sound Effects Cookbook` + `### Jump` / `### Coin / Collect` / `### Hit / Damage` / `### Game Over` | `knowledge/audio.md` |
| `## Game Patterns` + `### Platformer` + `### Shooter (top-down / side-scroll)` + `### Scene Management` | `knowledge/patterns.md` |
| `### Level Design`                     | `knowledge/patterns.md`      |
| `### Enemy Design`                     | `knowledge/patterns.md`      |
| `## Game Feel Constants` + `### Platformer Physics` + `### Variable Jump Height` + `### Forgiveness Mechanics (Critical)` + `### Hitbox Design` + `### Camera (Side-Scroller)` | `knowledge/game-feel.md` |
| `## Animation Timing` + `### State-Based Animator` | `knowledge/patterns.md`      |
| `## Quality Checklist`                 | **Split:** `Code` / `Drawing` rows stay in instructions.md (tool/API anti-patterns); `Layout` / `Visual` / `Audio` / `Sprite` / `Level` rows move to the matching knowledge file |

After trim, instructions.md target length: ~200 lines (technical reference only).

> **Implementation note:** verify each section heading exists in the current `instructions.md` before moving (use `grep -nE '^#{2,4} '`). Future-proof migration scripts should match by heading text, not line number.

### 10.2 Cross-link

Add to instructions.md tail:

```markdown
## Beyond verification: production harness

For an end-to-end game-production workflow (architecture, sprite design,
gameplay logic, quality gating), see https://github.com/kitao/pyxel-skill —
a Claude Code Skill that drives this MCP server through a phased pipeline.
```

### 10.3 Version bump

- `pyproject.toml`: 0.9.3 (provisional — confirm with user per `feedback_versioning.md`).
- `server.json` (both occurrences): 0.9.3.
- `CHANGELOG.md`: new section.
  - "Move design knowledge to pyxel-skill (separate repo)."
  - "Trim instructions.md to technical reference."
  - "Add cross-link to pyxel-skill."

## 11. Implementation order

### 11.1 Sequencing

```
Step 1   pyxel-skill repo: discard v3 drafts, archive to a branch, init clean working tree.
Step 2   pyxel-skill: write SKILL.md (orchestrator).
Step 3   pyxel-skill: write 7 stage files in pipeline order.
Step 4   pyxel-skill: write 3 reference files (quirks, test-harness, capture).
Step 5   pyxel-skill: write 5 knowledge files. (Mine pyxel-mcp instructions.md plus retroactive lessons.)
Step 6   pyxel-skill: write hooks/ (stop_check_bundle.py, install.sh, README).
Step 7   pyxel-skill: write docs/ (architecture, dk-reference validation, compatibility-matrix). retrospectives/ stays empty until first run.
Step 8   pyxel-skill: write README, LICENSE.
Step 9   pyxel-mcp: cut feat/v0.9.3-trim-instructions, do §10 work.
Step 10  pyxel-mcp: ship 0.9.3 (so pyxel-skill's Required runtime is satisfied at validation time).
Step 11  pyxel-skill: end-to-end test against "make Donkey Kong" prompt; capture as docs/retrospectives/.
Step 12  pyxel-skill: tag v0.1.0.
```

Steps 1–8 are sequential within pyxel-skill but Step 9 can run in parallel.

Step 10 is the validation gate: if the harness fails to produce a clearable DK, do not ship. Iterate.

### 11.2 What "done with this spec" means

- Spec is reviewed by a critical subagent against the godogen reference (`/tmp/godogen`).
- Critical findings are addressed.
- User has reviewed and approved.
- writing-plans skill is invoked to convert this spec into a step-by-step implementation plan.
- subagent-driven-development is invoked to execute the plan.

This document is **not** the implementation plan; it is the design specification that the implementation plan derives from.

## 12. Open questions

These are flagged for user resolution before writing-plans:

1. **Skill name:** `pyxel` (the SKILL.md frontmatter `name`) or `pyxel-skill` (the repo / install path). The user-facing `/pyxel` skill activation needs the former; the repo and install path use the latter. Confirm convention.
2. **Skill name conflict with pyxel MCP server:** the user's global `~/.claude/.mcp.json` already registers the MCP server under `"pyxel"`. If SKILL.md frontmatter also uses `name: pyxel`, does Claude Code's skill router collide with the MCP namespace, or are the two distinct? Worth verifying before commit.
3. **Hook scope:** is the §4.6 Stop hook acceptable as a non-blocking warning, or should it block (refuse to allow Claude Code to terminate cleanly until the gate passes)? Non-blocking is recommended; user opinion needed.
4. **Versioning:** 0.1.0 for pyxel-skill, 0.9.3 for pyxel-mcp are placeholders per `feedback_versioning.md`. Confirm before tagging.
5. **MCP Registry / pyxel-skill discoverability:** Skills are not currently in any registry (Claude Code's `~/.claude/skills/` is local-install only). Is a documented install procedure in `pyxel-skill/README.md` sufficient for v0.1.0, with future packaging discussion deferred? (Pyxel MCP itself is in the Official MCP Registry, so the runtime side is handled.)
6. **Knowledge file count (5):** is this the final count, or do we anticipate splits as the skill matures (e.g., separate `knowledge/level-design.md`)? Five is the working target; deferring further split until empirical signal. Also: is there a per-file size budget (e.g., "no knowledge file exceeds 200 lines") to keep JIT loading cheap?
7. **Donkey Kong validation:** is DK the canonical validation prompt, or do we expect multiple validation prompts (DK, a shmup, a puzzle game)? `docs/validation/dk-reference.md` is the v0.1.0 canonical; others are future work.
8. **MCP namespace assumption:** the spec assumes the user registers pyxel-mcp under the name `"pyxel"` so tools are accessible as `mcp__pyxel__*`. If a user registers it under a different name, all tool references in the skill break. Should SKILL.md detect and fail loudly, or document the requirement and bail with a clear error?
9. **Pyxel engine version:** auto-memory pins Pyxel 2.8.7; pyxel-mcp's instructions.md references "Pyxel 2.9 APIs". Which is the canonical baseline for v0.1.0? `docs/compatibility-matrix.md` will record specific known-working pairs, but the skill's `Required runtime` block needs a concrete floor.

## 13. Risks

- **Spec drift between this doc and `docs/architecture.md`.** Mitigation: `docs/architecture.md` is generated from this spec at v0.1.0, then maintained separately. Spec is frozen at design time; architecture is the runtime contract.
- **Knowledge migration regression.** Moving 600 lines from `pyxel-mcp/instructions.md` to `pyxel-skill/knowledge/` risks losing content or breaking tool-doc references. Mitigation: section-name migration table in §10.1; manual diff of pre/post `instructions.md` for tool-doc completeness.
- **Hook permission friction.** Claude Code Stop hooks require user permission once. If denied, the skill silently loses its tripwire. Mitigation: install.sh prints clear rationale; hook README documents how to enable / disable.
- **Skill self-review weakness.** Per auto-memory: the agent is prone to self-review shortcuts. Mitigation (already in the user instructions): use a dedicated reviewer subagent with godogen explicitly referenced; user review after Critical issues are addressed.
- **`inspect_layout` text dependency.** §7.7 #11 routes the layout-balance check to TITLE scene because `inspect_layout` is text-centric and may produce unstable balance metrics on text-less PLAY scenes. If the chosen game has no text on its TITLE either (e.g., logo-only), the check needs another strategy. Mitigation: secondary `inspect_screen` quadrant-density check for PLAY; document fallback in `quality-gate.md`.
- **Frame-rate ambiguity in difficulty floor.** §7.7 #10 specifies 10–14 seconds; this maps to different frame counts at 30 vs. 60 fps. Mitigation: gate-report.json records the configured fps from STRUCTURE.md and the gate computes the frame-window threshold at run time; do not hardcode a frame count.
- **Pyxel engine version drift.** The skill targets Pyxel 2.8.7 / 2.9.x; an engine upgrade between v0.1.0 and the next release could break sprite formats, MML semantics, or tool output. Mitigation: `docs/compatibility-matrix.md` records pinned working ranges; CI (when added) tests against pinned versions.

## 14. References

- `htdt/godogen` source: `/tmp/godogen`. Particularly: `bevy/skills/godogen/SKILL.md` (orchestrator), `bevy/skills/godogen/decomposer.md` (risk taxonomy), `bevy/skills/godogen/task-execution.md` (loop shape), `shared/skills/godogen/asset-planner.md` (ASSETS.md format), `shared/hooks/stop_post_task_gate.py` (Stop hook shape).
- `pyxel-mcp` repo: `/Users/takashi/repos/pyxel-mcp`. Current `instructions.md`: `src/pyxel_mcp/instructions.md` (906 lines, the migration source for §10).
- `pyxel-skill` v3 drafts: `/Users/takashi/repos/pyxel-skill` on `feat/harness`. Source for Pyxel-specific knowledge (risk taxonomy, sprite identity heuristics, scene state machine, quirks).
- Auto-memory: `~/.claude/projects/-Users-takashi-repos-pyxel-mcp/memory/project_pyxel_skill_harness.md` (this project's session continuity), `~/.claude/projects/-Users-takashi-repos-pyxel-mcp/memory/feedback_versioning.md` (versioning policy).

---

End of spec.
