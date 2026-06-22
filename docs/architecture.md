# pyxel-skill Architecture

`pyxel-skill` is the decision layer for Pyxel game work. It stays lean by delegating observation to `pyxel-mcp` and leaving game-specific judgment to the model.

## Role Split

- **Skill:** choose scope, keep the build loop honest, select genre-specific predicates, inspect captured frames, and decide whether the result satisfies the user's brief.
- **MCP:** run Pyxel headlessly, schedule inputs, capture snapshots, read Pyxel resources, render audio, diff frames, and expose Pyxel docs/resources.
- **Pyxel:** remains the engine and source of truth for APIs, examples, editors, packaging, and runtime behavior.

The skill intentionally does not add MCP tools, mutate client configuration, enforce universal quality scores, or replace Pyxel documentation.

## Loading Model

The default public surface is:

| File | Purpose | When to read |
|---|---|---|
| `SKILL.md` | Trigger, default loop, minimum verification, boundaries | Always |
| `strict-mode.md` | Evidence bundle and release/audit checks | Only when requested or warranted |
| `pyxel-notes.md` | Pyxel-specific footguns | Only when touching the relevant API |

The skill no longer ships a stage pipeline, topical knowledge directory, or stop hook. Those created too much policy before the model had observed the actual game.

## Verification Contract

A normal game task needs `validate`, at least one smoke `run`, at least one visually inspected `screen_image`, and one predicate from state or resource observations. Larger tasks can add strict-mode evidence, but strict mode is an escalation path, not the default.
