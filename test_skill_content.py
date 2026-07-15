"""Structural and contract checks for the public skill."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SKILL = ROOT / "SKILL.md"
README = ROOT / "README.md"
REFERENCES = ROOT / "references"


def _frontmatter() -> tuple[dict[str, str], list[str]]:
    lines = SKILL.read_text().splitlines()
    assert lines[0] == "---"
    end = lines.index("---", 1)
    fields = {
        line.split(":", 1)[0]: line.split(":", 1)[1].strip().strip('"')
        for line in lines[1:end]
        if line and not line.startswith(" ") and ":" in line
    }
    return fields, lines[1:end]


def _skill_markdown() -> list[Path]:
    return [SKILL, *sorted(REFERENCES.glob("*.md"))]


def test_skill_frontmatter_is_valid_and_current():
    fields, lines = _frontmatter()
    assert set(fields) == {"name", "description", "license", "metadata"}
    assert fields["name"] == "pyxel"
    assert re.fullmatch(r"[a-z0-9-]{1,64}", fields["name"])
    assert "Pyxel" in fields["description"]
    assert len(fields["description"]) <= 1024
    assert '  version: "1.3.0"' in lines

    body = SKILL.read_text()
    assert "pyxel-mcp 1.2+" in body
    assert "Python 3.11" in body
    assert "--refresh-package pyxel-mcp" in body


def test_skill_payload_has_one_shallow_reference_layer():
    assert {path.name for path in REFERENCES.glob("*.md")} == {
        "pyxel.md",
        "strict-mode.md",
    }
    assert not (ROOT / "pyxel-notes.md").exists()
    assert not (ROOT / "strict-mode.md").exists()
    assert not any(path.is_file() for path in REFERENCES.glob("*/*"))

    main = SKILL.read_text()
    assert "references/pyxel.md" in main
    assert "references/strict-mode.md" in main
    assert len(main.split()) <= 550


def test_skill_matches_the_eight_tool_v2_contract():
    text = "\n".join(path.read_text() for path in _skill_markdown())
    for tool in [
        "validate",
        "run",
        "pyxel_info",
        "read_palette",
        "read_image",
        "read_tilemap",
        "read_audio",
        "diff_frames",
    ]:
        assert f"`{tool}`" in text

    for removed in [
        "read_animation",
        "layout snapshot",
        "ASSERT PASS",
        "universal quality score",
        "pyxel://anti-patterns",
    ]:
        assert removed not in text
    assert "pyxel://validation-patterns" in text


def test_default_loop_requires_direct_mechanical_and_visual_evidence():
    text = SKILL.read_text().lower()
    assert "state" in text and "screen_image" in text
    assert "inspect" in text and "captured" in text
    assert "task-specific" in text
    assert "validate clean" not in text
    assert "relevant warnings" in text
    assert "log field" in text
    assert "run.log" not in text
    assert "even when" in text and "ok" in text


def test_references_are_progressive_and_task_specific():
    main = SKILL.read_text().lower()
    pyxel = (REFERENCES / "pyxel.md").read_text().lower()
    strict = (REFERENCES / "strict-mode.md").read_text().lower()

    assert "read" in main and "only when" in main
    assert "absolute" in pyxel
    assert "lowercase" in pyxel and ".png" in pyxel
    assert "pyxel.btnp" in pyxel and "colkey=0" in pyxel
    assert "replaces" in pyxel and "release" in pyxel
    assert "attribute paths" in pyxel and "expressions" in pyxel and "self." in pyxel
    assert "random.random" in pyxel and "explicit" in pyxel
    assert "runtime" in pyxel and "not auditioned" in pyxel
    assert "opt-in" in strict
    assert "proof" in strict and "release" in strict


def test_readme_is_human_installation_not_a_second_skill():
    text = README.read_text()
    assert "v1.3.0" in text
    assert "pyxel-mcp >= 1.2.0" in text
    assert "Python >= 3.11" in text
    assert "uvx pyxel-mcp install" in text
    assert "npx skills add kitao/pyxel-skill" in text
    assert "https://github.com/kitao/pyxel-skill.git" in text
    assert "must be named `pyxel`" in text
    assert "~/.agents/skills/pyxel" in text
    assert "${CODEX_HOME:-$HOME/.codex}/skills" in text
    assert "~/.claude/skills/pyxel" in text
    assert "## Default Loop" not in text


def test_repo_contains_no_server_or_distribution_plumbing():
    forbidden = [
        ROOT / "src" / "pyxel_mcp",
        ROOT / "server.json",
        ROOT / "build_hooks.py",
        ROOT / "hooks",
        ROOT / "knowledge",
    ]
    assert [str(path.relative_to(ROOT)) for path in forbidden if path.exists()] == []

    text = "\n".join(path.read_text().lower() for path in _skill_markdown())
    for term in ["publish-skill", "pyxel://workflow", "bundled skill"]:
        assert term not in text


def test_local_agent_state_is_ignored():
    ignore = (ROOT / ".gitignore").read_text()
    assert ".claude/" in ignore
    assert ".superpowers/" in ignore
