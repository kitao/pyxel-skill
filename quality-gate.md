# Stage 7: Quality Gate

Final acceptance check. PASS gates "done"; FAIL routes back to the phase that owns the failed check. The gate is the contract that prevents shortcut "done" declarations.

## Inputs

- `PLAN.md` (Stage 2) — milestone tables, win/lose-path inputs and frames.
- `STRUCTURE.md` (Stage 3) — `FPS` constant (used to compute the difficulty-floor frame window).
- `ASSETS.md` (Stage 4) — sprite identity contract (`color_count` minimum, `fill_ratio` band, paired-frame entries) and audio manifest.
- `MEMORY.md` — gotchas accumulated across phases.
- `screenshots/result/<N>/` — proof bundle from `capture.md` (win-path.gif, lose-path.gif, frames/, audio/).
- `knowledge/pixel-art.md` — rationale for hierarchy 2/2 and contrast threshold.
- `knowledge/background.md` — rationale for H-balance ≥ 70% and quadrant density.

## Output

`screenshots/result/<N>/gate-report.json` — structured PASS/FAIL per check, with `fail_route` for any FAIL row. The gate-report.json is the single source of truth for "did this attempt pass?". Do not declare done without it. `<N>` is the same bundle counter `task-execution` and `capture.md` produced — the gate writes its report inside the existing bundle directory rather than creating a new one.

## Order of execution

Run checks in numeric order:

1. **Structural (#1–#3)** — cheap, fail-fast. Rules out wholesale missing artifacts before spending tokens on `play_and_capture`.
2. **Asset (#4, #7–#9, #11)** — single tool calls per asset; cheap relative to playthroughs.
3. **Gameplay (#5, #6, #10)** — `play_and_capture` runs of the full win/lose path. Most expensive.
4. **Bundle (#12)** — verify `capture.md` produced the deliverable.

Stop and write gate-report.json with the FAIL even if later checks would have passed. Partial reports are valid input for routing — there is no benefit in running #5 and #6 when #2 or #3 has already failed.

## Stop conditions (flat list — all 12 must PASS)

| # | Check | How (concrete pyxel-mcp calls) | FAIL routes to |
|---|-------|--------------------------------|----------------|
| 1 | All four state files present | `os.path.exists` for `PLAN.md`, `STRUCTURE.md`, `ASSETS.md`, `MEMORY.md`; all non-empty | the owning phase (visual-target / decomposer / scaffold / asset-planner) |
| 2 | Script validates | `validate_script main.py` — clean (no syntax errors; anti-pattern warnings reviewed) | task-execution |
| 3 | Smoke run | `run_and_capture main.py --frames=30` returns non-empty image with no crash | scaffold / task-execution |
| 4 | Asset identity | Per ASSETS.md entry: `inspect_sprite` reports `len(color_count.keys()) ≥ ASSETS.md minimum` AND `0.15 ≤ fill_ratio ≤ 0.95`. For paired frames: `inspect_animation frame_count=2` reports per-frame pixel diff in 5–50%. The harness computes the diff automatically — no caller-side math | asset-gen |
| 5 | Win path | `play_and_capture` with PLAN.md win-path inputs reaches `scene == "WIN"` by the final-milestone frame | task-execution or PLAN.md |
| 6 | Lose path | `play_and_capture` with PLAN.md lose-path inputs (typically `KEY_SPACE` once at frame 30 to enter PLAY, then no further input — player stands still and is killed by hazards; exact schedule from PLAN.md "Lose Path Milestones" `Inputs` column) reaches `scene == "GAME_OVER"` by the final-milestone frame | task-execution or PLAN.md |
| 7 | Audio renders | Per audio manifest entry in ASSETS.md: `render_audio` returns non-empty notes with peak above the minimum threshold | asset-gen / scaffold |
| 8 | Palette hierarchy | `inspect_palette` reports `Hierarchy score: 2/2` | asset-planner / asset-gen |
| 9 | Contrast | `inspect_palette` low-contrast warnings ≤ 1 | asset-planner / asset-gen |
| 10 | Difficulty floor | Lose path triggers `GAME_OVER` within **10–14 seconds** at the configured fps (≈ 300–420 frames at 30fps; ≈ 600–840 frames at 60fps). Compute the frame window at run time from STRUCTURE.md `FPS` constant — do not hardcode | task-execution / decomposer |
| 11 | Layout balance | `inspect_layout` reports H-balance ≥ 70% on the **TITLE** scene (TITLE always has text and produces a stable balance metric). For text-less PLAY scenes, fall back to `inspect_screen` on a representative frame and assert that no quadrant is empty | scaffold |
| 12 | Proof bundle | `screenshots/result/<N>/` directory exists with `win-path.gif`, `lose-path.gif`, `frames/`, `audio/` — see `capture.md` for production rules | capture (in task-execution) |

## Computing the difficulty-floor frame window (#10)

Read `FPS` from STRUCTURE.md (commonly `30` or `60`). Compute the band:

```python
fps = int(structure_constants["FPS"])           # e.g., 30
lo, hi = int(10 * fps), int(14 * fps)            # 30fps → (300, 420); 60fps → (600, 840)
game_over_frame = play_and_capture_result["game_over_frame"]
result = "PASS" if lo <= game_over_frame <= hi else "FAIL"
```

Below the band → unfair (the player has no time to react). Above → the lose-path schedule isn't reliably triggering GAME_OVER, which means hazards or collision logic are too soft. Both route the same way, but fix the underlying cause — do not widen the band.

## gate-report.json schema

One row per check. The gate writes this file regardless of PASS/FAIL — it is the artifact the user reviews when the gate concludes.

```json
{
  "attempt": 1,
  "fps": 30,
  "checks": [
    {"id": 1, "label": "State files", "result": "PASS", "evidence": "all 4 files present"},
    {"id": 2, "label": "Validate", "result": "PASS"},
    {"id": 3, "label": "Smoke run", "result": "PASS", "evidence": "frame 30 captured, no crash"},
    {"id": 4, "label": "Asset identity", "result": "PASS"},
    {"id": 5, "label": "Win path", "result": "FAIL", "evidence": "scene at frame 660 = PLAY (expected WIN)", "fail_route": "task-execution"},
    {"id": 6, "label": "Lose path", "result": "PASS"},
    {"id": 7, "label": "Audio renders", "result": "PASS"},
    {"id": 8, "label": "Palette hierarchy", "result": "PASS"},
    {"id": 9, "label": "Contrast", "result": "PASS"},
    {"id": 10, "label": "Difficulty floor", "result": "PASS", "evidence": "GAME_OVER at frame 372 (12.4s @ 30fps, in 10–14s band)"},
    {"id": 11, "label": "Layout balance", "result": "PASS", "evidence": "TITLE H-balance 81%"},
    {"id": 12, "label": "Proof bundle", "result": "PASS"}
  ],
  "summary": {"pass": 11, "fail": 1, "total": 12}
}
```

The `fail_route` field is required on every FAIL row. PASS rows may omit `evidence` when the check is binary; FAIL rows must include enough evidence to act on.

## Anti-shortcut rules (restated for the agent at gate time)

These are the cheats the gate is built to catch. Read them before writing the gate-report.json:

1. **"It compiles and runs, looks fine"** — checks #2 and #3 only certify no-crash. They do not certify gameplay. Checks #5 and #6 are the gameplay certifications.
2. **"I added a sprite"** — without `inspect_sprite` matching the `represents` description from ASSETS.md, the sprite is unverified. Render, look, compare; check #4 enforces this.
3. **"Bundle exists"** — without playthrough completion (#5 and #6 PASS), the bundle could be a 30-frame loop with stale frames. Existence alone is not enough.
4. **"Audio plays"** — without `render_audio` returning non-empty notes (#7), the slot may be empty. A silent `play()` call passes #2 and #3 but fails #7.
5. **Adjusting milestones to fit** — *most important.* If the game can't reach WIN by the planned frame, fix the game, not the milestone. Backward edits to PLAN.md require re-running #5 and #6 from scratch. Loosening the spec to dodge a FAIL is the failure mode this gate exists to prevent.

## What happens on FAIL

For each FAIL row in gate-report.json:

1. Route to the phase named in the row's `fail_route` field. The phase reads its own state files plus the FAIL evidence and decides what to change.
2. Apply the remediation (fix the bug, redraw the sprite, re-tune the difficulty, regenerate the bundle). Update `MEMORY.md` if the fix is non-obvious — future sessions will need it.
3. Bump the bundle counter `<N>` and produce a fresh `screenshots/result/<N>/` per `capture.md`. Stale bundles are not patched in place.
4. Re-run the gate from check #1. **Do not retry the gate without remediation** — re-running the same checks against the same artifacts produces the same gate-report.json.

If multiple checks FAIL, route to the earliest-stage owner first (e.g., #4 asset-gen before #5 task-execution) — fixing upstream often resolves downstream failures. The gate is not a debugger; it tells you *which* phase owns the failure, not *what code* to change.

### Common FAIL patterns

- **#5 reaches PLAY but never WIN.** Win-trigger logic missing; route to task-execution.
- **#6 reaches PLAY and stays there past the lose-path window.** Collision/hazard logic too soft; route to task-execution.
- **#4 paired-frame diff < 5%.** Two frames are visually identical; route to asset-gen to redraw one.
- **#10 lose path < 10s.** Hazards spawn too aggressively; route to task-execution to slow spawn rate.
- **#11 H-balance < 70% on TITLE.** Title text is left- or right-weighted; route to scaffold to recenter.

## When this gate PASSes

All 12 checks PASS in gate-report.json. Then:

- `PLAN.md` shows all milestone rows marked `done` with verified-by notes.
- `MEMORY.md` has any non-obvious gotchas captured for next session.
- The latest `screenshots/result/<N>/` bundle is the deliverable, and `screenshots/result/<N>/gate-report.json` proves the bundle was accepted.

Report to the user (concise; the bundle and gate-report.json carry the detail):

- **Bundle path** — `screenshots/result/<N>/`. The user opens the GIFs and WAVs from there.
- **One-line summary** of what was implemented (game title, win condition, lose condition).
- **Any caveats** — known limitations, out-of-scope items deferred to a later attempt, anything the gate did not check.

Then stop. Done. Do not start the next iteration speculatively; if the user wants polish or a new feature, they will say so.
