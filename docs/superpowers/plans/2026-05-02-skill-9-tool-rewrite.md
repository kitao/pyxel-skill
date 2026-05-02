# pyxel-skill 9-tool surface rewrite — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite pyxel-skill (currently `feat/harness-v5` carrying v0.1.0) so every tool invocation targets the new pyxel-mcp 0.10.0 9-tool surface. Production behavior (the 7 stages, 4 state files, anti-shortcut rules, hooks, knowledge index) is unchanged. The rewrite ships as pyxel-skill **v0.2.0**.

**Architecture:** Pyxel-mcp's 16 tools collapsed into 9. Most former tools are now snapshot kinds inside the `run` primitive. Stage files that called e.g. `run_and_capture + inspect_state + play_and_capture` separately are rewritten to issue a single `run` call with `inputs` + `state` + `screen_image` snapshots. Static inspectors (`validate`, `inspect_palette`, `inspect_image`, `inspect_animation`, `inspect_tilemap`, `pyxel_info`), the offline analyzer (`compare_frames`), and the audio renderer (`render_audio`) remain as standalone tools, with renamed/restructured arguments. Heavy stage files get an end-to-end rewrite; medium files get section-level rewrites; small/minimal files get targeted swaps.

**Tech Stack:** Markdown only. The harness behavior is enforced by pyxel-mcp 0.10.0 (already shipped in `/Users/takashi/repos/pyxel-mcp` on `feat/v0.9.3-trim-instructions`, HEAD `9d76971`, 197 tests pass, **not yet on PyPI** — release happens after pyxel-skill rewrite + DK validation, judged by user).

---

## Tool-name mapping (lookup table for every rewrite)

| Old tool                         | New equivalent                                                            |
|----------------------------------|---------------------------------------------------------------------------|
| `validate_script <path>`         | `validate(script=<path>)`                                                  |
| `pyxel_info`                     | `pyxel_info()` (unchanged)                                                |
| `run_and_capture <path> --frames=N` | `run(script=<path>, frames=N, snapshots=[{"frame": N-1, "kind": "screen_image", "output": ...}])` |
| `inspect_state ... --frames=[A,B,C] --attrs=...` | one `run` call with `snapshots=[{"frames": [A, B, C], "kind": "state", "attrs": [...]}]` |
| `inspect_screen ... --frame=F`   | one `run` call with `snapshots=[{"frame": F, "kind": "screen_grid", "bbox": [...]}]` |
| `inspect_layout ... --frame=F`   | one `run` call with `snapshots=[{"frame": F, "kind": "layout"}]`           |
| `inspect_bank --image_index=I`   | `inspect_image(script=..., image=I)` (full bank by omitting `x/y/w/h`)     |
| `inspect_sprite --image_index=I --x= --y= --w= --h=` | `inspect_image(script=..., image=I, x=, y=, w=, h=)`        |
| `inspect_animation ... --frame_count=N` | `inspect_animation(script=..., image=I, x=, y=, w=, h=, region_count=N, direction=...)` |
| `inspect_palette`                | `inspect_palette(script=...)` (unchanged)                                 |
| `inspect_tilemap`                | `inspect_tilemap(script=..., tilemap=N)` (renamed args)                    |
| `play_and_capture --inputs=...`  | `run(script=..., frames=N, inputs=[{"frame": F, "buttons": [...]}], snapshots=[...])` |
| `record_gameplay --duration=N`   | `run(script=..., frames=N, inputs=[...], snapshots=[{"kind": "video", "start_frame": 0, "end_frame": N, "fps": 30, "output": ...}])` |
| `capture_frames --frames="A,B,C" --scale=N` | one `run` call with `snapshots=[{"frames": [A, B, C], "kind": "screen_image", "output_pattern": "frame-{frame}.png", "scale": N}]` |
| `render_audio --sound_index=N --output_wav_path=...` | `render_audio(script=..., target={"sound": N}, output_path=...)` (target dict required, exactly one of sound/music) |
| `render_audio --music_index=N --output_wav_path=...` | `render_audio(script=..., target={"music": N}, output_path=...)` |
| `compare_frames`                 | `compare_frames(frame_a=..., frame_b=...)`                                |

**Multi-frame `frames` semantics (spec §6.6):** the value is `list[int]` or a Python-range string `"start:end[:step]"` or `"all"`. `output_pattern` accepts only the literal `{frame}` token (5-digit zero-padded); format specifiers like `{frame:03d}` and unknown tokens like `{name}` are validation errors.

**`render_audio` validation (spec §8.3):** `target` MUST contain exactly one of `"sound"` or `"music"`. Both, neither, or extra keys → validation error. Slot index must be a non-negative int. Empty slot returns success with `peak_amplitude: 0.0`, `notes: []`, plus a warning (the WAV is still written, silent).

---

## Reference patterns to lift across the rewrite

These are non-obvious patterns that several tasks reference. Defining them once here keeps the per-task steps from drifting.

### Pattern A — One `run` call covers smoke + milestones

The verify loop in `task-execution`, `quality-gate`, and `test-harness` collapses three old tools (`run_and_capture` + `inspect_state` + `play_and_capture`) into a single `run` invocation. Always include each frame the predicate references in the `state` snapshot's `frames` list. If a predicate compares `y[31] - y[30]`, both 30 and 31 must be in the snapshot list.

```python
run(
    script="main.py",
    frames=<one past final milestone>,
    inputs=<from PLAN.md milestone table>,
    snapshots=[
        # smoke: catches black screen / import failures
        {"frame": 5, "kind": "screen_image", "output": "tmp/smoke.png"},
        # milestones: every frame referenced by any predicate
        {"frames": [30, 31, 48, 60], "kind": "state",
         "attrs": ["scene", "player.y", "player.vy", "player.on_ground"]},
    ],
)
```

The `snapshots` are returned in input order, with the multi-frame `state` block expanded frame-ascending. Walk the result list and key each entry by its `frame` value to evaluate predicates.

### Pattern B — Console assertions (ASSERT PASS/FAIL) augment state snapshots

Per pyxel-mcp spec §6.7 (godogen-derived), scripts can write structured verification lines to stdout:

```python
# Inside the script:
if pyxel.frame_count == 360 and self.scene == "WIN":
    print("ASSERT PASS: win_path_complete")
if pyxel.frame_count == 30 and self.lives != 3:
    print(f"ASSERT FAIL: starting_lives | expected 3, got {self.lives}")
```

The harness parses these into `result["assertions"]`:

```python
[
    {"name": "win_path_complete", "passed": True, "message": None, "frame": None},
    {"name": "starting_lives", "passed": False,
     "message": "expected 3, got 2", "frame": None},
]
```

(In v0.10.0, `frame` is always `None` — frame-of-emission interleaving is deferred. The `name` and `passed` are the load-bearing fields.)

**Use `state` snapshots for agent-driven readouts (the agent decides what's correct). Use ASSERT lines for script self-checks (the script knows what's correct).** Both surface in the same `run` call's result. `quality-gate` and `task-execution` use both: state for predicate evaluation, assertions for "the script itself agrees the milestone landed."

### Pattern C — Closed-loop steering (canonical for pyxel-mcp)

Open-loop scripted inputs drift past ~200 frames. To correct course, **do not try to resume `run` from a mid-game state** — pyxel-mcp's subprocess isolation (spec §5.1) makes each `run` a fresh init. The canonical pattern is:

1. `result = run(script=..., frames=200, inputs=schedule_so_far, snapshots=[state at frame 199])`
2. Read observed state from `result["snapshots"]`.
3. Compute the next input segment from the observed state.
4. Issue a **new** `run` call with the **cumulative** input schedule from frame 0 to the next milestone, and observe again.

This differs from godogen, where Bevy's persistent `World` allows `Update`-loop continuation. Pyxel's global module state forces fresh subprocesses, so cumulative-replay is the trade-off — slower than continuation but deterministic.

For paths under ~200 frames, run open-loop with generous predicate tolerances and skip the segmentation.

### Pattern D — Multi-frame snapshot result keying

`result["snapshots"]` is a list. To find the entry for a specific frame:

```python
def snap_at(snapshots, frame, kind):
    return next(
        (s for s in snapshots if s["kind"] == kind and s["frame"] == frame),
        None,
    )

scene_at_30 = snap_at(result["snapshots"], 30, "state")["values"]["scene"]
```

Multi-frame snapshots expand into a contiguous run of N entries at the original input position, frame-ascending (spec §6.5). For complex result shapes, build a `{(kind, frame): snapshot}` index up front.

### Pattern E — MCP resource cross-links

Stage files reference `pyxel-mcp` resources for full schemas:

- `pyxel://run-snapshots-schema` — full schema for the 5 snapshot kinds (screen_image, screen_grid, state, layout, video) and the multi-frame syntax. **Read before constructing complex snapshot lists.**
- `pyxel://api-reference` — Pyxel engine API quick reference (placeholder until added).
- `pyxel://palette/default` — Pyxel default 16-color palette indices.
- `pyxel://examples/<name>` — bundled example scripts (e.g., `01_hello_pyxel`).

Each stage file's References block adds a line for `pyxel://run-snapshots-schema` so a fresh reader knows where the snapshot schema lives.

### Pattern F — Tilemap verification opportunity

Pyxel-mcp's `inspect_tilemap` returns `usage` (per-tile-coord counter), `bounding_box` (used cells), and `trap_warning` (true when tilemap uses `(0,0)` AND the source bank's `(0,0)` tile has visible content). The trap is a common Pyxel mistake — a sprite drawn at source `(0,0)` accidentally appears in every "empty" tilemap cell. v0.2.0 surfaces this in `quality-gate` as a stop condition; `asset-gen` documents it as part of the asset-bank discipline.

### Pattern G — Frame regression diff (compare_frames)

`compare_frames(frame_a=path_a, frame_b=path_b)` returns `identical: bool`, `changed_pixels: int | None`, `region: {...} | None`, `size_match: bool`. Two skill-relevant use cases:

1. **Stall detection**: capture two `screen_image` snapshots from the same `run` (e.g., frame 60 and frame 120) and compare. If `identical: True` despite scheduled inputs, the game is stalled.
2. **Re-attempt regression**: compare a frame from the previous bundle (`screenshots/result/<N-1>/`) to the current bundle's matching frame. Drift tells the user whether a fix moved things in the intended direction.

Plan applies use case 1 to `quality-gate` as an option for check #11, and use case 2 to `capture.md` anti-pattern guidance.

---

## File touch list

| File                              | Scope    | Primary intent                                                                  |
|-----------------------------------|----------|---------------------------------------------------------------------------------|
| `task-execution.md`               | heavy    | per-task 9-step loop fully re-illustrated; ASSERT augmentation; Pattern A/B/C  |
| `quality-gate.md`                 | heavy    | 12+1 stop-conditions table rewritten; tilemap trap added (#13); ASSERT support |
| `test-harness.md`                 | heavy    | win/lose milestone playthrough collapsed into one `run`; Pattern C clarified    |
| `asset-gen.md`                    | medium   | per-sprite verify uses `inspect_image`+`inspect_animation` (incl. direction guide) |
| `capture.md`                      | medium   | bundle composition uses `run` with `video`+`screen_image`; compare_frames option |
| `SKILL.md`                        | small    | runtime requirement → `pyxel-mcp ≥ 0.10.0`; capabilities block; **version v0.2.0** |
| `scaffold.md`                     | small    | 5-6 tool name swaps                                                             |
| `docs/architecture.md`            | small    | tool inventory updated to the 9-tool list                                       |
| `docs/validation/dk-reference.md` | small    | DK win/lose schedule wording (no concrete tool calls embedded — verified)       |
| `docs/compatibility-matrix.md`    | small    | new row for v0.2.0 + 0.10.0 + Pyxel 2.9.4; floor language updated               |
| `visual-target.md`                | minimal  | audit-only (no tool calls expected)                                             |
| `decomposer.md`                   | minimal  | example tool-call sketches in Verify rubric updated                             |
| `asset-planner.md`                | minimal  | mention of `inspect_palette` / `inspect_image` updated                          |
| `quirks.md`                       | minimal  | 3 stale tool-name references swapped                                            |
| `knowledge/*.md` (5)              | none     | design knowledge; no tool names                                                 |
| `hooks/*`                         | none     | bundle integrity check; no tool names                                           |

Sequence: branch + version bump → heavy → medium → small → minimal → cleanup → final verify.

---

## Phase 0: Branch and version bump

### Task 0.1: Create rewrite branch from `feat/harness-v5`

**Files:**
- Branch: new `feat/9-tool-rewrite` off `feat/harness-v5`

- [ ] **Step 1: Verify pyxel-skill repo is clean and on `feat/harness-v5`**

```bash
cd /Users/takashi/repos/pyxel-skill
git status
git branch --show-current
```

Expected: clean working tree, current branch `feat/harness-v5`.

- [ ] **Step 2: Snapshot the old-tool-name footprint**

```bash
grep -nE "run_and_capture|validate_script|inspect_state|inspect_screen|inspect_bank|inspect_sprite|inspect_layout|capture_frames|play_and_capture|record_gameplay" *.md docs/*.md docs/validation/*.md > /tmp/skill-old-tool-grep-before.txt
wc -l /tmp/skill-old-tool-grep-before.txt
```

Expected: ~70-90 hits across the 13 files.

- [ ] **Step 3: Create the rewrite branch**

```bash
git checkout -b feat/9-tool-rewrite
```

- [ ] **Step 4: No commit** — branching is the artifact.

### Task 0.2: Bump skill version label and pyxel-mcp floor in SKILL.md

This commit lands first so subsequent task commits can reference `v0.2.0` without ambiguity. The version label is final — if user later requests a different label, that's a single late-stage rename commit, not a re-prefixing of the whole branch.

**Files:**
- Modify: `/Users/takashi/repos/pyxel-skill/SKILL.md`

- [ ] **Step 1: Read SKILL.md frontmatter and Required runtime block**

The frontmatter currently has `name`, `description`, `license`. Check whether a `version` field exists. The Required runtime block currently lists pyxel-mcp's floor.

- [ ] **Step 2: Update Required runtime block to `pyxel-mcp ≥ 0.10.0`**

Find the line listing the pyxel-mcp floor (usually `pyxel-mcp ≥ 0.9.3` or similar) and update to `pyxel-mcp ≥ 0.10.0`. If the block does not currently pin a floor, add one.

- [ ] **Step 3: Add `version: 0.2.0` to frontmatter** (if no version field exists) or update the existing version field from `0.1.0` to `0.2.0`.

- [ ] **Step 4: Commit**

```bash
git add SKILL.md
git commit -m "chore(0.2.0): bump skill version and pyxel-mcp floor for 9-tool rewrite"
```

The capabilities-block updates (adding `mcp__pyxel__run` etc.) come in Task 3.1. Keep this commit minimal — version + floor only.

---

## Phase 1: Heavy rewrites

Each heavy file gets a near-end-to-end rewrite. The rewrite preserves the file's sections, anti-shortcut rules, and pedagogy, but every concrete tool invocation is replaced with the 9-tool equivalent. The skill's structural shape (Inputs / Outputs / Loop / Anti-patterns / When done) is retained — what changes is the inside of each example.

### Task 1.1: Rewrite `task-execution.md`

**Files:**
- Modify: `/Users/takashi/repos/pyxel-skill/task-execution.md` (currently ~152 lines)

- [ ] **Step 1: Read the current file end-to-end**

Hold the structure: Inputs, Outputs, References, Per-task loop, Worked example, Phases, Visual primacy, When-to-consult, Anti-shortcut rules, Closed-loop input, Per-task checklist, MEMORY.md, Stop hook, Anti-patterns, When done. These section headers stay.

- [ ] **Step 2: Update the References block (currently L19-28)**

Two updates:

(a) Replace the L23 line about `test-harness.md`:

```
- `test-harness.md` — milestone playthrough via a single `run` call with scheduled `inputs` + per-milestone `state` snapshots. Read before win/lose-path runs.
```

(b) Add a new bullet pointing to the pyxel-mcp resource:

```
- `pyxel://run-snapshots-schema` (MCP resource) — full schema for the 5 snapshot kinds (screen_image, screen_grid, state, layout, video) and multi-frame syntax. Read before constructing complex snapshot lists.
```

- [ ] **Step 3: Rewrite the Per-task loop (currently L30-42)**

Steps 5, 6, 7 currently call `validate_script`, `run_and_capture`, then `play_and_capture` + `inspect_state` as separate tools. Collapse into:

```
5. **`validate` clean.** Catches syntax errors and Pyxel anti-patterns before runtime.
6. **One `run` call covers smoke + milestone verification (Pattern A).** Build a `snapshots` list with: (a) `{"frame": K, "kind": "screen_image", "output": "tmp/smoke.png"}` at one early frame to catch black-screen / import failures, and (b) one multi-frame `{"frames": [...], "kind": "state", "attrs": [...]}` covering every frame the task's predicates reference. Pass the task's input schedule via `inputs`. The single call returns `snapshots`, `assertions`, `exit_status`, and `log` — read them all.
7. **Evaluate the task's Verify predicates against the returned snapshots and assertions.** Each Verify clause maps to either (a) a `state` snapshot value at a specific frame, or (b) a named ASSERT in `result["assertions"]` (Pattern B). For complex tasks, use both: state for the agent's predicate evaluation, ASSERT for the script's self-check. If the script-side ASSERT disagrees with the agent-side predicate evaluation, that's a divergence — investigate before declaring PASS.
```

- [ ] **Step 4: Rewrite the Worked example (currently L44-59)**

```
PLAN.md task: *"Player jumps reach height H_JUMP=24px in 18 frames; falling resumes after frame 18; landing on platform clears `vy`."*

Verify: a single `run` call drives the script through 60 frames with `KEY_SPACE` pressed at frame 30, capturing `state` at frames 30, 31, 48, 60.

```python
# In your stage script (or directly via the MCP client):
run(
    script="main.py",
    frames=60,
    inputs=[
        {"frame": 30, "buttons": ["KEY_SPACE"]},
        {"frame": 32, "buttons": []},
    ],
    snapshots=[
        {"frame": 5, "kind": "screen_image", "output": "tmp/smoke-f5.png"},
        {"frames": [30, 31, 48, 60], "kind": "state",
         "attrs": ["player.y", "player.vy", "player.on_ground"]},
    ],
)
```

The `state` block expands to 4 entries with frames 30, 31, 48, 60. Use Pattern D to key by frame:

```python
snaps = {(s["kind"], s["frame"]): s for s in result["snapshots"]}
y30 = snaps[("state", 30)]["values"]["player.y"]
y31 = snaps[("state", 31)]["values"]["player.y"]
y48 = snaps[("state", 48)]["values"]["player.y"]
y60 = snaps[("state", 60)]["values"]["player.y"]

assert y31 - y30 < 0           # jumping
assert abs(y48 - y31 - (-24)) < 2   # peak around -24px
assert y60 >= y31              # landed
```

(Optional augmentation per Pattern B: have the script `print("ASSERT PASS: jump_lands")` once `on_ground` becomes True after frame 31. The agent then sees both the predicate result AND the script's self-confirmation in `result["assertions"]`.)
```

- [ ] **Step 5: Rewrite Visual primacy (currently L67-75)**

Replace `inspect_screen at that exact frame` with `a `run` call snapshotting `screen_grid` at that frame`. Replace `inspect_state` with `a `state` snapshot inside `run``. Replace `play_and_capture` with `run` with `inputs`. The three concrete divergence cases (player not at (40,100); score==0; ladder stuck) stay — only the witness mechanism changes. End the section by saying: "`screen_grid` and `state` snapshots inside `run` are the witnesses; the code is the suspect."

- [ ] **Step 6: Rewrite Anti-shortcut rules (currently L86-92)**

Update tool refs (`validate_script` → `validate`, `play_and_capture` → `run` with `inputs`, `inspect_state` → `run` with `state` snapshot). Keep the 5 rules themselves. Add a 6th if it strengthens script-side discipline:

```
- **Don't replace ASSERT lines with comments.** If the script writes `print("ASSERT PASS: ...")` to confirm a milestone, removing the print to "clean up" silently breaks Pattern B verification. Either keep the ASSERT or migrate to an explicit `state` snapshot agent-side.
```

- [ ] **Step 7: Rewrite Closed-loop input simulation (currently L94-110)**

Use Pattern C verbatim from the Reference patterns section. Specifically: do NOT suggest `run_b = run(..., inputs_starting_from_observed_state, ...)` — that's not how pyxel-mcp's subprocess isolation works. Canonical is: read state from result A, compute next input segment, issue a new `run` from frame 0 with the cumulative input schedule. Mention that this differs from godogen (Bevy persistent World) and is a deliberate engine-shape trade-off.

- [ ] **Step 8: Update Per-task checklist (currently L112-122)**

Update bullets:
- `validate_script` → `validate`
- `run_and_capture` → "one `run` call with smoke screen_image + milestone state snapshots"
- The `verified by:` note format updates: `verified by: run frames=420, state snapshot at frame 419 → scene=WIN, score=12000`. If the task uses ASSERT lines, also include the assertion summary: `verified by: run frames=420, state snapshot frame 419 → scene=WIN; assertions: win_path_complete=PASS`.

- [ ] **Step 9: Update Anti-patterns (currently L137-144)**

`play_and_capture, inspect_state, render_audio` → `run for state and screen, render_audio for audio`. Otherwise unchanged.

- [ ] **Step 10: Verify no old tool names remain in this file**

```bash
grep -nE "run_and_capture|validate_script|inspect_state|inspect_screen|inspect_bank|inspect_sprite|inspect_layout|capture_frames|play_and_capture|record_gameplay" task-execution.md
```

Expected: no output (exit 1).

- [ ] **Step 11: Verify the file still flows coherently**

Read the rewritten file end-to-end. Section headings unchanged. Length should be similar (~150-170 lines). The Worked example must use Pattern A (single `run`), Pattern B (assertions), Pattern D (snapshot keying).

- [ ] **Step 12: Commit**

```bash
git add task-execution.md
git commit -m "feat(0.2.0): rewrite task-execution.md for 9-tool surface (Pattern A/B/C/D)"
```

### Task 1.2: Rewrite `quality-gate.md`

**Files:**
- Modify: `/Users/takashi/repos/pyxel-skill/quality-gate.md` (currently ~132 lines)

The 12-row stop-conditions table grows to 13 rows (added: tilemap trap warning per Pattern F).

- [ ] **Step 1: Read the current file end-to-end**

Hold the structure: Inputs, Output, Order of execution, Stop conditions table (12 → 13 rows), Difficulty-floor frame window, gate-report.json schema, Anti-shortcut rules, On FAIL, Common FAIL patterns, When PASSes.

- [ ] **Step 2: Update Inputs and Order-of-execution sections (currently L5-28)**

(a) Inputs block: add a bullet for `pyxel://run-snapshots-schema` (MCP resource) for snapshot field shapes the gate reads.

(b) Order-of-execution paragraph 3: replace `play_and_capture runs of the full win/lose path` with ``run` calls of the full win/lose path with `inputs` + `state` snapshots`.

- [ ] **Step 3: Rewrite the stop-conditions table (currently L30-45) — heaviest part**

Use exactly these replacements. (Row 13 is new.)

| # | Check | New `How` cell text |
|---|-------|---------------------|
| 1 | All four state files present | (unchanged — file-existence check) |
| 2 | Script validates | `validate(script="main.py")` returns `ok: True` (no syntax errors; anti-pattern warnings reviewed) |
| 3 | Smoke run | `run(script="main.py", frames=30, snapshots=[{"frame": 29, "kind": "screen_image", "output": "tmp/smoke.png"}])` returns `exit_status="ok"` and the PNG is non-empty |
| 4 | Asset identity | Per ASSETS.md entry: `inspect_image(script="main.py", image=0, x=, y=, w=, h=)` reports `len(color_count) ≥ ASSETS.md minimum` AND `0.15 ≤ fill_ratio ≤ 0.95`. For paired frames: `inspect_animation(script="main.py", image=0, x=, y=, w=, h=, region_count=2, direction=<"horizontal" or "vertical" per ASSETS.md bank layout>)` reports `region_diffs[0]["diff_ratio"]` in `0.05–0.50` |
| 5 | Win path | `run(script="main.py", frames=<final_milestone+1>, inputs=<PLAN.md win-path inputs>, snapshots=[{"frames": [<every milestone frame>], "kind": "state", "attrs": ["scene", ...]}])` returns: keying snapshots with Pattern D, the snapshot at the final milestone has `values["scene"] == "WIN"`. **Optionally also passes if `result["assertions"]` contains `{"name": "win_path_complete", "passed": True}`** (Pattern B augmentation, only meaningful if the script writes the ASSERT line) |
| 6 | Lose path | `run(script="main.py", frames=<final_milestone+1>, inputs=[{"frame":30,"buttons":["KEY_SPACE"]},{"frame":32,"buttons":[]}], snapshots=[{"frames": [<every milestone frame>], "kind": "state", "attrs": ["lives", "scene"]}])` returns: snapshot at final milestone has `values["scene"] == "GAME_OVER"`. Optionally augmented by `result["assertions"]` containing a `lose_path_complete` PASS |
| 7 | Audio renders | Per audio manifest entry: `render_audio(script="main.py", target={"sound": N}, output_path=...)` returns `notes` non-empty and `peak_amplitude` ≥ the manifest's minimum threshold (manifest threshold lives in ASSETS.md audio table). Same with `target={"music": N}` for BGM |
| 8 | Palette hierarchy | `inspect_palette(script="main.py")` returns `hierarchy.score == 2` |
| 9 | Contrast | `inspect_palette(script="main.py")` returns `len(contrast_warnings) ≤ 1` |
| 10 | Difficulty floor | (mechanism unchanged — same 10-14s band) but: `game_over_frame` is now extracted by Pattern D — find the `state` snapshot whose `values["scene"]` first equals `"GAME_OVER"` and read its `frame`. If no such snapshot exists, FAIL |
| 11 | Layout balance | TITLE: `run(script="main.py", frames=60, snapshots=[{"frame": 30, "kind": "layout"}])` returns `snapshots[0]["h_balance"] ≥ 0.70`. (Frame 30 lets the TITLE blink prompt and any intro animation settle.) For text-less PLAY scenes, fall back to `{"frame": F, "kind": "screen_grid"}` and assert that no quadrant of the returned `grid` is empty |
| 12 | Proof bundle | `screenshots/result/<N>/` directory exists with `win-path.gif`, `lose-path.gif`, `frames/`, `audio/` — see `capture.md` |
| **13** | **Tilemap trap clean** | **`inspect_tilemap(script="main.py", tilemap=N)` returns `trap_warning: False` for every tilemap declared in STRUCTURE.md. The trap fires when a tilemap uses tile `(0,0)` AND the source bank's `(0,0)` tile has visible content. Route to asset-gen if the source-bank `(0,0)` is non-empty; route to scaffold if the tilemap usage is wrong** |

The "FAIL routes to" column for row #13 is `asset-gen / scaffold`.

- [ ] **Step 4: Update the difficulty-floor code block (currently L47-56)**

```python
fps = int(structure_constants["FPS"])
lo, hi = int(10 * fps), int(14 * fps)
# Find the first state snapshot whose scene == "GAME_OVER" (Pattern D scan):
state_snaps = [s for s in run_result["snapshots"] if s["kind"] == "state"]
game_over_frame = next(
    (s["frame"] for s in state_snaps if s["values"].get("scene") == "GAME_OVER"),
    None,
)
result = "PASS" if game_over_frame is not None and lo <= game_over_frame <= hi else "FAIL"
```

- [ ] **Step 5: Update gate-report.json schema (currently L60-83)**

Add a 13th entry to the `checks` array example:

```json
{"id": 13, "label": "Tilemap trap clean", "result": "PASS"}
```

Update `summary.total` from `12` to `13` in both the example and any prose. The `summary.pass + summary.fail == summary.total` invariant should hold.

- [ ] **Step 6: Update Anti-shortcut rules (currently L88-96)**

- Bullet 2: `inspect_sprite` → `inspect_image`.
- Bullet 4: clarify `render_audio` signal: `notes` non-empty AND `peak_amplitude` above manifest threshold (not just notes).
- Add a bullet: **"`trap_warning: True` is a silent killer."** Tilemap (0,0) trap means every "empty" cell shows a sprite. The visual artifact is "stair-step pattern across empty space" — easy to miss in a small screenshot, fatal in a 256x256 tilemap. Check #13 catches it.

- [ ] **Step 7: Update Common FAIL patterns (currently L109-115)**

Add a row for #13 trap:

```
- **#13 trap_warning True.** Source-bank (0,0) has visible pixels and the tilemap uses (0,0). Route to asset-gen to clear source (0,0), or to scaffold to remap empty tilemap cells to a different tile coord.
```

- [ ] **Step 8: Verify no old tool names remain**

```bash
grep -nE "run_and_capture|validate_script|inspect_state|inspect_screen|inspect_bank|inspect_sprite|inspect_layout|capture_frames|play_and_capture|record_gameplay" quality-gate.md
```

Expected: no output.

- [ ] **Step 9: Commit**

```bash
git add quality-gate.md
git commit -m "feat(0.2.0): rewrite quality-gate; add tilemap trap as check #13"
```

### Task 1.3: Rewrite `test-harness.md`

**Files:**
- Modify: `/Users/takashi/repos/pyxel-skill/test-harness.md` (currently ~128 lines)

The biggest semantic change: the old version chained `play_and_capture` + `inspect_state` per milestone. The new version is a single `run` per path with the milestone frames listed in a multi-frame `state` snapshot.

- [ ] **Step 1: Read the current file end-to-end**

Hold structure: What to run, Win-path execution, Lose-path execution, Stall and crash monitoring, Closed-loop steering, Test fixture considerations, Anti-patterns, When done.

- [ ] **Step 2: Add a References block at the top (after the header paragraph)**

```
## References

- `pyxel://run-snapshots-schema` (MCP resource) — snapshot kind schemas and multi-frame syntax.
- `task-execution.md` — per-task verification (this file scales to whole-path verification).
```

- [ ] **Step 3: Rewrite "What to run" (currently L8-19)**

```
For each milestone table in `PLAN.md` (one for the win path, one for the lose path):

1. Build the input schedule from the table's `Inputs` column → `inputs: list[InputEvent]`.
2. Collect every milestone frame and every attribute referenced by the table's `Asserts` column.
3. Issue **one** `run` call (Pattern A) with `inputs` and one multi-frame `state` snapshot covering the milestone frames.
4. Optionally include script-side ASSERT lines (Pattern B) and read `result["assertions"]` for the script's self-check.
5. Aggregate per-milestone PASS/FAIL by walking `result["snapshots"]` (Pattern D) and evaluating each predicate against the captured value.
```

- [ ] **Step 4: Rewrite "Win-path execution" (currently L21-48)**

```
The win-path schedule is a sequence of inputs leading the player from start to goal. Translate the milestone table directly:

| Frame | Inputs (held until next row) | Asserts |
|-------|-----------------------------|---------|
| 30    | KEY_SPACE press             | scene == "PLAY" |
| 60    | KEY_RIGHT held              | player.x > start_x + 20 |
| 120   | KEY_UP at ladder            | player.y < floor_y - 8 |

becomes a single `run` call:

```python
run(
    script="main.py",
    frames=121,                    # one past the last milestone
    inputs=[
        {"frame": 30, "buttons": ["KEY_SPACE"]},
        {"frame": 32, "buttons": []},
        {"frame": 60, "buttons": ["KEY_RIGHT"]},
        {"frame": 120, "buttons": ["KEY_UP"]},
    ],
    snapshots=[
        {"frames": [30, 60, 120], "kind": "state",
         "attrs": ["scene", "player.x", "player.y"]},
    ],
)
```

After the call, walk `result["snapshots"]` (frame-ascending) and evaluate each predicate against the matching snapshot's `values`. Pattern D for the keying:

```python
snaps = {s["frame"]: s["values"] for s in result["snapshots"] if s["kind"] == "state"}
assert snaps[30]["scene"] == "PLAY"
assert snaps[60]["player.x"] > start_x + 20
assert snaps[120]["player.y"] < floor_y - 8
```
```

- [ ] **Step 5: Rewrite "Lose-path execution" (currently L50-70)**

```python
run(
    script="main.py",
    frames=601,
    inputs=[
        {"frame": 30, "buttons": ["KEY_SPACE"]},
        {"frame": 32, "buttons": []},
    ],
    snapshots=[
        {"frames": [120, 240, 360, 480, 600], "kind": "state",
         "attrs": ["lives", "scene"]},
    ],
)
```

Predicate: lives decrements monotonically across snapshots, and the snapshot at the largest frame has `scene == "GAME_OVER"`. If `scene` never reaches `"GAME_OVER"` by frame 600, FAIL with the same routing as before.

- [ ] **Step 6: Rewrite "Stall and crash monitoring" (currently L72-84)**

`run` already exposes the data this section needs:

- **Crash:** `result["exit_status"] == "crashed"` and `result["errors"]` carries the phase + traceback. The old `subprocess returncode` check is no longer needed.
- **Stall:** for v0.2.0 manual checking, compare two `state` snapshots N frames apart — if every observed attribute is identical despite scheduled inputs, the game has stalled. (Optionally: capture two `screen_image` snapshots and use Pattern G's `compare_frames` to confirm visual stall.) Pyxel-mcp also offers a built-in `run(stall_detection=True)` flag (spec §6.5) that sets `exit_status="stalled"` automatically — this is the canonical way for v0.2.0.
- **Frame budget:** `result["elapsed_seconds"] / frames` gives average per-frame ms. Same rule as before (>100ms → WARN, not FAIL).

- [ ] **Step 7: Rewrite "Closed-loop steering for paths > 200 frames" (currently L86-99)**

Use Pattern C verbatim. **godogen contrast note:** "godogen leverages Bevy's persistent `World` to resume an `Update` loop mid-game; pyxel-mcp's subprocess isolation (spec §5.1) precludes resume, so the canonical pattern is cumulative-replay from frame 0 with the union of all input segments. The trade-off is determinism over runtime cost — fresh subprocesses guarantee no leaked state between attempts."

End with: "For v0.2.0, open-loop with generous tolerances handles most win paths under 200 frames. Pattern C (cumulative-replay segmentation) is the escape hatch when a single open-loop schedule cannot be made deterministic."

- [ ] **Step 8: Rewrite "Test fixture considerations" (currently L101-109)**

```
Pyxel reads input via `pyxel.btnp` / `pyxel.btn`. The harness's `apply_to_pyxel` (called from `run`'s frame loop) drives Pyxel's set_btn / set_btnv API directly — production code does not need test-aware branching to be testable.

For frame-based logic that needs determinism (random spawn timing, particle scatter), `run` accepts `random_seed: int` which seeds Pyxel's RNG (`pyxel.rseed`) at the pre-loop checkpoint. Pass the same seed across re-runs for reproducible behavior:

```python
run(script="main.py", frames=600, random_seed=42, inputs=..., snapshots=...)
```
```

- [ ] **Step 9: Update Anti-patterns (currently L111-121)**

The four bullets reference `play_and_capture`'s input schedule. Replace with `run`'s `inputs` + `snapshots`. Keep the four anti-patterns themselves. Add a 5th if it strengthens Pattern A discipline:

```
- Snapshotting only the final milestone. The intermediate `state` entries cost nothing extra (one `run` call) and catch divergence early. Pattern D's snapshot-by-frame indexing makes intermediate entries cheap to read.
```

- [ ] **Step 10: Update "When this is done" (currently L123-128)**

Replace `play_and_capture` reference. Keep the routing back to task-execution → capture.md.

- [ ] **Step 11: Verify no old tool names remain**

```bash
grep -nE "run_and_capture|validate_script|inspect_state|inspect_screen|inspect_bank|inspect_sprite|inspect_layout|capture_frames|play_and_capture|record_gameplay" test-harness.md
```

Expected: no output.

- [ ] **Step 12: Commit**

```bash
git add test-harness.md
git commit -m "feat(0.2.0): rewrite test-harness.md for run-with-state-snapshots; clarify closed-loop"
```

---

## Phase 2: Medium rewrites

### Task 2.1: Rewrite `asset-gen.md`

**Files:**
- Modify: `/Users/takashi/repos/pyxel-skill/asset-gen.md` (currently ~155 lines)

- [ ] **Step 1: Read the current file end-to-end**

- [ ] **Step 2: Add `pyxel://run-snapshots-schema` to the Inputs/References list at the top**

After the `knowledge/pixel-art.md` line, add:

```
- `pyxel://run-snapshots-schema` (MCP resource) — only relevant for `screen_image` outputs from any verify run; `inspect_image` returns its own self-contained schema.
```

- [ ] **Step 3: Rewrite the "Loop per asset" section (currently L17-33)**

Old per-asset bash block:
```bash
validate_script main.py
inspect_sprite main.py --image_index=0 --x=0 --y=0 --w=16 --h=16
```

New:
```python
validate(script="main.py")
inspect_image(script="main.py", image=0, x=0, y=0, w=16, h=16)
```

The semantic is identical. Note that `inspect_image` returns `pixels` only when the requested region's area ≤ 4096 (per spec §6.4.1's `_PIXEL_GRID_LIMIT` mirror in spec §7.2). For 16x16 sprites, pixels is included; for the full 256x256 bank, pixels is None.

- [ ] **Step 4: Rewrite "Sprite identity heuristics" (currently L35-42)**

```
- **Color region count.** `inspect_image` returns `color_count` as a dict mapping palette-index integer keys to pixel counts (or string keys after JSON serialization through MCP). Assert `len(color_count) >= min_distinct_colors` from ASSETS.md.
- **Bounding-box density.** `inspect_image` returns `fill_ratio` (non-zero pixels / total). Assert `0.15 <= fill_ratio <= 0.95`.
- **Frame pair diff.** For paired frames (`walk_1` / `walk_2`), call `inspect_animation`. The argument that controls "how many adjacent regions" is `region_count` (renamed from old `frame_count`); pair the count with `direction`:
  - `direction="horizontal"` if frames are laid out side-by-side (e.g., `walk_1` at (0,0), `walk_2` at (16,0))
  - `direction="vertical"` if frames stack (e.g., `walk_1` at (0,0), `walk_2` at (0,16))
  Read the layout from ASSETS.md before choosing. The result's `region_diffs[0]["diff_ratio"]` is the pair diff; assert `0.05 <= diff_ratio <= 0.50`. Do NOT compute the diff yourself.
- **Edge contrast.** Surfaces in `inspect_image`'s `warnings` list when an outlined sprite's perimeter palette is too close to the interior. Treat warnings as FAILs for outlined sprites.
```

- [ ] **Step 5: Rewrite the worked-example invocation (currently L70-77)**

```bash
validate(script="main.py")
inspect_image(script="main.py", image=0, x=0, y=0, w=16, h=16)
```

Expected output description (`color_count` keys ≥ 5, `fill_ratio` ≈ 0.45) is unchanged in semantic.

- [ ] **Step 6: Rewrite "Animation pairs" (currently L90-98)**

```python
inspect_animation(
    script="main.py",
    image=0,
    x=0, y=0, w=16, h=16,
    region_count=2,
    direction="horizontal",   # or "vertical" — match ASSETS.md bank layout
)
```

The `frame_count=2` argument is renamed `region_count=2`. Direction must be specified explicitly.

- [ ] **Step 7: Rewrite "End-of-stage verification" (currently L125-138)**

Whole-bank scan:

```python
inspect_image(script="main.py", image=0)
```

omits `x/y/w/h` to get the full bank. The result's `pixels` is `None` (256x256 = 65k > 4096), but `color_count` and `fill_ratio` give a useful summary. For per-pair diffs, same `inspect_animation` invocation as Step 6.

**New bullet — tilemap source-bank trap awareness (Pattern F):**

If ASSETS.md declares a tilemap (used in scaffold or task-execution), the source bank's `(0, 0)` tile must be empty (all palette index 0) — otherwise every "empty" tilemap cell shows visible content. This is `quality-gate.md` check #13. Verify by inspecting the (0,0) corner of the source bank:

```python
inspect_image(script="main.py", image=0, x=0, y=0, w=8, h=8)
# Assert: color_count keys == {0} (only background) and fill_ratio == 0.0
```

If non-zero pixels are at (0,0), move the offending sprite to a different bank location and update ASSETS.md.

- [ ] **Step 8: Update Anti-patterns (currently L141-147)**

- Bullet 1: `inspect_sprite` → `inspect_image`.
- Bullet 4: `validate_script` → `validate`.
- Bullet 5 (`inspect_animation`): keep tool name; emphasize `region_count` (not `frame_count`) and `direction` requirement.

- [ ] **Step 9: Update "When this stage is done" (currently L149-155)**

- `inspect_sprite` → `inspect_image`.
- `inspect_animation` arg `frame_count=2` → `region_count=2, direction="horizontal" or "vertical"`.
- `inspect_bank --image_index=0` → `inspect_image(script="main.py", image=0)`.
- Add a bullet: **"`inspect_image(image=0, x=0, y=0, w=8, h=8)` shows source-bank (0,0) is fully transparent (no tilemap trap)."**

- [ ] **Step 10: Verify no old tool names remain**

```bash
grep -nE "run_and_capture|validate_script|inspect_state|inspect_screen|inspect_bank|inspect_sprite|inspect_layout|capture_frames|play_and_capture|record_gameplay" asset-gen.md
```

Expected: no output.

- [ ] **Step 11: Commit**

```bash
git add asset-gen.md
git commit -m "feat(0.2.0): rewrite asset-gen for inspect_image/inspect_animation; add (0,0) trap check"
```

### Task 2.2: Rewrite `capture.md`

**Files:**
- Modify: `/Users/takashi/repos/pyxel-skill/capture.md` (currently ~139 lines)

- [ ] **Step 1: Read the current file end-to-end**

- [ ] **Step 2: Add a References block at the top of the file**

After the header paragraph, before "Bundle structure":

```
## References

- `pyxel://run-snapshots-schema` (MCP resource) — full schema for `video`, `screen_image`, `screen_grid`, `state`, `layout` snapshot kinds used in bundle production.
- `task-execution.md` — calls into this file for intermediate captures.
- `quality-gate.md` — gates final bundle existence (check #12) and assets (#4).
```

- [ ] **Step 3: Update the bundle structure block (currently L9-31)**

Directory tree stays the same (`win-path.gif`, `lose-path.gif`, `frames/`, `audio/`, `notes.md`). Update the trailing comments:

```
├── win-path.gif         — `run` `video` snapshot of full clear
├── lose-path.gif        — `run` `video` snapshot of full death
├── frames/
│   ├── title.png        — `run` `screen_image` snapshot
│   └── ...              (5 frames at TITLE, play_start, mid_game, win, game_over)
├── audio/
│   ├── bgm_ch0.wav      — render_audio per BGM channel (target={"music": N})
│   └── se_*.wav         — render_audio per SE manifest entry (target={"sound": N})
```

- [ ] **Step 4: Rewrite the L33-34 paragraph**

Old: "`record_gameplay` writes the GIFs; `render_audio` writes WAVs via its `output_wav_path` argument; `capture_frames` writes PNGs."

New: "A single `run` call per path writes the GIF (via a `video` snapshot) and the milestone frame PNGs (via a multi-frame `screen_image` snapshot) atomically. `render_audio` writes WAVs via its `output_path` argument."

- [ ] **Step 5: Rewrite GIF requirements (currently L36-52)**

```
## Win-path GIF requirements

- Duration: at least the full win-path scenario, typically 20–30 seconds at 30 fps = **600–900 frames**.
- Must show the player traversing from start to goal and ending on the WIN scene.
- Production: `run` `video` snapshot with `start_frame=0, end_frame=<frames>, fps=30, output="screenshots/result/<N>/win-path.gif"`. The `.gif` extension triggers PIL-based encoding (no ffmpeg dependency).
- A bundle whose first 5 seconds look right and then sits static for 20 seconds is FAIL — `compare_frames` between mid and late frames must show meaningful change (Pattern G).

## Lose-path GIF requirements

- Duration: at least until GAME_OVER triggers, typically **≥ 360 frames** (~12 s at 30 fps).
- Must show a hazard appearing, hitting the player, and `lives` decrementing on screen.
- Must end on the GAME_OVER scene.
- Production: `run` `video` snapshot, same shape as win-path with shorter `end_frame`.

For `.mp4` output, the harness falls back to GIF if ffmpeg is unavailable on PATH (spec §6.4.5) — emits a warning and rewrites the path to `.gif`. Either format is accepted by `quality-gate.md` check #12.
```

- [ ] **Step 6: Rewrite "Frame snapshots" (currently L54-60)**

```
Capture key scene transitions in the **same `run` call** that produces the GIF, so the inputs and frame timing are guaranteed to match. Add a multi-frame `screen_image` snapshot to the `snapshots` list:

```python
{
    "frames": [30, 90, 180, 360, 720],
    "kind": "screen_image",
    "output_pattern": "screenshots/result/1/frames/{frame}.png",
    "scale": 2,
}
```

The `{frame}` token expands to a 5-digit zero-padded integer (only this token is supported — `{frame:03d}` and unknown tokens are validation errors). After the run, the files are at `00030.png`, `00090.png`, etc. Rename to `title.png`, `play_start.png`, `mid_game.png`, `win.png`, `game_over.png` per the bundle layout, OR pre-name by issuing five separate single-frame `screen_image` snapshots with literal `output` paths (longer snapshot list, no rename).
```

- [ ] **Step 7: Rewrite "Audio rendering" (currently L62-69)**

```
For every audio cue declared in `ASSETS.md` (BGM channels and SE), render to WAV:

```python
render_audio(script="main.py", target={"sound": 10},
             output_path="screenshots/result/1/audio/se_jump.wav")
render_audio(script="main.py", target={"music": 0},
             output_path="screenshots/result/1/audio/bgm_ch0.wav")
```

The `target` dict must contain exactly one of `"sound"` or `"music"` (validation error otherwise). The result schema is unchanged: `peak_amplitude`, `notes`, `warnings`. Assert `peak_amplitude > 0` and `len(notes) > 0` per `quality-gate.md` check #7. An empty slot returns success with `peak_amplitude: 0.0`, `notes: []`, plus a warning — that's the gate-failing condition.
```

- [ ] **Step 8: Rewrite "Concrete invocations" block (currently L98-117)**

Old block has 5 separate tool calls. Replace with a unified pattern:

```python
# Win path: GIF + frames + state proof, all in one run
run(
    script="main.py",
    frames=720,
    inputs=<PLAN.md win-path inputs>,
    snapshots=[
        {"kind": "video", "start_frame": 0, "end_frame": 720, "fps": 30,
         "output": "screenshots/result/1/win-path.gif"},
        {"frames": [30, 90, 180, 360, 719], "kind": "screen_image",
         "output_pattern": "screenshots/result/1/frames/win-{frame}.png", "scale": 2},
        {"frame": 719, "kind": "state", "attrs": ["scene"]},
    ],
)

# Lose path: same shape, shorter frames, lose-path inputs
run(
    script="main.py",
    frames=480,
    inputs=[
        {"frame": 30, "buttons": ["KEY_SPACE"]},
        {"frame": 32, "buttons": []},
    ],
    snapshots=[
        {"kind": "video", "start_frame": 0, "end_frame": 480, "fps": 30,
         "output": "screenshots/result/1/lose-path.gif"},
        {"frame": 479, "kind": "state", "attrs": ["scene"]},
    ],
)

# Audio (script must run cleanly to populate sound slots first):
render_audio(script="main.py", target={"sound": 10},
             output_path="screenshots/result/1/audio/se_jump.wav")
render_audio(script="main.py", target={"music": 0},
             output_path="screenshots/result/1/audio/bgm_ch0.wav")
```

- [ ] **Step 9: Update Anti-patterns (currently L119-130)**

- Bullet 5 (compare_frames stall check): keep, args are unchanged. Reword to invoke Pattern G: "`compare_frames(frame_a=mid_frame_path, frame_b=late_frame_path)` returns `identical: True` only if pixels are bit-identical. For middle-of-bundle stall checks, capture two frames in the visually-active range and assert `identical: False`. (`region` is `None` when identical, so the check needs both `identical` and `size_match`.)"
- Add a bullet: **"Re-attempt regression checks (Pattern G)."** When iterating, compare a representative frame from the previous bundle (`screenshots/result/<N-1>/frames/mid_game.png`) to the same frame in the new bundle (`screenshots/result/<N>/frames/mid_game.png`). Drift confirms a fix moved things; identical pixels mean the fix did not change the visible state. Useful as a sanity check before running the full gate.

- [ ] **Step 10: Verify no old tool names remain**

```bash
grep -nE "run_and_capture|validate_script|inspect_state|inspect_screen|inspect_bank|inspect_sprite|inspect_layout|capture_frames|play_and_capture|record_gameplay" capture.md
```

Expected: no output.

- [ ] **Step 11: Commit**

```bash
git add capture.md
git commit -m "feat(0.2.0): rewrite capture.md bundle composition; add Pattern G regression check"
```

---

## Phase 3: Small touch-ups

### Task 3.1: Update `SKILL.md` capabilities block

**Files:**
- Modify: `/Users/takashi/repos/pyxel-skill/SKILL.md`

(Version bump and pyxel-mcp floor were committed in Task 0.2; this task only updates the capabilities block and any anti-shortcut wording.)

- [ ] **Step 1: Read the file**

- [ ] **Step 2: Update the capabilities check (currently L15-16)**

Old:
```
- `mcp__pyxel__pyxel_info` is callable.
- `mcp__pyxel__validate_script` is callable.
```

New:
```
- `mcp__pyxel__pyxel_info` is callable.
- `mcp__pyxel__validate` is callable.
- `mcp__pyxel__run` is callable.
```

The `run` check is essential — without it the skill cannot execute any milestone verification. Three checks total.

- [ ] **Step 3: Update Anti-shortcut rule 2 (currently L122)**

Old: "Trust media over code. A passing `validate_script` and `run_and_capture` only certify the script does not crash."

New: "Trust media over code. A passing `validate` and a non-crashing `run` only certify the script does not crash. They do not certify gameplay."

- [ ] **Step 4: Update Anti-shortcut rule 6 (currently L126)**

Old: "Closed-loop input only. Open-loop scripted input drifts past ~200 frames. Use `play_and_capture` with state observation between segments."

New: "Closed-loop input only. Open-loop scripted input drifts past ~200 frames. Issue `run` calls in segments per Pattern C (cumulative-replay), reading observed `state` snapshots between segments and recomputing the next input schedule from the actual position."

- [ ] **Step 5: Verify no old tool names remain**

```bash
grep -nE "run_and_capture|validate_script|inspect_state|inspect_screen|inspect_bank|inspect_sprite|inspect_layout|capture_frames|play_and_capture|record_gameplay" SKILL.md
```

Expected: no output.

- [ ] **Step 6: Commit**

```bash
git add SKILL.md
git commit -m "feat(0.2.0): update SKILL.md capability checks and anti-shortcut wording"
```

### Task 3.2: Update `scaffold.md`

**Files:**
- Modify: `/Users/takashi/repos/pyxel-skill/scaffold.md`

- [ ] **Step 1: Read the file**

- [ ] **Step 2: Replace `validate_script main.py` → `validate(script="main.py")`** (5-6 occurrences). The `validate(script=...)` form is the canonical syntax going forward.

- [ ] **Step 3: Replace `run_and_capture main.py --frames=30` → `run(script="main.py", frames=30, snapshots=[{"frame": 29, "kind": "screen_image", "output": "tmp/scaffold-smoke.png"}])`**.

- [ ] **Step 4: Verify no old tool names remain**

```bash
grep -nE "run_and_capture|validate_script|inspect_state|inspect_screen|inspect_bank|inspect_sprite|inspect_layout|capture_frames|play_and_capture|record_gameplay" scaffold.md
```

Expected: no output.

- [ ] **Step 5: Commit**

```bash
git add scaffold.md
git commit -m "feat(0.2.0): swap scaffold.md tool calls to validate/run"
```

### Task 3.3: Update `docs/architecture.md`

**Files:**
- Modify: `/Users/takashi/repos/pyxel-skill/docs/architecture.md`

- [ ] **Step 1: Read the file**

- [ ] **Step 2: Find any tool inventory / capability list** and replace with the 9-tool list:

```
- run (dynamic execution: scheduled inputs + snapshots — screen_image, screen_grid, state, layout, video — and console assertions)
- validate (static: 10 anti-pattern detectors)
- pyxel_info (discovery: versions, examples, resource URIs)
- inspect_palette (static)
- inspect_image (static, image bank region)
- inspect_animation (static, cross-region Jaccard)
- inspect_tilemap (static, with (0,0)-trap detection)
- render_audio (audio: sound or music slot to WAV)
- compare_frames (offline: pixel diff between two PNGs)
```

- [ ] **Step 3: Update any "as of pyxel-mcp X.Y.Z" version mention to `0.10.0`.**

- [ ] **Step 4: Verify**

```bash
grep -nE "run_and_capture|validate_script|inspect_state|inspect_screen|inspect_bank|inspect_sprite|inspect_layout|capture_frames|play_and_capture|record_gameplay" docs/architecture.md
```

Expected: no output.

- [ ] **Step 5: Commit**

```bash
git add docs/architecture.md
git commit -m "feat(0.2.0): update architecture.md tool inventory for 0.10.0"
```

### Task 3.4: Update `docs/validation/dk-reference.md`

**Files:**
- Modify: `/Users/takashi/repos/pyxel-skill/docs/validation/dk-reference.md`

The current dk-reference.md (~124 lines) is mostly **prose** and **markdown tables**; it does NOT embed concrete tool-call command lines. The known references to update:

- L100: "If `inspect_animation` reports a paired-frame diff outside 5–50% on any pair, gate check #4 FAILs."
- L102-107: "Quality gate expected output" mentions `quality-gate.md table` (12 checks).

- [ ] **Step 1: Read the file end-to-end (verify no concrete tool calls slipped in since the audit)**

```bash
grep -nE "validate_script|run_and_capture|inspect_state|inspect_screen|inspect_bank|inspect_sprite|inspect_layout|capture_frames|play_and_capture|record_gameplay" docs/validation/dk-reference.md
```

Expected: no output. (If hits exist, swap them per Tool-name mapping table.)

- [ ] **Step 2: Update L100 wording to clarify the new argument**

Old: "If `inspect_animation` reports a paired-frame diff outside 5–50% on any pair, gate check #4 FAILs."

New: "If `inspect_animation` (with `region_count=2`, `direction` matching the ASSETS.md bank layout) reports `region_diffs[0]['diff_ratio']` outside 0.05–0.50 on any pair, gate check #4 FAILs."

- [ ] **Step 3: Update L106 (gate-report.json expectation)**

Old: "`summary.pass` == 12, `summary.fail` == 0. All 12 checks individually PASS per the `quality-gate.md` table."

New: "`summary.pass` == 13, `summary.fail` == 0. All 13 checks individually PASS per the `quality-gate.md` table (12 original + #13 tilemap trap)."

- [ ] **Step 4: Verify**

```bash
grep -nE "run_and_capture|validate_script|inspect_state|inspect_screen|inspect_bank|inspect_sprite|inspect_layout|capture_frames|play_and_capture|record_gameplay" docs/validation/dk-reference.md
```

Expected: no output.

- [ ] **Step 5: Commit**

```bash
git add docs/validation/dk-reference.md
git commit -m "feat(0.2.0): align dk-reference with new gate count and inspect_animation args"
```

### Task 3.5: Update `docs/compatibility-matrix.md`

**Files:**
- Modify: `/Users/takashi/repos/pyxel-skill/docs/compatibility-matrix.md`

The current matrix (~35 lines) has one row: pyxel-skill 0.1.0 / pyxel-mcp 0.9.3 / Pyxel 2.8.7 / Python 3.14 (note: Python 3.14 is incorrect — `.venv` actually runs 3.12.13 per memory; fix this drift too).

- [ ] **Step 1: Read the file**

- [ ] **Step 2: Append a new row to the Matrix table**

Add below the existing 0.1.0 row:

```
| 0.2.0       | 0.10.0    | 2.9.4        | 3.12   | 2026-05-02    | DK                | 9-tool surface rewrite. Targets pyxel-mcp 0.10.0 (run/validate/9-tool surface). Pyxel 2.9.4. macOS Darwin 25.3.0. |
```

(Keep the 0.1.0 row intact — older toolchains may still need to know what worked together at v0.1.0.)

- [ ] **Step 3: Update the Floor / ceiling guidance section (L17-23)**

Replace these bullets:

- **pyxel-mcp floor:** `0.10.0` for pyxel-skill v0.2.0+ — required because v0.2.0 stage files target the 9-tool surface (`run`, `validate`, `inspect_image`, etc.). For pyxel-skill v0.1.x, the floor is the legacy `0.9.3` (16-tool surface).
- **Pyxel engine floor:** `2.9.4` for pyxel-skill v0.2.0+ — required by pyxel-mcp 0.10.0 (uses `set_btnv`, `pyxel.colors.append`, `pyxel.tilemaps[i].cls((0,0))`, `pyxel.flip()` for input ring, etc.). For v0.1.x, the legacy floor `2.8.7` still applies.
- **Python floor:** 3.10 — unchanged. (Note: the previous matrix row erroneously listed Python 3.14; the actual `.venv` runs 3.12.13.)

- [ ] **Step 4: Verify**

```bash
grep -nE "run_and_capture|validate_script|inspect_state|inspect_screen|inspect_bank|inspect_sprite|inspect_layout|capture_frames|play_and_capture|record_gameplay" docs/compatibility-matrix.md
```

Expected: no output. (The compatibility matrix should mention old tool names only as historical context for the v0.1.x row, not as the current matrix's authority.)

- [ ] **Step 5: Commit**

```bash
git add docs/compatibility-matrix.md
git commit -m "feat(0.2.0): add 0.2.0 row to compatibility matrix; update floors"
```

---

## Phase 4: Minimal touch-ups

### Task 4.1: Audit `visual-target.md`

**Files:**
- Modify (if any drift): `/Users/takashi/repos/pyxel-skill/visual-target.md`

- [ ] **Step 1: Read the file (controller pre-confirms zero hits)**

```bash
grep -nE "run_and_capture|validate_script|inspect_state|inspect_screen|inspect_bank|inspect_sprite|inspect_layout|capture_frames|play_and_capture|record_gameplay" visual-target.md
```

If the spec is right (text-only stage), there are zero hits and no edits are needed.

- [ ] **Step 2: If hits exist, swap to 9-tool equivalents** following Phase 3 patterns. If no hits, skip the commit.

- [ ] **Step 3: Commit if any change**

```bash
git add visual-target.md
git commit -m "feat(0.2.0): polish visual-target.md (no tool-name drift expected)"
```

If no edits, no commit.

### Task 4.2: Update `decomposer.md` Verify-rubric examples

**Files:**
- Modify: `/Users/takashi/repos/pyxel-skill/decomposer.md`

- [ ] **Step 1: Read the file**

- [ ] **Step 2: Locate the example tool-call sketches (currently L46-59)**

The current sketches use `inspect_state`, `play_and_capture`. Rewrite each as a `run` call with `inputs` + `state` snapshots. Keep them as **sketches** — pseudo-code is fine; the actual implementation lives in task-execution.md.

Example rewrite (L53-54):
- Old: `play_and_capture inputs that hold KEY_RIGHT for 60 frames, inspect_state at frames 20, 40, 60`
- New: `run with inputs holding KEY_RIGHT for 60 frames, state snapshot at frames [20, 40, 60]`

- [ ] **Step 3: Verify**

```bash
grep -nE "run_and_capture|validate_script|inspect_state|inspect_screen|inspect_bank|inspect_sprite|inspect_layout|capture_frames|play_and_capture|record_gameplay" decomposer.md
```

Expected: no output.

- [ ] **Step 4: Commit**

```bash
git add decomposer.md
git commit -m "feat(0.2.0): update decomposer Verify-rubric examples"
```

### Task 4.3: Update `asset-planner.md` example mentions

**Files:**
- Modify: `/Users/takashi/repos/pyxel-skill/asset-planner.md`

- [ ] **Step 1: Read the file**

- [ ] **Step 2: Replace `inspect_sprite` mentions (L48, L129, anywhere else) → `inspect_image`.** These are passive mentions (no actual invocation); just update the tool name in the prose.

- [ ] **Step 3: Replace `inspect_animation` argument-name in any inline example** (`frame_count` → `region_count`; add `direction` mention if the prose discusses bank layout).

- [ ] **Step 4: `inspect_palette` mentions need only minor wording — argument shape is unchanged.**

- [ ] **Step 5: Verify**

```bash
grep -nE "run_and_capture|validate_script|inspect_state|inspect_screen|inspect_bank|inspect_sprite|inspect_layout|capture_frames|play_and_capture|record_gameplay" asset-planner.md
```

Expected: no output.

- [ ] **Step 6: Commit**

```bash
git add asset-planner.md
git commit -m "feat(0.2.0): refresh asset-planner.md tool-name examples"
```

---

## Phase 5: Quirks update

### Task 5.1: Update `quirks.md` tool references

**Files:**
- Modify: `/Users/takashi/repos/pyxel-skill/quirks.md`

`quirks.md` documents Pyxel API behaviors — the underlying behaviors do not change. Only the references to old tool names need updating.

- [ ] **Step 1: Read the file**

- [ ] **Step 2: Update L31** (`play_and_capture` and `record_gameplay`)

Old:
```
- This is the entire reason `play_and_capture` and `record_gameplay`
```

New:
```
- This is the entire reason `run` (with `inputs` and a `video` snapshot)
```

- [ ] **Step 3: Update L51** if it changed wording (`render_audio` tool name unchanged, but the surrounding sentence may need adjusting). Check.

- [ ] **Step 4: Rewrite L54-60 (`inspect_state` does not auto-expand deep nesting)**

Old: "## `inspect_state` does not auto-expand deep nesting" + body referencing `inspect_state`.

New: "## `state` snapshots do not auto-expand deep nesting" + body referencing the `state` snapshot kind inside `run`. Same semantic: `attrs: None` returns top-level scalar primitives only; deep paths must be named explicitly via dotted/indexed strings (per pyxel-mcp spec §6.4.3).

- [ ] **Step 5: Verify**

```bash
grep -nE "run_and_capture|validate_script|inspect_state|inspect_screen|inspect_bank|inspect_sprite|inspect_layout|capture_frames|play_and_capture|record_gameplay" quirks.md
```

Expected: no output.

- [ ] **Step 6: Commit**

```bash
git add quirks.md
git commit -m "feat(0.2.0): retarget quirks.md tool refs to 9-tool surface"
```

---

## Phase 6: Cross-link audit and finalization

These are controller-driven tasks (whole-repo grep, link auditing, manual stage-flow read). Subagent dispatch is awkward because the verification spans multiple files; do these tasks inline.

### Task 6.1: Whole-repo grep for old tool names

**Files:**
- (verification only)

- [ ] **Step 1: Run the master grep**

```bash
cd /Users/takashi/repos/pyxel-skill
grep -rnE "run_and_capture|validate_script|inspect_state|inspect_screen|inspect_bank|inspect_sprite|inspect_layout|capture_frames|play_and_capture|record_gameplay" \
    --include="*.md" \
    .
```

Expected: no output (exit 1).

- [ ] **Step 2: If any hit appears in `knowledge/*.md` or `hooks/*.md`** — investigate. If a knowledge file mentions an old tool name in passing (e.g., quoting an example), update only the tool reference. Do not rewrite knowledge content.

- [ ] **Step 3: If any hit appears in `README.md`** — update README's quick-start tool references.

- [ ] **Step 4: Commit any leftover fixes**

```bash
git add <leftover files>
git commit -m "feat(0.2.0): final old-tool-name swaps across repo"
```

If no leftover, no commit.

### Task 6.2: Cross-link audit

**Files:**
- (verification only — may produce small fixes)

- [ ] **Step 1: List inter-stage links (both inline and reference-style)**

```bash
cd /Users/takashi/repos/pyxel-skill
# inline form: [text](path)
grep -rnE "\[.*\]\(\.?\./?[a-zA-Z_/-]+\.md(#[a-zA-Z0-9-]+)?\)" --include="*.md" . > /tmp/skill-internal-links-inline.txt
# reference form: [text][ref] ... [ref]: path
grep -rnE "^\[[a-zA-Z0-9_-]+\]:" --include="*.md" . > /tmp/skill-internal-links-refs.txt
```

- [ ] **Step 2: Spot-check 10 random links**

For each, confirm the target file exists and (if anchored) the heading exists in the target.

- [ ] **Step 3: Verify the new `pyxel://run-snapshots-schema` cross-links land**

```bash
grep -rnE "pyxel://run-snapshots-schema" --include="*.md" .
```

Expected: hits in at least `task-execution.md`, `quality-gate.md`, `test-harness.md`, `asset-gen.md`, `capture.md` (the 5 stage files where Phase 1/2 added the cross-link).

- [ ] **Step 4: Fix broken links inline; commit any fixes**

```bash
git commit -am "feat(0.2.0): repair stage-file cross-links"
```

If no fixes, no commit.

### Task 6.3: Manual stage-flow read

**Files:**
- (verification only)

- [ ] **Step 1: Read SKILL.md → visual-target → decomposer → scaffold → asset-planner → asset-gen → task-execution → quality-gate**

In sequence. Make sure the narrative flows: each stage's "When this is done" hands off cleanly to the next stage's "Inputs". No new contradictions introduced by the rewrite.

- [ ] **Step 2: Read test-harness.md and capture.md as references** — these are called from task-execution / quality-gate; verify the call sites in those files match the new patterns (Pattern A/B/C/D/E/F/G).

- [ ] **Step 3: Tilemap-trap discipline read**

Verify that asset-gen.md (Step 7), quality-gate.md (check #13), and quirks.md tell a consistent story about the (0,0) trap. Specifically:
- asset-gen.md: how to PREVENT the trap (don't draw at source (0,0)).
- quality-gate.md: how to DETECT the trap (`inspect_tilemap.trap_warning`).
- quirks.md: WHY the trap exists (Pyxel default tilemap initial value is (0,0)).

- [ ] **Step 4: ASSERT regime discipline read**

Verify that task-execution.md (Pattern B, Step 3, Step 4 worked example), quality-gate.md (rows #5/#6 augmentation), and the SKILL.md anti-shortcut rules tell a consistent story about ASSERT lines as a script-side self-check that augments agent-side state predicates.

- [ ] **Step 5: If any contradictions found, file a small fix commit**

```bash
git commit -am "feat(0.2.0): resolve stage-flow inconsistencies surfaced by manual read"
```

If no inconsistencies, no commit.

### Task 6.4: Final version label confirmation

**Files:**
- (no edits unless user requests label change)

The skill is on `feat/9-tool-rewrite` with all commits prefixed `feat(0.2.0):`. SKILL.md frontmatter has `version: 0.2.0` and pyxel-mcp floor `0.10.0` (Task 0.2). The compatibility matrix has the 0.2.0 row (Task 3.5).

- [ ] **Step 1: Confirm with user before any tag, push, or symlink update**

Per `feedback_release_approval.md`: do NOT push the branch, do NOT tag a release, do NOT alter `~/.claude/skills/pyxel` symlink target. The skill is "complete" only after end-to-end DK validation against the new mcp 0.10.0 + skill v0.2.0 combination, judged by the user.

- [ ] **Step 2: If user requests a different label** (e.g., v0.1.1, v1.0.0):

```bash
# Update SKILL.md frontmatter version field
# Update docs/compatibility-matrix.md row label
# Optionally rebase to rewrite commit messages (or leave as-is — labels in commit prefixes are advisory)
git commit -am "chore: rename skill version label to <NEW_LABEL>"
```

If the label stays `v0.2.0`, no action.

---

## Self-review checklist (run after writing the plan; do not skip)

**1. Spec coverage:** Walk pyxel-mcp spec §10's table row by row. Each file → covered by a Phase task or explicitly marked "no touch" with rationale.

- `SKILL.md`: Task 0.2 (version + floor) + Task 3.1 (capabilities + anti-shortcut) ✓
- `visual-target.md`: Task 4.1 (audit-only) ✓
- `decomposer.md`: Task 4.2 ✓
- `scaffold.md`: Task 3.2 ✓
- `asset-planner.md`: Task 4.3 ✓
- `asset-gen.md`: Task 2.1 ✓
- `task-execution.md`: Task 1.1 ✓
- `quality-gate.md`: Task 1.2 (12 → 13 checks) ✓
- `quirks.md`: Task 5.1 ✓
- `test-harness.md`: Task 1.3 ✓
- `capture.md`: Task 2.2 ✓
- `knowledge/*.md` (5): no touch (declared none in spec §10) ✓
- `hooks/*`: no touch (declared none in spec §10) ✓
- `docs/architecture.md`: Task 3.3 ✓
- `docs/validation/dk-reference.md`: Task 3.4 ✓
- `docs/compatibility-matrix.md`: Task 3.5 ✓

**2. Pattern coverage:**

- Pattern A (one `run` for smoke + milestones): Task 1.1, 1.2, 1.3, 2.2 ✓
- Pattern B (ASSERT augmentation): Task 1.1, 1.2, 1.3, SKILL anti-shortcut #6 ✓
- Pattern C (closed-loop steering): Task 1.1, 1.3 (consistent) ✓
- Pattern D (snapshot keying): Task 1.1, 1.2, 1.3, 2.1 ✓
- Pattern E (MCP resource cross-links): Task 1.1, 1.2, 1.3, 2.1, 2.2 ✓
- Pattern F (tilemap trap): Task 1.2 (#13), Task 2.1 (asset-gen step 7), Task 5.1 (quirks updates) ✓
- Pattern G (compare_frames regression): Task 1.3 (stall), Task 2.2 (re-attempt regression) ✓

**3. godogen capability mapping (spec §4.4) coverage:**

| godogen capability | skill activation |
|---|---|
| `cargo build/check` | Task 3.2 (validate everywhere) ✓ |
| `cargo run` smoke | Task 1.2 row #3 ✓ |
| Single screenshot | Task 1.1, 1.3 (screen_image snapshot) ✓ |
| Frame sequence | Task 2.2 (multi-frame screen_image) ✓ |
| Video (mp4/gif) | Task 2.2 (video snapshot) ✓ |
| Headless target | (harness internal — no skill-side action) ✓ |
| set_btn / set_btnv | Task 1.1, 1.3 (inputs) ✓ |
| Log reading | Task 1.1 Step 3 (`result["log"]`) ✓ |
| Visual verification | Task 2.2 (screen_image for agent visual review) ✓ |
| Asset inspection | Task 2.1 (inspect_image / inspect_animation / inspect_palette) ✓ |
| Tilemap inspection | Task 1.2 (#13), Task 2.1 (Step 7) ✓ — godogen-omitted, Pyxel adds |
| Audio | Task 1.2 row #7, Task 2.2 ✓ — godogen-omitted, Pyxel adds |
| Frame regression diff | Task 2.2 (anti-pattern + Pattern G), Task 1.3 (stall) ✓ |
| API docs (Resources) | Task 1.1, 1.2, 1.3, 2.1, 2.2 (cross-links to `pyxel://run-snapshots-schema`) ✓ |
| ASSERT PASS/FAIL | Task 1.1, 1.2, 1.3 (Pattern B) ✓ — godogen-derived, Pyxel adopts |

**4. Placeholder scan:** No "TBD" / "TODO" / "implement later" / "fill in details" — every step shows the exact text replacement or the exact grep command. Verify by `grep -nE "tbd|TODO|fill in|implement later" docs/superpowers/plans/2026-05-02-skill-9-tool-rewrite.md`.

**5. Tool-name consistency:** Every rewrite step uses tool names from the 9-tool surface (`run`, `validate`, `pyxel_info`, `inspect_palette`, `inspect_image`, `inspect_animation`, `inspect_tilemap`, `render_audio`, `compare_frames`). Old names appear only in the explicit "old → new" mapping table at the top of the plan and in `git diff` strings.

**6. Argument-name consistency:**
- `inspect_animation` uses `region_count` (not `frame_count`) and `direction` (explicit `"horizontal"` or `"vertical"`).
- `inspect_image` uses `image` (not `image_index`).
- `inspect_tilemap` uses `tilemap` (not `tilemap_index`).
- `render_audio` uses `target={"sound": N} | {"music": N}` (not separate `sound_index`/`music_index`); `output_path` (not `output_wav_path`).
- `run` top-level: `frames` is total int. `run.snapshots[i]`: `frame` (int) for single-frame; `frames` (list/string) for multi-frame. `inputs[i]`: `frame` (int) + `buttons` (list).

**7. Pattern D consistency:** Every Step that walks `result["snapshots"]` includes either an explicit Pattern D snippet or a reference to Pattern D. No step assumes positional indexing without documenting the intent.

---

## Execution choice

**Plan complete and saved to `docs/superpowers/plans/2026-05-02-skill-9-tool-rewrite.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — Dispatch a fresh subagent per task. Best fit because each task touches one file (Phases 1-5) and is self-contained. Phase 6 verification tasks run inline by the controller (whole-repo grep, link audit, stage-flow read).

**2. Inline Execution** — Execute tasks in this session using `superpowers:executing-plans`, batch execution with checkpoints.

**Which approach?**
