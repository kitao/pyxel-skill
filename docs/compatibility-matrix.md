# pyxel-skill Compatibility Matrix

Known-working combinations of pyxel-skill, pyxel-mcp, and the underlying Pyxel engine.

## Pinning policy

The `Required runtime` block in `SKILL.md` lists the **floor** version of pyxel-mcp that pyxel-skill expects. The actual tested combinations are recorded here.

When a new pyxel-skill release is tagged, append a new row with the validated versions and the date of validation. Do not delete old rows — they are useful for users on older toolchains.

## Matrix

| pyxel-skill | pyxel-mcp | Pyxel engine | Python | Validated on  | Validation prompt | Notes                                                        |
|-------------|-----------|--------------|--------|---------------|-------------------|--------------------------------------------------------------|
| 0.1.0       | 0.9.3     | 2.8.7        | 3.14   | 2026-05-01    | DK                | Initial release. macOS Darwin 25.3.0 + uv 0.10.7 + Pyxel 2.8.7 in `.venv`. |

## Floor / ceiling guidance

- **pyxel-mcp floor:** 0.9.3 — required because earlier versions still carry the design knowledge in `instructions.md` that pyxel-skill v0.1.0+ migrated to `knowledge/`. Earlier pyxel-mcp versions still work as a tool host but pollute context.
- **pyxel-mcp ceiling:** open. New versions are presumed compatible until proven otherwise.
- **Pyxel engine floor:** 2.8.7 — earlier versions lack `pyxel.gen_bgm` (added 2.9.0 syntax change) and `pyxel.set_btnv` headless input (used by pyxel-mcp's `play_and_capture`).
- **Pyxel engine ceiling:** open.
- **Python floor:** 3.10 (uses `from __future__ import annotations` plus 3.10+ syntax in hooks; pyxel-mcp itself requires ≥3.10).

## Reporting compatibility issues

If pyxel-skill produces broken output on a newer pyxel-mcp or Pyxel engine, file an issue with:

- Versions of pyxel-skill, pyxel-mcp, Pyxel, Python.
- The validation prompt used.
- The contents of `screenshots/result/<N>/gate-report.json` (or note that no bundle was produced).
- The contents of `MEMORY.md` (gotchas the agent recorded during the run).

A new row is added to the matrix once the issue is diagnosed and either pyxel-skill is updated or the version pair is documented as incompatible.
