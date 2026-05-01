# Stage 6: Task Execution

Implement gameplay logic against `PLAN.md` and `STRUCTURE.md`. Verify after every change. Move on only when the task's Verify predicates are met by observed state, not by inspection of the code.

## Inputs

- `PLAN.md` (from Stage 2) — Risk Tasks, Main Build tasks, Win/Lose milestones, Audio manifest.
- `STRUCTURE.md` (from Stage 3) — modules, scene state machine, tuning constants.
- `ASSETS.md` (from Stage 4 + 5) — sprite manifest with bank coordinates.
- `MEMORY.md` — gotchas accumulated so far.
- `main.py` — runnable skeleton with `_build_assets()` populated.

## Outputs

- `main.py` with all PLAN.md tasks implemented and verified.
- `PLAN.md` tasks marked done with one-line `verified by:` notes.
- `MEMORY.md` updated with any non-obvious gotcha discovered while implementing.

## References

Read these before invoking the corresponding tools:

- `test-harness.md` — milestone playthrough verification (`play_and_capture` + `inspect_state` aggregation). Read before win/lose-path runs.
- `capture.md` — intermediate captures and the final proof bundle. Read before producing any frames or GIFs that the gate will read.
- `quirks.md` — Pyxel gotchas (coords, `btnp` semantics, `colkey`, MML volume scaling). Read whenever Pyxel behaves unexpectedly.
- `knowledge/game-feel.md` — physics tuning (gravity, jump arcs), hitboxes vs sprite bounds, camera follow, screen shake, hitstop. Read before implementing player physics or hit feedback.
- `knowledge/audio.md` — SE-per-event policy, channel allocation (BGM ch0–2, SE ch3), MML volume mapping. Read before adding any sound trigger.
- `knowledge/patterns.md` — level/enemy archetypes, animation-frame timing (`frame_count // 4 % 2`). Read before implementing scrolling, spawn waves, or AI patterns.

## Per-task loop

For each task in `PLAN.md`:

1. **Read the task definition.** Confirm Verify criteria are observable (specific predicates against state values or scene transitions, not "looks fine"). If the Verify is vague — re-read `decomposer.md` and tighten PLAN.md before coding.
2. **Read `STRUCTURE.md`.** Identify which class / function gains the change. If no module owns this behavior, you skipped Stage 3 — go back.
3. **Read the current source.** Don't guess what's there.
4. **Implement the smallest change that makes the task observable.** One method, one constant, one behavior. No bundled "while I'm in there" edits.
5. **`validate_script` clean.** Catches syntax errors and Pyxel anti-patterns before runtime.
6. **`run_and_capture` at a relevant frame.** Sanity render. Catches import errors, infinite loops, obvious draw failures, or a black screen.
7. **Run the task's specific Verify procedure** — typically `play_and_capture` with the scripted inputs from PLAN.md plus `inspect_state` at the milestone frames named in the task.
8. **If FAIL** — read the captured state, find the divergence, fix. Don't move on. Don't lower the threshold. Don't retry the same input expecting a different result.
9. **If PASS** — update `PLAN.md` (mark task done with a one-line `verified by:` note pointing to the milestone frame and observed value), append to `MEMORY.md` if a non-obvious gotcha was discovered, commit.

## Worked example: one task end-to-end

PLAN.md task: *"Player jumps reach height H_JUMP=24px in 18 frames; falling resumes after frame 18; landing on platform clears `vy`."* Verify: `play_and_capture` with `KEY_SPACE` at frame 30, `inspect_state` at frames 31, 48, 60. Predicates: `y[31] - y[30] < 0`, `y[48] - y[31] ≈ -24` (peak), `y[60] >= y[31]` (landed).

```bash
# Step 4: edit Player.update() to add jump physics (one method change).
# Step 5:
validate_script main.py
# Step 6:
run_and_capture main.py --frames=60
# Step 7:
play_and_capture main.py --inputs='[{"frame":30,"down":["KEY_SPACE"]}]' --frames=60
inspect_state main.py --frames='[31,48,60]' --attrs='player.y,player.vy,player.on_ground'
```

Read the state output. If `player.y[48] - player.y[31] == -10` instead of ~-24, the jump curve is wrong — fix `JUMP_VY` or gravity, not the milestone frame. If `player.on_ground[60] == False`, the landing detection is broken — fix the collision check, not the predicate. Step 9 only runs once all three predicates hold.

## Phases

**Risk Slice.** Implement each PLAN.md risk task in isolation. Keep code small and contained — a risk task that needs three classes and a state machine is a sign the risk wasn't really isolated. Once the risk task passes its Verify, carry only the validated pattern (the single function, the single constant, the single approach) into Main Build. Don't carry forward speculative scaffolding.

**Main Build.** Everything else from PLAN.md. Lock scene ownership first (which class owns TITLE rendering, which owns PLAY update, etc., per STRUCTURE.md), then implement vertical slices: pick one feature, run it through draw + update + verify, before starting the next.

## Visual primacy

When the code says X happened but the capture shows Y, the capture is right. Don't argue with the pixels. Three concrete divergence cases:

- "I drew the player at (40, 100)" but the screenshot shows nothing at (40, 100). Probable causes: `colkey` makes the sprite invisible against background; the sprite is drawn but at a different layer ordering and is overdrawn; `pyxel.cls()` is called *after* the player's draw and erases it. Run `inspect_screen` at that exact frame and look at the palette indices around (40, 100); the truth is in the grid.
- "I incremented score on barrel-jump" but `inspect_state` at frame 150 shows `score == 0`. The collision check never fires; either the hitbox rectangle is wrong (bounds inverted, off-by-one) or the trigger condition has a strict-equality bug (`y == barrel.y` instead of `abs(y - barrel.y) < EPS`).
- "Mario climbs the ladder" but `play_and_capture` with `KEY_UP` shows Mario stuck. The climb-eligibility check has a strict bound (`x == ladder.x` instead of `ladder.x <= x <= ladder.x + ladder.w`), or `on_ladder` is set in `update()` *after* the input read.

In each case the fix is to look at observed state, not to re-explain the code. `inspect_state` and `inspect_screen` are the witnesses; the code is the suspect.

## When to consult each knowledge file

The references at the top of this stage are not all loaded for every task. Choose by what the current task touches:

- Implementing player movement, jump arcs, gravity, hit feedback, screen shake, hitstop, camera follow → read `knowledge/game-feel.md` *before* writing the constants. Tuning numbers in PLAN.md must agree with the heuristics there.
- Adding any sound trigger (jump, hit, death, score, scene transition) → read `knowledge/audio.md` for SE-per-event policy and channel allocation. SE volume below 5/7 will be inaudible over BGM.
- Implementing scrolling, parallax, enemy spawn waves, animation cycles, AI patterns → read `knowledge/patterns.md`. Animation timing follows `frame_count // 4 % 2`, not `frame_count % 2` — the latter flickers.
- Pyxel doing something unexpected at runtime → check `quirks.md` first. If the issue is not there, it's a project-specific bug → fix it and append to `MEMORY.md`.

## Anti-shortcut rules

- **No "looks fine".** Each Verify is a specific predicate against an observed value. If you cannot name the predicate, it is not a Verify — go fix PLAN.md.
- **Don't skip lose-path verification.** Win path is exciting; lose path is forgotten. Both must verify with `play_and_capture` and reach their target scene by the milestone frame.
- **Don't comment out failing assertions.** Fix the code.
- **Don't lower the threshold to make it pass.** If `lives reaches 0` doesn't happen by frame 360 in lose path, either barrels are too slow (PLAN.md is wrong → re-decompose) or collision is broken (code is wrong → fix). Don't move the milestone to frame 600.
- **Don't trust subprocess returncode alone.** A script can run cleanly and produce a black screen, no audio, frozen state. Always observe captured state — that's what `inspect_state` is for.

## Closed-loop input simulation

Open-loop input (timed press / release) drifts. Over 200+ frames the player position desyncs from the planned trajectory because of floating-point physics, frame-skip, and stochastic spawn timing. For long sequences, run `play_and_capture` in segments: at each milestone, read observed state, then compute the next input segment from the actual position rather than the planned one.

A second pattern, useful when input would have to thread a precise needle: temporarily replace input checks with state observation in a test fixture:

```python
# Production code:
if pyxel.btn(pyxel.KEY_UP) and self.on_ladder:
    self.y -= CLIMB_SPEED

# Deterministic test (in an instrumented build):
if self.test_target_y is not None and self.y > self.test_target_y:
    self.y -= CLIMB_SPEED
```

Design milestones around what state should be reached, not what input should have happened. See `test-harness.md` for the full segmented playthrough pattern.

## Per-task implementation checklist

Before marking a task done in PLAN.md:

- [ ] Code change is minimal and confined to the task's scope (no drive-by edits).
- [ ] `validate_script` clean.
- [ ] `run_and_capture` at a representative frame: no black screen, no obvious render bug.
- [ ] All Verify predicates from PLAN.md are observed in `inspect_state` / `play_and_capture` output.
- [ ] PLAN.md task marked done with a one-line `verified by:` note (e.g., `verified by: play_and_capture frames=420, scene=WIN, score=12000`).
- [ ] `MEMORY.md` updated if a gotcha was discovered (don't repeat yourself in the next task).

## What to record in MEMORY.md

`MEMORY.md` is the project-local log of gotchas — the file you'll thank yourself for in the next session. Append items only when they meet all three:

- Non-obvious (a fresh reader of `quirks.md` would not have predicted it).
- Project-specific (general Pyxel behavior belongs in `quirks.md`, not here).
- Cost more than 5 minutes to track down.

Format: one bullet, one or two sentences, with the symptom first and the fix second. Examples: `- Boss spawns at x=128 collide with HUD score text (also at x=128). Fixed: drew score at x=120.` Don't write a postmortem; one bullet is enough. The next session reader scans MEMORY.md before touching `task-execution`.

## Stop hook awareness

The Stop hook (`hooks/stop_check_bundle.py`) fires at session end and warns on a missing or incomplete proof bundle. **Do not** rely on it to enforce; you must run the gate (Stage 7) explicitly. The hook is a guardrail against accidental "I'm done" — it is not a quality gate.

## Anti-patterns in this stage

- **Implementing all tasks before verifying any.** Catch a bad pattern before propagating it across five tasks.
- **Skipping Risk Tasks for Main Build because Main Build is "easier".** Risk Tasks were isolated for a reason — bugs in them spread into Main Build with interest.
- **Editing physics constants mid-task.** If `JUMP_VY` changes, all jump-related milestones in PLAN.md need re-verification — and they probably already passed at the old value, so changing it now silently breaks them.
- **Adding new features mid-task.** If a fix needs a new system (e.g., particle effects for damage flash), open a new task in `PLAN.md` and verify it on its own loop. Don't pile.
- **"It works on my machine" via interactive run.** Stage 6 verifies via the harness — `play_and_capture`, `inspect_state`, `render_audio`. An interactive run means nothing.
- **Skipping `MEMORY.md` updates.** A gotcha you found and didn't write down will cost an hour next session.

## When this stage is done

- Every PLAN.md task is marked done with a one-line `verified by:` note.
- `MEMORY.md` records the gotchas worth keeping.
- The proof bundle exists at `screenshots/result/<N>/` (win-path GIF, lose-path GIF, milestone frames, audio renders) — see `capture.md` for the bundle contract.
- Move to Stage 7 (read `quality-gate.md`).
