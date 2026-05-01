# Reference: Proof Bundle Production

Called from `task-execution.md` (intermediate captures) and
`quality-gate.md` (final bundle check). Produces a
`screenshots/result/<N>/` directory containing runnable evidence
that the game functions end-to-end.

## Bundle structure

For attempt `<N>` (start at 1, increment each new final attempt):

```
screenshots/result/<N>/
├── win-path.gif         — record_gameplay output of full clear
├── lose-path.gif        — record_gameplay output of full death
├── frames/
│   ├── title.png
│   ├── play_start.png
│   ├── mid_game.png
│   ├── win.png
│   └── game_over.png
├── audio/
│   ├── bgm_ch0.wav      — render_audio per BGM channel
│   ├── bgm_ch1.wav
│   ├── bgm_ch2.wav
│   ├── se_jump.wav      — render_audio per SE manifest entry
│   ├── se_climb.wav
│   ├── se_death.wav
│   └── se_win.wav
└── notes.md             — summary, observations, known issues
```

`record_gameplay` writes the GIFs; `render_audio` writes WAVs via
its `output_wav_path` argument; `capture_frames` writes PNGs.

## Win-path GIF requirements

- Duration: at least the full win-path scenario, typically 20–30
  seconds at 30 fps = **600–900 frames**.
- Must show the player traversing from start to goal and ending
  on the WIN scene.
- A bundle whose first 5 seconds look right and then sits static
  for 20 seconds is FAIL, not partial pass — `compare_frames`
  between mid and late frames must show meaningful change.

## Lose-path GIF requirements

- Duration: at least until GAME_OVER triggers, typically
  **≥ 360 frames** (~12 s at 30 fps).
- Must show a hazard appearing, hitting the player, and `lives`
  decrementing on screen.
- Must end on the GAME_OVER scene.

## Frame snapshots

Capture key scene transitions with `capture_frames`. Pick frames
that fall on TITLE, the moment PLAY starts, mid-game, WIN, and
GAME_OVER. For input-driven scenes (PLAY, mid-game), use
`play_and_capture` with the same input schedule the GIF uses, so
the snapshots and the GIF tell the same story.

## Audio rendering

For every audio cue declared in `REFERENCE.md` §6 (BGM channels and
SE), render to WAV. Verify each WAV is non-empty and contains
notes — an empty `notes` array in the response means the slot is
blank or the script never ran the `set` call. The note sequence
in the response confirms the BGM/SE plays the intended pitches,
even though headless playback is silent.

## notes.md template

Brief summary, no narrative prose. Replace angle brackets with the
actual values:

```markdown
# Bundle <N>

Generated: <ISO timestamp>
Game: <Title>
Spec: REFERENCE.md @ <git ref>
Plan: PLAN.md @ <git ref>

## Verified

- Win path GIF: <duration>s, ends on WIN at frame <N>.
- Lose path GIF: <duration>s, ends on GAME_OVER at frame <N>.
- Audio: <count> BGM channels rendered, <count> SE rendered.
- Frames: title / play_start / mid_game / win / game_over all show
  recognizable scenes.

## Known issues

- <anything caught but accepted as out-of-scope, with rationale>
```

## Concrete invocations

```bash
record_gameplay main.py \
  --inputs '<win-path inputs from PLAN.md>' \
  --duration 720 --scale 2 \
  > screenshots/result/1/win-path.gif

record_gameplay main.py \
  --inputs '[{"frame":30,"keys":["KEY_SPACE"]},{"frame":32,"keys":[]}]' \
  --duration 480 --scale 2 \
  > screenshots/result/1/lose-path.gif

capture_frames main.py --frames="30,90,180,360,720" --scale=2

render_audio main.py --sound_index=10 \
  --output_wav_path=screenshots/result/1/audio/se_jump.wav

render_audio main.py --music_index=0 \
  --output_wav_path=screenshots/result/1/audio/bgm_ch0.wav
```

## Anti-patterns

- Bundle with `duration < 60`. Too short to demonstrate the loop.
- Skipping audio. A game with no rendered SE/BGM is not a complete
  proof, even if the visuals are perfect.
- Frames captured but no GIF. Static PNGs cannot prove animation
  or input handling.
- Reusing a stale bundle from before a code change. Bump `<N>` and
  produce a fresh bundle after any non-trivial change.
- Bundle whose middle 80% is the same frame (game stalled). Use
  `compare_frames` between two frames in that range to confirm
  meaningful motion before declaring the bundle complete.

## When this is done

`screenshots/result/<N>/` exists with all required artifacts:
both GIFs, the five frame snapshots, one WAV per audio manifest
entry, and `notes.md`. The counter `<N>` is the next integer
above the previous bundle. Return to `task-execution.md` (which
hands off to `quality-gate.md`).
</content>
</invoke>