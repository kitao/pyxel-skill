# pyxel-skill

[![Tests](https://img.shields.io/github/actions/workflow/status/kitao/pyxel-skill/test.yml?branch=main&label=tests)](https://github.com/kitao/pyxel-skill/actions/workflows/test.yml)
[![Agent Skills](https://img.shields.io/badge/Agent_Skills-spec_compliant-blue)](https://agentskills.io/specification)
[![License](https://img.shields.io/github/license/kitao/pyxel-skill)](LICENSE)

An [Agent Skill](https://agentskills.io) for making and playtesting [Pyxel](https://kitao.dev/pyxel/) games in Python, from 2D sprites and tilemaps to Pyxel Cube scenes. It uses [pyxel-mcp](https://github.com/kitao/pyxel-mcp) to look up the installed API, play a game with scheduled input, inspect its frames, or read artwork and sound directly from a resource file.

## Install

### Claude Code plugin

```bash
claude plugin marketplace add kitao/pyxel-skill
claude plugin install pyxel@pyxel-skill
```

The plugin includes both the skill (`/pyxel:pyxel`) and the `pyxel` MCP server configuration. The server uses `uvx`, provided by [uv](https://docs.astral.sh/uv/).

### Other skill installations

With the skills CLI, run the following command and choose your client.

```bash
npx skills add kitao/pyxel-skill
```

For manual installation, clone this repository into your client's skills directory under the name `pyxel`, or symlink a shared clone there. For example, for Codex:

```bash
git clone https://github.com/kitao/pyxel-skill.git "${CODEX_HOME:-$HOME/.codex}/skills/pyxel"
```

### MCP setup

If your client already lists the bundled `pyxel` server, use that registration. Otherwise register the following stdio command with your client.

```bash
uvx --from 'pyxel-mcp>=1.5.0' pyxel-mcp
```

For Codex CLI, the registration command is:

```bash
codex mcp add pyxel -- uvx --from 'pyxel-mcp>=1.5.0' pyxel-mcp
```

Append `install` to the server command to print configuration examples for other clients. Keep the version requirement in the command you register. Restart your client and call `pyxel_info`. The server needs Python 3.11+ and installs Pyxel as a dependency. The Python environment you use to launch your game is separate.

If the installed versions are too old, update the plugin or existing server registration, refresh the packages, and restart the client.

```bash
uvx --refresh-package pyxel-mcp --refresh-package pyxel --from 'pyxel-mcp>=1.5.0' pyxel-mcp install
```

## Try it

- “Build a Pyxel game where I collect falling stars. Make the stars readable against the night sky and show me a frame from a catch.”
- “When I scroll, my score disappears. Reproduce it, fix it, and check the HUD while I'm moving.”
- “Show me eight tiles starting at (0, 17) in tilemap 0 of the bundled platformer. Which image bank do they use?”

The [skill](SKILL.md) links to guides for [game design](references/design.md), [2D graphics and sound](references/pyxel.md), [Cube](references/cube.md), and [playtesting](references/playtesting.md). The playtesting example works with the platformer included in Pyxel.

## Development

```bash
pip install pytest skills-ref uv 'mcp>=2,<3'
pytest -q
```

The integration tests need network access. They start the bundled server in an isolated uv tool directory containing an older installation and exercise the documented requests against published packages. To run only the distribution checks, use `pytest -q test_skill_content.py`.

Run `agentskills validate /path/to/skills/pyxel` on an installation named `pyxel`, and `claude plugin validate .` for the plugin manifest.

## Compatibility

| pyxel-skill | pyxel-mcp | Pyxel | Python |
|---|---|---|---|
| 1.6.0 | >= 1.5.0 | >= 3.0.3 | >= 3.11 |
| 1.5.0 | >= 1.4.0 | >= 3.0.1 | >= 3.11 |
| 1.4.3 | >= 1.3.1 | >= 2.9.6 | >= 3.11 |
| 1.4.2 | >= 1.3.1 | >= 2.9.6 | >= 3.11 |
| 1.4.1 | >= 1.3.0 | >= 2.9.6 | >= 3.11 |
| 1.4.0 | >= 1.3.0 | >= 2.9.6 | >= 3.11 |
| 1.3.0 | >= 1.2.0 | >= 2.9.6 | >= 3.11 |

See the [migration notes](references/pyxel.md#older-projects-and-distribution) before upgrading a Pyxel 2 project. See [CHANGELOG.md](CHANGELOG.md) for the skill's version history.

## License

[MIT](LICENSE)
