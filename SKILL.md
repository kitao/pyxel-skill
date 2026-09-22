---
name: pyxel
description: Build, debug, and verify games made with Pyxel, the retro game engine for Python. Use whenever a task creates, changes, tests, or reviews a Pyxel game, or asks for a retro Python game that should use Pyxel. Do not use for other engines or general Python work.
license: MIT
compatibility: Requires the pyxel-mcp MCP server 1.3 or newer (Python 3.11+, installs Pyxel 2.9.6+). Use `uvx --from 'pyxel-mcp>=1.3.0' pyxel-mcp` as the server command.
metadata:
  version: "1.4.2"
  pyxel-mcp: ">=1.3.0"
---

# Pyxel

Build the smallest complete game that satisfies the request, then prove it from observed behavior. Keep the process proportional to the task.

## Runtime

pyxel-mcp provides eight observation tools. They report facts; judging them is your job.

- `validate` reports syntax errors and recognizable Pyxel code patterns without running the script.
- `run` drives headless frames with scheduled input, stops on `until`, and captures `state`, `screen_image`, `screen_grid`, or `video`. `screen_image` with `inline: true` returns an image.
- `pyxel_info` reports versions, bundled examples, and resource URIs.
- `read_palette`, `read_image`, `read_tilemap`, and `read_audio` inspect the palette, image banks, tilemaps, and rendered audio; `read_image` and `read_tilemap` take `inline=true` to return their renders as images.
- `diff_frames` compares two captured PNGs.

If tools are missing or `pyxel_info` reports a version below 1.3.0, update the plugin or set the client's MCP command to `uvx --from 'pyxel-mcp>=1.3.0' pyxel-mcp`. Append `install` for setup examples; it only prints instructions. Apply the appropriate registration with this versioned command. Avoid duplicate plugin registrations. Restart the client and recheck `pyxel_info`. While blocked, use focused logic tests plus direct headless Pyxel runs, and report weaker visual and interaction verification.

## Workflow

1. Infer the smallest playable scope. Ask only when a missing choice would materially change the game.
2. Implement a complete slice: entry state, controls, objective, and a retry or terminal state when the genre needs one. Keep assets in code unless files are provided. For presentation defaults, read [references/design.md](references/design.md).
3. Run `validate`. Fix errors; resolve or explain relevant warnings.
4. Run from frame 0 with a `random_seed` and an explicit input schedule. Capture `state` for mechanics and `screen_image` with `inline: true` and `scale` 2 to 4 for what the player sees. Use `until` with `"frame": "end"` snapshots when the event frame is unknown.
5. Read `log` even when `ok` is true. Look at the returned frame for the task-specific result; a non-blank screen is not evidence of a correct scene.
6. Iterate only on observed defects. Add focused logic tests when rules are easier to prove outside rendering.
7. Report controls, changed files, exact verification results, and what was not verified.

## Minimum evidence

- `validate` has no errors; relevant warnings are resolved or explained.
- A smoke `run` reaches its intended stop without crash, timeout, or unexpected stall.
- At least one captured frame is inspected directly.
- At least one task-specific state predicate is checked.

Add only relevant evidence: success and failure paths for action games, legal and illegal moves for puzzles, rendered WAV data for authored audio, asset inspection when sprites and maps are part of the request.

## References

- [references/pyxel.md](references/pyxel.md): input, drawing, assets, audio, and determinism. Read for related implementation or diagnosis.
- [references/design.md](references/design.md): presentation and game-feel defaults for creating or polishing games.
- [references/strict-mode.md](references/strict-mode.md): opt-in evidence for release confidence, audits, proof bundles, or long multi-session builds.

## Boundaries

- Treat tool output as evidence, not aesthetic judgment.
- Do not require a proof bundle for ordinary edits.
- Do not accept a broken frame because state checks passed.
- Do not claim sound quality without listening; report it as not auditioned.
- Do not create planning or tracking files unless project scale makes them useful.
- Do not substitute placeholder shapes for requested sprite art unless primitive geometry is the intended style.
