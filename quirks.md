# Pyxel Quirks

Keep this file small and high-signal. Each item below has bitten real implementations and shows up as ambiguous bugs.

**Inclusion rule.** Add only repeated, non-obvious issues that would have prevented real confusion in `scaffold`, `asset-gen`, `task-execution`, `capture`, or any `knowledge/` file. If an item is already in `pyxel-mcp`'s `instructions.md` Error Recovery section, it does not belong here. If it is answerable by `pyxel://api-reference`, it does not belong here.

## Coordinates and drawing

- **Origin (0, 0) is top-left, Y increases downward.** Math conventions
  with origin bottom-left will produce upside-down sprites. Always
  reason about Y as "distance from top".
- **Draw order is paint order.** Background first, sprites next, UI
  on top. There is no z-buffer; whatever you draw last wins.

## Image bank lifecycle

- `pyxel.images[N].set(...)` and `.load(...)` must run **before**
  `pyxel.run()`, in `__init__` or a setup helper. Calling them inside
  `update`/`draw` either misses the first frames or wastes CPU
  re-uploading every frame.
- The image bank is **256x256 pixels per slot**. Plan u/v coordinates
  in `ASSETS.md` so sprites do not overlap. Default Pyxel exposes
  3 banks (0, 1, 2); more can be added but most games stay within
  the defaults.

## Tilemap (0, 0) is the default "empty cell"

- Pyxel initializes every cell of `pyxel.tilemaps[N]` to tile coord
  `(0, 0)`. If the source image bank has visible content at its
  (0, 0) tile, every "empty" cell of the tilemap renders that
  content — typically a stair-step pattern of half-drawn sprites
  across the screen, easy to miss on a small screenshot.
- The fix: keep the source bank's (0, 0) tile fully transparent
  (all palette index 0). `inspect_image(image=0, x=0, y=0, w=8, h=8)`
  confirms this; `inspect_tilemap(...).trap_warning` flags
  violations. `quality-gate.md` check #13 enforces it.

## Input simulation in headless mode

- The MCP harness drives input through `pyxel.set_btn(key, frame)`
  and `pyxel.set_btnv(key, val)`. Production code reads the same
  events via `btn()` / `btnp()` — no code branch needed for tests.
- This is the entire reason `run` (with scheduled `inputs` and
  `screen_image` / `state` / `video` snapshots) can verify
  input-dependent logic. If your code reads input through some other
  mechanism (e.g., directly polling SDL), tests will not drive it.

## Audio: SE volume and tone choice

- The 4 audio channels are split BGM (ch0–ch2) and SE (ch3). SE
  volume must be **5–7** (out of 7) to cut through 3-channel BGM.
  Volumes 1–4 are typically inaudible during gameplay.
- Square (`"s"`) and pulse (`"p"`) tones carry over BGM. Noise
  (`"n"`) is too quiet for melodic SE — reserve it for percussive
  hits where the texture is the point, not the pitch.

## Headless audio driver

Headless runs (the MCP harness, CI) need `SDL_AUDIODRIVER=dummy` in
the environment, otherwise SDL tries to open a real audio device
and may hang or error. The harness sets this for you, but if you
shell out to your own subprocess for audio rendering, set it
explicitly. `render_audio` produces real WAV output even in dummy
mode — the dummy driver only suppresses speaker playback.

## `state` snapshots do not auto-expand deep nesting

The `state` snapshot kind inside `run` reads attributes off the
`App` instance (the class that calls `pyxel.run()`). With `attrs:
None` (or omitted), only top-level scalar primitives are returned —
lists, dicts, and custom objects are skipped. Dotted/indexed paths
like `"player.x"` or `"barrels[0].y"` are followed when explicitly
named, but **arbitrary nested chains are not auto-expanded**:
`app.world.player.physics.velocity.y` will not be reachable as a
single attr — name each leaf individually, or flatten to top-level
App attributes (`self.player_x`, `self.player_vy`, `self.scene`).

## `pyxel.quit()` does not force-exit since 2.8

`pyxel.quit()` *requests* the loop to end after the current frame.
Since Pyxel 2.8, it does **not** force-terminate the process. A
`while True:` loop or busy-wait inside `update()` after calling
`quit()` will hang the script — and hang the harness, which will
hit its timeout instead of exiting cleanly. Return from `update()`
promptly; let the loop end naturally.

## Feedback Loop

Quirks are curated manually in this skill. Add only repeated, non-obvious issues that would have prevented real confusion in a stage file (`scaffold`, `asset-gen`, `task-execution`, `capture`) or in a knowledge file. Remove items that have stopped biting after engine or skill changes.
</content>
</invoke>