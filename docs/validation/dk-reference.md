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

- Player: `idle`, `walk_1`, `walk_2`, `jump`, `climb_1`, `climb_2` (6 sprites, 16x16). Paired frames (`walk_1`/`walk_2`, `climb_1`/`climb_2`) laid out **horizontally** in the bank (frame_2 immediately right of frame_1) so `inspect_animation(... region_count=2, direction="horizontal")` resolves the pair.
- Antagonist: at least `boss_idle` (32x32).
- Goal: `princess` (16x24).
- Hazard: `barrel_1`, `barrel_2` (16x16, paired-frame diff 5–50%, laid out **horizontally** for `direction="horizontal"`).
- HUD: `life_icon` (8x8).

If `inspect_animation` (with `region_count=2`, `direction` matching the ASSETS.md bank layout) reports `region_diffs[0]["diff_ratio"]` outside 0.05–0.50 on any pair, gate check #4 FAILs.

## Quality gate expected output

`screenshots/result/1/gate-report.json` should show:

- `summary.pass` == 13, `summary.fail` == 0.
- All 13 checks individually PASS per the `quality-gate.md` table (12 original + #13 tilemap trap).

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
