"""Exercise the shipped server configuration with Pyxel 3, Cube, and audio."""

from __future__ import annotations

import asyncio
import base64
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import wave
from pathlib import Path

import pytest
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from packaging.specifiers import SpecifierSet
from skills_ref import read_properties

ROOT = Path(__file__).resolve().parent
GAME = ROOT / "tests" / "fixtures" / "skill_game.py"
CUBE_GAME = ROOT / "tests" / "fixtures" / "cube_game.py"


@pytest.fixture(scope="module")
def server_parameters(tmp_path_factory):
    """A stale server or Pyxel must not override the bundled requirements."""
    sandbox = tmp_path_factory.mktemp("skill-runtime")
    temporary = sandbox / "tmp"
    temporary.mkdir()
    env = {
        **os.environ,
        "UV_TOOL_DIR": str(sandbox / "tools"),
        "UV_TOOL_BIN_DIR": str(sandbox / "bin"),
        "UV_CACHE_DIR": str(sandbox / "cache"),
        "UV_PYTHON": sys.executable,
        "TMPDIR": str(temporary),
        "TMP": str(temporary),
        "TEMP": str(temporary),
        "SDL_VIDEODRIVER": "dummy",
        "SDL_AUDIODRIVER": "dummy",
    }
    for variable in ("PYTHONPATH", "PYTHONHOME"):
        env.pop(variable, None)
    uv = shutil.which("uv")
    assert uv is not None, "Install uv to run the MCP integration tests"
    installation = subprocess.run(
        [uv, "tool", "install", "pyxel-mcp==1.3.0", "--with", "pyxel==2.9.6"],
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert installation.returncode == 0, installation.stderr
    tool_python = Path(env["UV_TOOL_DIR"]) / "pyxel-mcp" / (
        "Scripts/python.exe" if os.name == "nt" else "bin/python"
    )
    installed = subprocess.run(
        [
            str(tool_python),
            "-c",
            "import importlib.metadata as m; "
            "print(m.version('pyxel-mcp'), m.version('pyxel'))",
        ],
        env=env,
        check=True,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert installed.stdout.strip() == "1.3.0 2.9.6"

    config = json.loads((ROOT / ".mcp.json").read_text())["mcpServers"]["pyxel"]
    return StdioServerParameters(
        command=config["command"],
        args=config["args"],
        env=env,
        cwd=sandbox,
    )


async def _with_server(parameters, exercise):
    # stdio_client closes the pipes and terminates the child on success or failure.
    async with stdio_client(parameters) as (reader, writer):
        async with ClientSession(reader, writer, read_timeout_seconds=120) as session:
            await session.initialize()
            await exercise(session)


def _run(parameters, exercise):
    asyncio.run(asyncio.wait_for(_with_server(parameters, exercise), timeout=180))


async def _call(session, name, arguments):
    result = await session.call_tool(name, arguments)
    assert not result.is_error, result.content
    data = result.structured_content
    assert data is not None, result.content
    assert data["ok"], data
    assert not data["errors"], data
    return result, data


def test_bundled_server_runs_seeded_input_and_inline_capture(server_parameters):
    async def exercise(session):
        _, info = await _call(session, "pyxel_info", {})
        requirements = read_properties(ROOT).metadata
        assert info["pyxel_mcp_version"] in SpecifierSet(requirements["pyxel-mcp"]), info
        assert info["pyxel_version"] in SpecifierSet(requirements["pyxel"]), info

        request = {
            "script": str(GAME),
            "frames": 10,
            "random_seed": 7,
            "inputs": [
                {"frame": 0, "buttons": ["KEY_RIGHT"]},
                {"frame": 1, "buttons": ["KEY_RIGHT", "KEY_SPACE"]},
                {"frame": 2, "buttons": ["KEY_RIGHT"]},
            ],
            "until": "x == 4 and presses == 1",
            "snapshots": [
                {
                    "kind": "state",
                    "frame": "end",
                    "attrs": ["x", "presses", "module_random", "pyxel_random"],
                },
                {"kind": "screen_image", "frame": "end", "inline": True, "scale": 2},
            ],
        }
        observations = []
        for _ in range(2):
            response, data = await _call(session, "run", request)
            assert data["exit_status"] == "ok", data
            assert data["until_met"] is True, data
            assert data["seeded"] is True, data
            assert data["frame_count"] == 4, data
            state = next(s for s in data["snapshots"] if s["kind"] == "state")
            assert not state["warnings"], state
            assert state["frame"] == 3, state
            assert state["values"]["x"] == 4, state
            assert state["values"]["presses"] == 1, state
            images = [item for item in response.content if item.type == "image"]
            assert len(images) == 1, response.content
            assert images[0].mime_type == "image/png"
            png = base64.b64decode(images[0].data, validate=True)
            assert png.startswith(b"\x89PNG\r\n\x1a\n")
            assert struct.unpack(">II", png[16:24]) == (64, 48)
            image_path = Path(
                next(
                    s["path"]
                    for s in data["snapshots"]
                    if s["kind"] == "screen_image"
                )
            )
            assert image_path.read_bytes() == png
            observations.append((state["values"], png))
        assert observations[0] == observations[1]

    _run(server_parameters, exercise)


def test_cube_input_state_and_rendering(server_parameters, tmp_path):
    async def exercise(session):
        _, info = await _call(session, "pyxel_info", {})
        assert Path(info["cube_stubs_path"]).is_file()
        example = next(e for e in info["examples"] if e["name"] == "cube/c01_hello_cube")
        source = await session.read_resource(f"pyxel://examples/{example['name']}")
        assert source.contents[0].text == Path(example["path"]).read_text()

        _, api = await _call(session, "lookup_api", {"name": "cube.Camera"})
        assert "clear_color" in api["members"]
        assert api["declarations"]

        _, validation = await _call(session, "validate", {"script": str(CUBE_GAME)})
        assert not any(issue["severity"] == "error" for issue in validation["issues"])

        response, data = await _call(session, "run", {
            "script": str(CUBE_GAME),
            "frames": 10,
            "inputs": [{"frame": 0, "buttons": ["KEY_RIGHT"]}],
            "until": "box.transform.pos.x >= 4",
            "snapshots": [
                {"kind": "state", "frame": "end", "attrs": ["box.transform.pos.x"]},
                {"kind": "screen_grid", "frame": "end"},
                {
                    "kind": "screen_image", "frames": [0, 3], "inline": True,
                    "output_pattern": str(tmp_path / "cube-{frame}.png"), "scale": 2,
                },
            ],
        })
        assert data["exit_status"] == "ok", data
        assert data["until_met"] is True, data
        assert data["frame_count"] == 4, data
        state = next(s for s in data["snapshots"] if s["kind"] == "state")
        assert not state["warnings"], state
        assert state["values"]["box.transform.pos.x"] == pytest.approx(4), state
        grid = next(s for s in data["snapshots"] if s["kind"] == "screen_grid")
        # Camera clears to 1; the box draws in 11. This catches an empty viewport.
        assert {color for row in grid["grid"] for color in row} == {1, 11}
        images = [base64.b64decode(item.data) for item in response.content if item.type == "image"]
        assert len(images) == 2, response.content
        assert all(struct.unpack(">II", png[16:24]) == (128, 96) for png in images)
        assert images[0] != images[1], "Moving the Cube node should change its rendered pixels"

    _run(server_parameters, exercise)


def _documented_requests(reference, field):
    source = (ROOT / "references" / reference).read_text()
    examples = [
        json.loads(block)
        for block in re.findall(r"```json\s*\n(.*?)\n```", source, flags=re.DOTALL)
    ]
    requests = [example for example in examples if field in example]
    assert requests, f"No example with {field} in {reference}"
    return requests


async def _platformer(session):
    _, info = await _call(session, "pyxel_info", {})
    return Path(next(e["path"] for e in info["examples"] if e["name"] == "10_platformer"))


@pytest.mark.parametrize("example", _documented_requests("playtesting.md", "inputs"))
def test_documented_platformer_replay(server_parameters, example):
    async def exercise(session):
        script = await _platformer(session)
        assert Path(example["script"]).name == script.name
        request = {**example, "script": str(script)}
        response, moving = await _call(session, "run", request)
        assert moving["exit_status"] == "ok"
        assert moving["until_met"] is True
        state = next(s for s in moving["snapshots"] if s["kind"] == "state")
        assert not state["warnings"]
        assert state["values"]["__main__.player.x"] >= 16
        assert any(item.type == "image" for item in response.content)

        _, idle = await _call(session, "run", {**request, "inputs": []})
        assert idle["exit_status"] == "ok"
        assert idle["until_met"] is False
        state = next(s for s in idle["snapshots"] if s["kind"] == "state")
        assert state["values"]["__main__.player.x"] == 0

    _run(server_parameters, exercise)


@pytest.mark.parametrize("example", _documented_requests("pyxel.md", "target"))
def test_documented_resource_audio_returns_inline_wav(server_parameters, example):
    async def exercise(session):
        resource = (await _platformer(session)).parent / "assets" / "platformer.pyxres"
        assert Path(example["script"]).suffix == resource.suffix
        response, data = await _call(session, "read_audio", {**example, "script": str(resource)})
        audio = next(item for item in response.content if item.type == "audio")
        assert audio.mime_type == "audio/wav"
        assert base64.b64decode(audio.data, validate=True) == Path(data["path"]).read_bytes()
        assert data["peak_amplitude"] > 0
        assert data["duration_seconds"] > 0
        with wave.open(data["path"], "rb") as wav:
            assert wav.getnframes() > 0
            assert wav.getframerate() == data["sample_rate"]
            assert wav.getnchannels() == data["channels"]

    _run(server_parameters, exercise)


@pytest.mark.parametrize("example", _documented_requests("pyxel.md", "tilemap"))
def test_documented_tile_selection_matches_its_source_art(server_parameters, example):
    async def exercise(session):
        directory = (await _platformer(session)).parent
        resource = directory / "assets" / Path(example["script"]).name
        request = {**example, "script": str(resource)}
        response, row = await _call(session, "read_tilemap", request)
        assert any(item.type == "image" for item in response.content)
        x, y, w, h = request["bbox"]
        assert row["sampled_region"] == {"x": x, "y": y, "w": w, "h": h}
        assert len(row["tiles"]) == h
        assert all(len(line) == w for line in row["tiles"])
        u, v = row["tiles"][0][0]

        _, cell = await _call(session, "read_tilemap", {**request, "bbox": [x, y, 1, 1]})
        _, sprite = await _call(session, "read_image", {
            "script": str(resource), "image": row["imgsrc"],
            "x": 8 * u, "y": 8 * v, "w": 8, "h": 8, "inline": True,
        })
        _, diff = await _call(session, "diff_frames", {
            "frame_a": cell["rendered"], "frame_b": sprite["rendered"],
        })
        assert diff["identical"] is True

    _run(server_parameters, exercise)


def test_script_audio_tracker_fields(server_parameters, tmp_path):
    async def exercise(session):
        output = tmp_path / "sound.wav"
        _, data = await _call(session, "read_audio", {
            "script": str(GAME), "target": {"sound": 0}, "output_path": str(output),
        })
        assert Path(data["path"]) == output.resolve()
        assert [note["note"] for note in data["notes"]] == ["C2", "D2", "E2", "rest"]
        assert [note["tone"] for note in data["notes"]] == ["t", "p", "t", "p"]
        assert [note["volume"] for note in data["notes"]] == [1, 7, 1, 7]
        assert [note["effect"] for note in data["notes"]] == ["n", "h", "q", "n"]

    _run(server_parameters, exercise)
