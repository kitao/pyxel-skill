# Stage 5: Asset Generation

For every entry in `ASSETS.md`, write the `pyxel.images[N].set()` call in `_build_assets()` and verify the rendered sprite reads as its `represents:` description before moving on.

## Inputs

- `ASSETS.md` (from Stage 4) — full sprite manifest with bank coordinates, palette plan, identity contract.
- `STRUCTURE.md` "Modules" — `_build_assets()` lives in `App.__init__`.
- `main.py` — runnable skeleton from Stage 3.
- `knowledge/pixel-art.md` — 16-color palette, 3-color-per-material rule, sprite design process.

## Output

`main.py` with `_build_assets()` populated. Every ASSETS.md entry has a working `inspect_sprite` showing distinguishable pixels at the declared coordinates.

## Loop per asset

For each entry in ASSETS.md, in the order they appear:

1. Write the hex-string sprite data into `_build_assets()` (or a helper called from it).
2. Run `validate_script` to catch syntax errors in the hex strings (wrong length, missing comma, bad indent).
3. Run `inspect_sprite` at the asset's bank coordinates to dump pixels.
4. **Look at the pixels.** Does the silhouette match the `represents:` description? Are color regions distinguishable?
5. If FAIL — rewrite the hex strings. Don't move on. Catch one bad sprite before writing 10 of them.

Concretely, for one asset:

```bash
# After editing main.py to add player_walk_1:
validate_script main.py
inspect_sprite main.py --image_index=0 --x=0 --y=0 --w=16 --h=16
# Look at the output grid. Is it Mario, or a blob?
```

## Sprite identity heuristics

`inspect_sprite` returns a hex pixel grid plus aggregate fields. Map the ASSETS.md identity contract to those fields directly — do not eyeball:

- **Color region count.** `inspect_sprite` returns `color_count` as a dict `{palette_idx: pixel_count}`. Assert `len(color_count.keys()) >= min_distinct_colors` from ASSETS.md. Below that → single-blob → FAIL.
- **Bounding-box density.** `inspect_sprite` returns `fill_ratio` (non-transparent pixels / total). Assert `0.15 <= fill_ratio <= 0.95`. Above 0.95 → no silhouette. Below 0.15 → too few visible pixels.
- **Frame pair diff.** For paired frames (`walk_1` / `walk_2`), call `inspect_animation` with `frame_count=2` at the pair's bank position. The harness computes per-frame `diff_ratio` automatically; assert `0.05 <= diff_ratio <= 0.50`. Do NOT compute the diff yourself by reading raw `pixels` arrays — `inspect_animation` does it.
- **Edge contrast** (for outlined sprites): perimeter palette indices should differ from interior majority color. The output flags this as a warning when contrast is too low; treat warnings as FAILs for outlined sprites.

## Worked example: `player_walk_1` (16x16, 6+ colors)

```python
# Inside _build_assets():
pyxel.images[0].set(0, 0, [
    "0008888880000000",   #     ████
    "0088888888000000",   #    ██████
    "008f44ff44f00000",   #   skin/face with outline & mouth
    "008f4ff4ff4f0000",   #   eye details
    "0008f4444f000000",   #
    "0008cccccccc0000",   #   overalls (12=cyan)
    "008c87887878c000",   #   buttons (8=red dots)
    "008cccccccccc000",   #
    "0088cc8800cc8800",   #   arms swing forward
    "008c08000080cc00",   #
    "0080000000000000",   #
    "00cccc0000cccc00",   #   legs separated (one fwd, one bk)
    "00cccc0000cccc00",   #
    "0044440000444400",   #   shoes (4=brown)
    "0044440000444400",   #
    "0000000000000000",
])
```

This is illustrative — exact pixels depend on art direction. The point is: 16x16 is enough room for cap, face, eyes, mustache hint, overalls with two buttons, arm in distinguishable position, two separated legs, and shoes. A "Mario-shaped blob" with one or two colors does not satisfy the contract.

After writing this block:

```bash
validate_script main.py
inspect_sprite main.py --image_index=0 --x=0 --y=0 --w=16 --h=16
```

Expect `color_count` keys ≥ 5 (e.g., `{0, 4, 8, 12, 15}` for transparent / brown / red / cyan / white), and `fill_ratio` around 0.45.

## Hex-string conventions

Every character in a hex string is a single palette index `0`–`f`. Width = number of characters per line; height = number of lines. Pyxel does not tolerate ragged rows: if one line is 15 chars and another is 16, `validate_script` flags it but the underlying `images.set()` call may silently pad or crash depending on context. Keep all rows the same length.

Conventions worth holding to:

- Use `0` for transparent pixels and pass `colkey=0` everywhere `blt()` is called. Mixing transparent palette indices across sprites breaks reuse.
- Indent hex strings at the same column so columns line up visually — this is how you spot a stray pixel before running `inspect_sprite`.
- Trailing comments (`# overalls (12=cyan)`) are encouraged. Stage 6 maintainers read these.
- For 8x8 sprites, prefer 8x8 over a half-filled 16x16 — pixel density scales differently and animation diff thresholds tighten.

## Animation pairs

When ASSETS.md declares paired frames (`walk_1` / `walk_2`, `barrel_1` / `barrel_2`, swing-left / swing-right), implement both before verifying. `inspect_animation` is the only tool that reports the per-frame diff cleanly:

```bash
inspect_animation main.py --image_index=0 --x=0 --y=0 --w=16 --h=16 --frame_count=2
```

The two frames must share palette (same `color_count` keys, allowing for one or two pixels of motion-driven swap) and outline silhouette, but differ in 5–50% of pixels. Practical recipe: copy walk_1's hex into walk_2, then move legs / arms / cape down or up by 1–2 pixels. Don't redraw walk_2 from scratch; it will diverge too much.

## Bank organization tip

Use a region dict that mirrors ASSETS.md so coordinates aren't magic numbers:

```python
REGIONS = {
    "player_walk_1": (0,   0),
    "player_walk_2": (16,  0),
    "player_jump":   (32,  0),
    "hammer_idle":   (96,  0),
    "hammer_swing":  (112, 0),
    "boss":          (128, 0),
    "barrel_1":      (0,  32),
    "barrel_2":      (16, 32),
}

def _build_assets(self):
    img = pyxel.images[0]
    img.set(*REGIONS["player_walk_1"], [...])
    img.set(*REGIONS["player_walk_2"], [...])
    # ...
```

When you change a coordinate in ASSETS.md, change it once here. Draw calls `pyxel.blt(x, y, 0, *REGIONS["player_walk_1"], 16, 16, colkey=0)` stay readable.

## End-of-stage verification

Once every ASSETS.md entry is implemented, run a whole-stage scan:

```bash
inspect_bank main.py --image_index=0
```

Visually scan the bank: every declared region should contain its asset, no empty regions where ASSETS.md says there should be data, no sprite spilling into a neighbor's region. Then for each animation pair declared in ASSETS.md:

```bash
inspect_animation main.py --image_index=0 --x=0 --y=0 --w=16 --h=16 --frame_count=2
```

Frames should differ (5–50% per-frame diff) but share palette and silhouette outline. If the diff is below 5%, the animation will look static. Above 50%, it will flicker.

## Anti-patterns in this stage

- **Generating sprites in `update()` instead of `_build_assets()`.** Either runs every frame (perf disaster) or runs after `pyxel.run()` starts and is invisible to `inspect_sprite` for the first few frames.
- **"Add it later" placeholders:** `pyxel.rect(x, y, 8, 8, 8)` in `draw()` instead of `pyxel.blt(...)`. The asset manifest declares a sprite; the draw call must `blt` from it. Asset-gen was skipped — the gate FAILs check #4.
- **Bulk-edit then bulk-verify.** Edit one sprite, run `inspect_sprite`, look at the grid, fix, then move on. Editing 10 sprites before running `inspect_sprite` once means 10 broken sprites to triage at once.
- **Forgetting `colkey=0` in `blt()` calls.** The transparent background of the sprite renders opaque (palette index 0). `validate_script` warns about missing `colkey` — fix it.
- **Computing diffs yourself.** `inspect_animation` returns `diff_ratio`. Don't read raw `pixels` arrays and XOR them — the harness already did the math.

## When this stage is done

- Every ASSETS.md entry has a corresponding `pyxel.images[N].set(...)` call in `_build_assets()`.
- `inspect_sprite` per asset reports `color_count` keys ≥ ASSETS.md minimum, `fill_ratio` in [0.15, 0.95].
- `inspect_animation` per paired frames reports `diff_ratio` in [0.05, 0.50].
- `inspect_bank --image_index=0` shows the declared layout with no overlap and no missing regions.
- Move to Stage 6 (read `task-execution.md`).
