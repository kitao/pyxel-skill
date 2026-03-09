# pyxel-skill

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill for building retro games with [Pyxel](https://github.com/kitao/pyxel).

## What is this?

This skill teaches Claude Code how to create retro-style games using the Pyxel game engine. It covers Pyxel conventions, color palettes, sprite design, audio, and a visual-verification workflow powered by [pyxel-mcp](https://github.com/kitao/pyxel-mcp).

## Prerequisites

Install the pyxel-mcp MCP server. Add to your Claude Code MCP configuration (`~/.claude/.mcp.json`):

```json
{
  "mcpServers": {
    "pyxel": {
      "command": "uvx",
      "args": ["pyxel-mcp"]
    }
  }
}
```

## Installation

Copy or symlink `SKILL.md` into your Claude Code skills directory:

```bash
# Option 1: Symlink (auto-updates with git pull)
ln -s /path/to/pyxel-skill/SKILL.md ~/.claude/skills/pyxel.md

# Option 2: Copy
cp /path/to/pyxel-skill/SKILL.md ~/.claude/skills/pyxel.md
```

## Usage

Once installed, Claude Code will automatically activate this skill when you ask it to create Pyxel games. For example:

- "Make a simple shooting game with Pyxel"
- "Create a retro platformer"
- "Build an 8-bit puzzle game with chiptune music"

## Links

- [Pyxel](https://github.com/kitao/pyxel) — The retro game engine
- [pyxel-mcp](https://github.com/kitao/pyxel-mcp) — MCP server for AI-assisted Pyxel development
- [anthropics/skills](https://github.com/anthropics/skills) — Claude Code community skills collection

## License

MIT
