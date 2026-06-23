"""Repository-level checks for stale public skill content."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SKILL_MD = ROOT / "SKILL.md"
README_MD = ROOT / "README.md"
PYXEL_NOTES_MD = ROOT / "pyxel-notes.md"
ALLOWED_FRONTMATTER_KEYS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
STALE_PATTERNS = [
    "inspect_",
    "render_audio",
    "compare_frames",
    "run_and_capture",
    "0.10.0",
    "0.9.3",
    "v0.2.0",
    "Donkey",
    "DK",
    "Mario",
    "Princess",
    "princess",
    "barrel",
    "barrels",
    "girder",
    "girders",
    "hammer",
    "hammers",
    "13-check",
    "15-check",
    "docs/superpowers",
    "superpowers/",
    "publish-skill",
    "bundled copy",
]


def test_public_markdown_has_no_stale_tool_or_validation_lore():
    offenders: list[str] = []
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        text = path.read_text().lower()
        for pattern in STALE_PATTERNS:
            if pattern.lower() in text:
                offenders.append(f"{path.relative_to(ROOT)}: {pattern}")

    assert offenders == []


def test_skill_frontmatter_uses_spec_fields():
    lines = SKILL_MD.read_text().splitlines()
    assert lines[0] == "---"
    end = lines.index("---", 1)
    keys = {
        line.split(":", 1)[0]
        for line in lines[1:end]
        if line and not line.startswith(" ") and ":" in line
    }

    assert "version" not in keys
    assert keys <= ALLOWED_FRONTMATTER_KEYS
    assert "metadata" in keys
    assert any(line == '  version: "1.1.0"' for line in lines[1:end])


def test_skill_frontmatter_name_matches_install_contract():
    lines = SKILL_MD.read_text().splitlines()
    end = lines.index("---", 1)
    fields = {
        line.split(":", 1)[0]: line.split(":", 1)[1].strip().strip('"')
        for line in lines[1:end]
        if line and not line.startswith(" ") and ":" in line
    }
    name = fields["name"]
    description = fields["description"]
    compatibility = fields["compatibility"]
    readme = README_MD.read_text()

    assert re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?", name)
    assert "--" not in name
    assert len(description) <= 1024
    assert len(compatibility) <= 500
    assert "must be named `pyxel`" in readme
    assert "~/.agents/skills/pyxel" in readme


def test_skill_default_surface_stays_lean():
    forbidden = {
        "visual-target.md",
        "decomposer.md",
        "scaffold.md",
        "asset-planner.md",
        "asset-gen.md",
        "task-execution.md",
        "quality-gate.md",
        "test-harness.md",
        "capture.md",
        "quirks.md",
    }
    present = {p.name for p in ROOT.glob("*.md")}
    assert forbidden.isdisjoint(present)
    assert not (ROOT / "knowledge").exists()
    assert not (ROOT / "hooks").exists()
    assert not any(p.is_file() for p in (ROOT / "docs").rglob("*"))

    words = SKILL_MD.read_text().split()
    assert len(words) <= 850

    assert (ROOT / "strict-mode.md").is_file()
    assert (ROOT / "pyxel-notes.md").is_file()

def test_audio_examples_include_output_path():
    offenders = []
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        text = path.read_text()
        if "read_audio(target=" in text:
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []


def test_skill_examples_do_not_show_placeholder_artifact_paths():
    text = SKILL_MD.read_text()

    assert "output_path=...)" not in text
    assert "output_path=<absolute path>" in text


def test_mcp_unavailable_guidance_prefers_install_over_fallback():
    text = SKILL_MD.read_text().lower()

    assert "uvx pyxel-mcp install" in text
    assert "older than 1.0.0" in text
    assert "temporary fallback" in text
    assert "weaker" in text


def test_visual_verification_requires_task_result_not_nonblank_only():
    text = SKILL_MD.read_text().lower()

    assert "not just nonblank pixels" in text
    assert "task-specific result" in text


def test_rule_heavy_games_prefer_small_logic_tests():
    text = SKILL_MD.read_text().lower()

    assert "rule-heavy" in text
    assert "focused tests" in text


def test_pyxel_notes_require_absolute_artifact_paths():
    text = PYXEL_NOTES_MD.read_text().lower()

    assert "must be expanded absolute paths" in text
    assert "render_path=<absolute path>" in text
    assert "output_path=<absolute path>" in text


def test_readme_install_points_to_github_and_codex_skill_path():
    text = README_MD.read_text()

    assert "from PyPI via `uvx`" in text
    assert "uvx pyxel-mcp install" in text
    assert "pyxel_info" in text
    assert "pyxel-mcp >= 1.0.0" in text
    assert "https://github.com/kitao/pyxel-skill.git" in text
    assert "skill directory used by your client" in text
    assert "~/.agents/skills/pyxel" in text
    assert "${CODEX_HOME:-$HOME/.codex}/skills" in text
    assert "~/.claude/skills/pyxel" in text


def test_local_agent_settings_are_ignored_by_repo():
    ignore = (ROOT / ".gitignore").read_text()
    assert ".claude/" in ignore


def test_superpowers_scratch_dirs_are_not_present():
    assert not (ROOT / "superpowers").exists()
    assert not (ROOT / "docs" / "superpowers").exists()


def test_skill_repo_has_no_mcp_server_or_bundled_distribution_surface():
    forbidden_paths = [
        ROOT / "src" / "pyxel_mcp",
        ROOT / "server.json",
        ROOT / "build_hooks.py",
        ROOT / "skill",
    ]
    assert [str(p.relative_to(ROOT)) for p in forbidden_paths if p.exists()] == []

    forbidden_terms = [
        "publish-skill",
        "pyxel://workflow",
        "bundled copy",
        "bundled skill",
        "workflow resource",
    ]
    offenders = []
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        text = path.read_text().lower()
        for term in forbidden_terms:
            if term.lower() in text:
                offenders.append(f"{path.relative_to(ROOT)}: {term}")
    assert offenders == []
