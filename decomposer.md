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
