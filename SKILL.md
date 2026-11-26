---
name: pyxel
description: Create, debug, and playtest Python games made with Pyxel, including Pyxel Cube 3D. Use for Pyxel gameplay, rendering, controls, sound, .pyxres assets, and GLB models and motions in Cube.
license: MIT
metadata:
  version: "1.6.1"
  python: ">=3.11"
  pyxel-mcp: ">=1.5.0"
  pyxel: ">=3.0.3"
---

# Pyxel

**For a new game**, start with the action the player takes and what changes when it succeeds or fails. Build that interaction at the intended screen size, play it, and use the result to tune controls, art, and feedback. See [game design](references/design.md) for new games and polish work. For a 3D game, use the [Pyxel Cube guide](references/cube.md) to build the scene and camera.

**For an existing game**, find its entry point, controls, assets, and target Pyxel version. Reproduce the reported behavior through the normal controls when possible. After the change, replay the same inputs and check the consequence the player can see or hear.

**For an asset question**, inspect a [`.pyxres` resource](references/pyxel.md) directly with the relevant reader. For a [GLB model or motion](references/cube.md#import-a-model-and-play-its-motions), use Cube. Use the game itself when the question depends on how it draws or plays the asset.

Use Pyxel's standard 16 colors for new artwork unless the user requests a custom palette or the project already defines one. When creating [2D pixel art](references/design.md#draw-for-decisions), draw the sprites or scenery as assets you can inspect on their own. Check how they read together in the game.

## Work with the installed runtime

Use `pyxel_info` to check the server and Pyxel versions and find bundled examples. The bundled command is `uvx --from 'pyxel-mcp>=1.5.0' pyxel-mcp`. It installs Pyxel for the server. Check the game's own dependency before adopting a new API, and verify a pinned project in its own environment.

For an unfamiliar call, ask `lookup_api` for a symbol such as `Image.set` or `cube.Node`. A partial name returns candidates. Look up a match for its declarations. To read a bundled example, append its name from `pyxel_info` to `pyxel://examples/`. To play it, pass its returned file path to `run` so its assets resolve.

## Play the change

Use `validate` for static findings. Use `run` on a trusted entry script to observe the game headlessly. Choose input and a check that could actually fail if the change were broken. Inspect state for a rule, a rendered frame for appearance, and a sequence for timing. For a new game, play through its main interaction and look at the result on screen.

If an observation contradicts the intended behavior, fix the cause and replay the affected route. The [playtesting guide](references/playtesting.md) includes a runnable example, input timing, state paths, and ways to diagnose a missed event. If MCP is unavailable, use the project's tests and a bounded headless check supported by its Pyxel version. Report how to launch or reproduce the change, what you observed, and any target or behavior that still needs verification.
