# Change Log

## 1.4.0

- Require pyxel-mcp 1.3 and look at frames through inline screen images
- Add references/design.md with presentation and game-feel defaults
- Ship a Claude Code plugin manifest that bundles the pyxel-mcp server
- Declare `compatibility` in the frontmatter per the Agent Skills spec
- Document relative asset paths, stall detection, and `until_met` values
- Validate the skill against the Agent Skills specification in CI

## 1.3.0

- Target the eight-tool pyxel-mcp 1.2 contract and drop `read_animation`
- Move Pyxel notes and strict mode under references/

## 1.2.0

- Teach until-based runs and the validation pattern catalog
- Add the `npx skills add` install path and project-scoped install guards
- Add content tests and CI

## 1.1.0

- Refresh the workflow for pyxel-mcp 1.0
- Replace the staged pipeline with one lightweight loop plus strict mode
- Guard the skill's role boundary against server plumbing

## 1.0.0

- Align with pyxel-mcp 0.9.1 and remove duplicated MCP instructions
