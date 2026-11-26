# 2D graphics, tilemaps, and sound

## Implement with Pyxel

Initialize the display before accessing its banks. Load shared resources during setup. With `pyxel.run(update, draw)`, advance the game in `update` and draw from that state. Use `btn` for held movement and `btnp` for an action that fires on press. A static picture can use `show()`. For an interactive web target use callbacks, since manual `flip()` is desktop-only.

- **Sprite drawing.** `pyxel.images[0].set(x, y, rows)` takes one hex digit per pixel and ignores whitespace. Draw the region with `blt`, supplying the sprite's transparent palette index as `colkey`. A negative width mirrors the sprite. When a project uses a custom palette, set it with `pyxel.colors[:] = colors` before importing images that must map to it.
- **World and screen coordinates.** Apply `pyxel.camera(x, y)` for the world, then reset with `pyxel.camera()` before drawing a screen-space HUD. Restore any clip, palette remap, or dithering used for a local effect before drawing layers that should retain their normal appearance.
- **Tilemaps.** Each cell references an 8×8 region in its source image. `tilemap.pget(tx, ty)` takes tile coordinates, while `pyxel.bltm` takes its source rectangle in pixels. `Tilemap.collide` accepts the moving rectangle and displacement in pixels and returns the allowed displacement. The bundled `10_platformer` shows how to apply it.
- **Sound.** Use `Sound.set` for tracker notes, `Sound.mml` for a score, or `Sound.pcm` to load recorded audio. Choose channels for music and effects so triggering one preserves the parts that should continue. Check the event that starts playback as well as the sound slot it selects.

Use the installed declarations for exact parameters and the [Pyxel API reference](https://kitao.dev/pyxel/api-reference/) for behavior.

## Inspect the asset at the right point

The four readers take a local path in `script`. A `.pyxres` loads directly with its matching sibling `.pyxpal` when present. A trusted Python script exposes the banks it has prepared by its first `run`, `show`, or `flip`. To inspect pixels produced later during gameplay, capture the screen with `run`.

| Question | Observation |
|---|---|
| Which colors are in the palette or used by image banks? | `read_palette` returns RGB colors and used indices. |
| Is the intended sprite in the bank? | `read_image` takes an `image` index and `x, y, w, h` in pixels. Set `inline: true` to see the crop. |
| Which tile is drawn at this location? | `read_tilemap` takes a `tilemap` index and `bbox: [x, y, w, h]` in tiles. Inspect `sampled_region`, `tiles`, and `imgsrc`. A cell referencing tile (0, 0) can have visible artwork. |
| What does the selected cue sound like? | `read_audio` takes one sound or music slot. Listen to the WAV for timbre and balance. The `notes` field describes tracker data. Use the render for MML or PCM. |

To trace a wrong-looking tile, use `read_tilemap` on the affected row. Try this on `assets/platformer.pyxres` beside the bundled `10_platformer.py`. It selects eight cells starting at tile (0, 17).

```json
{
  "script": "/absolute/path/assets/platformer.pyxres",
  "tilemap": 0,
  "bbox": [0, 17, 8, 1],
  "inline": true
}
```

The returned tile pair `[u, v]` identifies the artwork. For a numbered `imgsrc`, inspect that bank with `read_image` at pixel `(8*u, 8*v)` with width and height 8. If both the map and the tile look right, check the game's source rectangle, transparency, and camera in a rendered frame.

To hear sound 0 from an editor resource, substitute its absolute path in this `read_audio` call.

```json
{
  "script": "/absolute/path/game.pyxres",
  "target": {"sound": 0},
  "inline": true
}
```

The result includes duration, peak amplitude, and a local WAV path. An inline WAV limit of 4 MiB applies. If the client cannot play audio, report the measurements you actually checked.

## Older projects and distribution

Pyxel 3 removed pre-2.0 resource loading and the old MML syntax. When migration is requested, keep the originals and convert a copy of a legacy resource in a compatible Pyxel 2 editor. Check the converted banks and audition rewritten music. See the [current MML commands](https://kitao.dev/pyxel/mml-studio/mml-commands.html).

When a packaged game is requested, run `pyxel package game game/main.py` from the parent of the game directory, substituting the actual directory and entry point. Include the assets at the paths used by the game. Exercise the resulting `.pyxapp` with `pyxel play`, or convert it with `pyxel app2html` and check the generated page in a browser for a web target.
