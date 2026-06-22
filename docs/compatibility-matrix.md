# Compatibility Matrix

Known current runtime pairings for `pyxel-skill`.

| pyxel-skill | pyxel-mcp | Pyxel | Python | Notes |
|---|---|---|---|---|
| 1.1.0 | >= 1.0.0 | >= 2.9.6 | >= 3.10 | Current 9-tool surface: `run`, `validate`, `pyxel_info`, `read_*`, `diff_frames`. |

`pyxel-mcp` should be registered under the `pyxel` MCP namespace before the skill starts. Run `pyxel_info` first when debugging a host setup.
