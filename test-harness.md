# Reference: Milestone Playthrough Verification

Called from `task-execution.md` (Stage 6) and from `quality-gate.md`
when re-verifying a fix. Run the win-path and lose-path milestone
tables from `PLAN.md` against the implemented game. This is the
integration test; per-task verification belonged to earlier stages.

## What to run

For each milestone table in `PLAN.md` (one for the win path, one
for the lose path):

1. Build the input schedule from the table's `Inputs` column.
2. Build the assertion plan from the table's `Asserts` column.
3. Call `play_and_capture` with the input schedule, capturing
   screenshots at each milestone frame.
4. Call `inspect_state` at the same milestone frames, with the
   attributes the assertions reference.
5. Aggregate per-milestone PASS/FAIL into a single result.

## Win-path execution

The win-path schedule is a sequence of inputs leading the player
from start to goal. Translate the milestone table directly into
the `play_and_capture` `inputs` JSON:

```
| Frame | Inputs (held until next row) | Asserts |
|-------|-----------------------------|---------|
| 30    | KEY_SPACE press             | scene == PLAY |
| 60    | KEY_RIGHT held              | player.x > start_x + 20 |
| 120   | KEY_UP at ladder            | player.y < floor_y - 8 |
```

becomes

```json
[
  {"frame": 30, "keys": ["KEY_SPACE"]},
  {"frame": 32, "keys": []},
  {"frame": 60, "keys": ["KEY_RIGHT"]},
  {"frame": 120, "keys": ["KEY_UP"]}
]
```

Then call `inspect_state` with `frames="30,60,120,..."` and
`attributes="scene,player_x,player_y,..."`, evaluating each
predicate against the captured value.

## Lose-path execution

The lose path is usually simpler: the player stands still (or
performs the minimum input to enter PLAY) and is killed by hazards.
Schedule: enter PLAY, then empty inputs.

```json
[
  {"frame": 30, "keys": ["KEY_SPACE"]},
  {"frame": 32, "keys": []}
]
```

Run for the full death duration (typically 360–600 frames). Assert
at intermediate milestones that `lives` decrements, and at the
final milestone that `scene == GAME_OVER`.

If the lose path does not fail by the planned final frame, either
hazards are not actually hazardous (collision detection bug; back
to per-task verification) or difficulty is too low (boss spawn
rate, hazard speed) — fix and rerun.

## Stall and crash monitoring

Beyond per-milestone asserts, the harness watches for:

- **Crash:** `play_and_capture` returns non-zero or the captured
  stderr contains an exception trace → FAIL with
  `script crashed at frame N`.
- **Stall:** the state hash (concatenation of inspected attributes)
  is unchanged across 60 consecutive frames *despite* the schedule
  having sent inputs in that range → FAIL with
  `no progress between frame X and frame Y; expected motion in attribute Z`.
- **Frame budget:** if the script averages > 100ms per frame
  → WARN, not FAIL. Flag as a perf bug for later.

## Closed-loop steering for paths > 200 frames

Open-loop scripted inputs drift on long paths. For win paths
beyond ~200 frames, run in segments: at each milestone, read
observed state with `inspect_state`, compute the next input
segment, then call `play_and_capture` again from that frame
forward. Example: instead of pre-baking "hold RIGHT for 80
frames", check at frame 60 whether the player has reached the
expected ladder x — if yes, switch to KEY_UP; if not, keep
RIGHT for another 10 frames and recheck.

For v0.1.0, open-loop with generous tolerances is acceptable for
most win paths. Closed-loop is the escape hatch when an open-loop
schedule cannot be made deterministic.

## Test fixture considerations

If production code reads input through `pyxel.btnp` / `pyxel.btn`,
the harness's `set_btn` calls flow through naturally — no code
changes for testing.

If the game has frame-based logic that needs determinism (random
spawn timing, particle scatter), seed the RNG at scene start so
runs are repeatable: `pyxel.rseed(42)` (or any fixed seed).

## Anti-patterns

- Asserting only the final milestone. Intermediate asserts catch
  early divergence cheaply.
- Verifying only the win path and skipping the lose path. The
  lose path is what proves hazards function as hazards.
- Loose predicates ("scene changed") instead of exact values
  ("scene == WIN"). A loose predicate passes for the wrong reason.
- Capturing state at a frame that exceeds the input schedule's
  last entry. The schedule's final entry must precede the last
  observation frame, or `play_and_capture` will run out of inputs.

## When this is done

All win-path milestones PASS, all lose-path milestones PASS, no
crashes, no stalls. Return to `task-execution.md` and proceed to
producing the proof bundle (`capture.md`).
</content>
</invoke>