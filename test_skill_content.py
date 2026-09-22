"""Distribution contracts; editorial guidance is reviewed as prose."""

from __future__ import annotations

import json
import re
import shlex
from pathlib import Path
from urllib.parse import unquote, urlsplit

from skills_ref import read_properties

ROOT = Path(__file__).resolve().parent


def test_release_metadata_agrees():
    skill = read_properties(ROOT)
    plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
    assert skill.name == plugin["name"] == "pyxel"
    assert skill.license == plugin["license"] == "MIT"
    version = plugin["version"]
    assert skill.metadata["version"] == version
    readme = (ROOT / "README.md").read_text()
    rows = [
        [cell.strip() for cell in line.strip("|").split("|")]
        for line in readme.splitlines()
        if line.startswith("|")
    ]
    release = [row for row in rows if row[0] == version]
    assert len(release) == 1, "Current release must have a compatibility row"
    assert release[0][1].replace(" ", "") == skill.metadata["pyxel-mcp"]
    releases = re.findall(r"^## (\S+)", (ROOT / "CHANGELOG.md").read_text(), re.MULTILINE)
    assert releases[0] == version


def test_local_document_links_resolve():
    documents = [*ROOT.glob("*.md"), *(ROOT / "references").rglob("*.md")]
    for document in documents:
        for target in re.findall(r"\]\(([^\s)]+)\)", document.read_text()):
            link = urlsplit(target)
            if link.scheme or link.netloc or not link.path:
                continue
            path = document.parent / unquote(link.path)
            assert path.exists(), f"Broken link in {document.name}: {target}"


def test_bundled_command_matches_documented_requirement():
    skill = read_properties(ROOT)
    config = json.loads((ROOT / ".mcp.json").read_text())
    server = config["mcpServers"]["pyxel"]
    command = ["uvx", "--from", f"pyxel-mcp{skill.metadata['pyxel-mcp']}", "pyxel-mcp"]
    assert [server["command"], *server["args"]] == command
    for name in ("SKILL.md", "README.md"):
        assert shlex.join(command) in (ROOT / name).read_text(), name


def test_marketplace_resolves_to_the_plugin():
    marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
    plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
    entry = next(item for item in marketplace["plugins"] if item["name"] == plugin["name"])
    assert (ROOT / entry["source"]).resolve() == ROOT
    if "version" in entry:
        assert entry["version"] == plugin["version"]
