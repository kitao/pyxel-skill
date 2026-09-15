"""Structural and contract checks for the public skill."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL = ROOT / "SKILL.md"
README = ROOT / "README.md"
CHANGELOG = ROOT / "CHANGELOG.md"
REFERENCES = ROOT / "references"
PLUGIN = ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
MCP_CONFIG = ROOT / ".mcp.json"

VERSION = "1.4.1"
MCP_MINIMUM = "1.3.0"
TOOLS = [
    "validate",
    "run",
    "pyxel_info",
    "read_palette",
    "read_image",
    "read_tilemap",
    "read_audio",
    "diff_frames",
]


def _frontmatter() -> tuple[dict[str, str], str]:
    lines = SKILL.read_text().splitlines()
    assert lines[0] == "---"
    end = lines.index("---", 1)
    fields = {
        line.split(":", 1)[0]: line.split(":", 1)[1].strip().strip('"')
        for line in lines[1:end]
        if line and not line.startswith(" ") and ":" in line
    }
    return fields, "\n".join(lines[1:end])


def _body() -> str:
    text = SKILL.read_text()
    return text.split("---", 2)[2]


def _skill_markdown() -> list[Path]:
    return [SKILL, *sorted(REFERENCES.glob("*.md"))]


def test_frontmatter_follows_the_agent_skills_spec():
    fields, raw = _frontmatter()
    assert set(fields) == {"name", "description", "license", "compatibility", "metadata"}
    assert fields["name"] == "pyxel"
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", fields["name"])
    assert "Pyxel" in fields["description"] and "Do not use" in fields["description"]
    assert 1 <= len(fields["description"]) <= 1024
    assert "pyxel-mcp" in fields["compatibility"] and "1.3" in fields["compatibility"]
    assert 1 <= len(fields["compatibility"]) <= 500
    assert fields["license"] == "MIT"
    assert f'  version: "{VERSION}"' in raw
    assert f'  pyxel-mcp: ">={MCP_MINIMUM}"' in raw


def test_body_is_short_with_one_shallow_reference_layer():
    assert len(_body().split()) <= 550
    assert {path.name for path in REFERENCES.glob("*.md")} == {
        "pyxel.md",
        "design.md",
        "strict-mode.md",
    }
    assert not any(path.is_file() for path in REFERENCES.glob("*/*"))
    body = _body()
    for name in ("pyxel.md", "design.md", "strict-mode.md"):
        assert f"](references/{name})" in body


def test_runtime_contract_matches_pyxel_mcp():
    body = _body()
    for tool in TOOLS:
        assert f"`{tool}`" in body
    assert "eight observation tools" in body
    assert f"below {MCP_MINIMUM}" in body
    assert "uvx pyxel-mcp install" in body
    assert "--refresh-package pyxel-mcp" in body

    text = "\n".join(path.read_text() for path in _skill_markdown())
    for removed in [
        "read_animation",
        "layout snapshot",
        "ASSERT PASS",
        "universal quality score",
        "pyxel://anti-patterns",
        "pyxel-mcp 1.2+",
    ]:
        assert removed not in text


def test_default_loop_requires_direct_mechanical_and_visual_evidence():
    body = _body().lower()
    assert "inline: true" in body and "scale` 2 to 4" in body
    assert "`state` for mechanics" in body
    assert "random_seed" in body and "input schedule" in body
    assert "until" in body and '"frame": "end"' in body
    assert "read `log` even when `ok` is true" in body
    assert "non-blank screen is not evidence" in body
    assert "task-specific" in body
    assert "not auditioned" in body
    assert "relevant warnings" in body


def test_references_are_task_specific():
    pyxel = (REFERENCES / "pyxel.md").read_text().lower()
    design = (REFERENCES / "design.md").read_text().lower()
    strict = (REFERENCES / "strict-mode.md").read_text().lower()

    assert "inline: true" in pyxel and "12 inline images" in pyxel
    assert "must be absolute" in pyxel and ".png" in pyxel
    assert "pyxel.btnp" in pyxel and "colkey=0" in pyxel
    assert "attribute paths" in pyxel and "self." in pyxel
    assert "random.random" in pyxel and "explicit seed" in pyxel
    assert "relative asset paths" in pyxel and "script's directory" in pyxel
    assert "stall_window_frames" in pyxel and "until_met" in pyxel
    assert "images[0].set" in pyxel
    assert "not auditioned" in pyxel

    assert "solid black" in design and "palette" in design
    assert "feedback" in design and "channel 3" in design
    assert "inline frame" in design

    assert "opt-in" in strict and "proof" in strict
    assert "explicit `output` paths" in strict


def test_plugin_manifest_bundles_skill_and_server():
    plugin = json.loads(PLUGIN.read_text())
    assert plugin["name"] == "pyxel"
    assert plugin["version"] == VERSION
    assert plugin["license"] == "MIT"
    assert plugin["repository"] == "https://github.com/kitao/pyxel-skill"
    assert "skills" not in plugin  # the root SKILL.md is the single skill

    marketplace = json.loads(MARKETPLACE.read_text())
    assert marketplace["name"] == "pyxel-skill"
    assert marketplace["owner"]["name"]
    assert marketplace["metadata"]["description"]
    assert [entry["name"] for entry in marketplace["plugins"]] == ["pyxel"]
    assert marketplace["plugins"][0]["source"] == "./"
    assert "version" not in marketplace["plugins"][0]  # plugin.json is the source of truth

    servers = json.loads(MCP_CONFIG.read_text())["mcpServers"]
    assert servers == {"pyxel": {"command": "uvx", "args": ["pyxel-mcp"]}}


def test_readme_and_changelog_agree_with_the_skill():
    readme = README.read_text()
    assert f"Version {VERSION} targets pyxel-mcp >= {MCP_MINIMUM}" in readme
    assert f"| {VERSION} | >= {MCP_MINIMUM} | >= 2.9.6 | >= 3.11 |" in readme
    assert "claude plugin marketplace add kitao/pyxel-skill" in readme
    assert "claude plugin install pyxel@pyxel-skill" in readme
    assert "npx skills add kitao/pyxel-skill" in readme
    assert "uvx pyxel-mcp install" in readme
    assert "must be named `pyxel`" in readme
    assert "~/.agents/skills/pyxel" in readme
    assert "${CODEX_HOME:-$HOME/.codex}/skills" in readme
    assert "~/.claude/skills/pyxel" in readme
    assert "## Default Loop" not in readme

    changelog = CHANGELOG.read_text()
    assert changelog.startswith("# Change Log\n\n## " + VERSION + "\n")
    for line in changelog.splitlines():
        assert len(line) <= 80, line


def test_repo_contains_no_server_or_distribution_plumbing():
    forbidden = [
        ROOT / "src" / "pyxel_mcp",
        ROOT / "server.json",
        ROOT / "build_hooks.py",
        ROOT / "hooks",
        ROOT / "knowledge",
        ROOT / "skills",
    ]
    assert [str(path.relative_to(ROOT)) for path in forbidden if path.exists()] == []

    text = "\n".join(path.read_text().lower() for path in _skill_markdown())
    for term in ["publish-skill", "pyxel://workflow", "bundled skill"]:
        assert term not in text


def test_local_agent_state_is_ignored():
    ignore = (ROOT / ".gitignore").read_text()
    assert ".claude/" in ignore
    assert ".superpowers/" in ignore
