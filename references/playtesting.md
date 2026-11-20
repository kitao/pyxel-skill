# Playtesting with pyxel-mcp

## Replay a player action

In Pyxel's bundled `10_platformer`, the player starts at the left edge. To observe the first 16 pixels of rightward movement, find the example in `pyxel_info.examples` and substitute its absolute `path` below. Keeping the script in place lets it load its own level and sprites. Read its source at `pyxel://examples/10_platformer`.

```json
{
  "script": "/absolute/path/10_platformer.py",
  "frames": 30,
  "inputs": [{"frame": 0, "buttons": ["KEY_RIGHT"]}],
  "until": "__main__.player.x >= 16",
  "snapshots": [
    {"kind": "state", "frame": "end", "attrs": ["__main__.player.x"]},
    {"kind": "screen_image", "frame": "end", "inline": true, "scale": 2}
  ]
}
```

Check that `until_met` is true, read the final position, and look at the returned PNG. Replay with an empty input schedule to check that the movement depends on input. In your own game, choose the control, state path, and condition from its source.

## Schedule the input

Each `run` starts fresh at frame 0. To continue a route, replay the full schedule with a larger frame budget. Set `random_seed` when comparing runs that use Pyxel or Python's module-level RNG. Independently seeded generators, clocks, and external data can still vary.

- A `buttons` list replaces the held set. To jump while walking, send `["KEY_RIGHT", "KEY_SPACE"]` together, then `["KEY_RIGHT"]` on the next frame. Send `[]` to release all buttons. An `axes` map also persists until replaced.
- Mouse position persists. `mouse_wheel` (horizontal, vertical), `input_text`, and `dropped_files` apply on their scheduled frame only. Put simultaneous events in one entry.
- `run` drives `pyxel.run` callbacks, observes a static `pyxel.show()`, and treats each manual `pyxel.flip()` as a presented frame. A finite loop or `pyxel.quit()` can finish before the budget.

## Choose the observation

Use a `state` path such as `player.x` on the bound update object, or `__main__.player.x` for a script global. Paths support attributes and indexing. Put comparisons in `until`. Use a small `screen_grid` region for exact palette indices and `screen_image` for the player's view. Inspect a short `video` or several frames for movement and transitions. `diff_frames` gives the changed pixels between two saved PNGs.

A single inline PNG can use the server's temporary path. For multiple frames in one `screen_image` request, use `frames` and an absolute `output_pattern` ending in `.png` with a literal `{frame}`. The server embeds up to 12 PNGs per call. See `pyxel://run-snapshots-schema` for ranges and recording options.

## Diagnose an unexpected result

- **A condition never fired.** Check `exit_status`, `frame_count`, `until_met`, `log`, and snapshot warnings. Capture the relevant values earlier in the route. A false condition was evaluated without a match. A null value means it was never evaluated.
- **The game looks stuck.** Observe a value or small pixel region that should change during this action. For stall detection, request `state` or `screen_grid` on consecutive frames and set `stall_window_frames`. A menu waiting for input can legitimately repeat.
- **A tool reports an error.** Inspect its structured `errors` and any completed observations. For `validate`, read `issues` and their severities. An informational finding can describe intentional drawing behavior. Category definitions are at `pyxel://validation-patterns`.
- **Release review.** Exercise the game's reachable success, failure, and retry paths and any relevant rejected actions. Retain the input schedule, seed, and representative frames or audio when someone needs to reproduce the result. For performance or platform-specific behavior, play the artifact on the intended target.
