"""Exercise the shipped server configuration and documented audio request."""

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

ROOT = Path(__file__).resolve().parent
GAME = ROOT / "tests" / "fixtures" / "skill_game.py"


@pytest.fixture(scope="module")
def server_parameters(tmp_path_factory):
    """A stale installed tool must not override the bundled minimum version."""
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
        [uv, "tool", "install", "pyxel-mcp==1.2.0"],
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
            "import importlib.metadata; print(importlib.metadata.version('pyxel-mcp'))",
        ],
        env=env,
        check=True,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert installed.stdout.strip() == "1.2.0"

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
        version = tuple(int(part) for part in info["pyxel_mcp_version"].split(".")[:3])
        assert version >= (1, 3, 0), info

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


def test_documented_audio_request_renders_wav(server_parameters, tmp_path):
    reference = (ROOT / "references" / "pyxel.md").read_text()
    audio = re.search(r"^## Audio\n(.*?)(?=^## |\Z)", reference, re.MULTILINE | re.DOTALL)
    assert audio is not None, "Missing audio reference"
    blocks = re.findall(r"```json\s*\n(.*?)\n```", audio.group(1), flags=re.DOTALL)
    assert len(blocks) == 1, "Keep one executable request in the audio reference"
    request = json.loads(blocks[0])
    # Preserve the documented target and all other fields so invalid API names fail.
    for key in ("script", "output_path"):
        assert isinstance(request[key], str) and request[key], key
    request["script"] = str(GAME)
    request["output_path"] = str(tmp_path / "sound.wav")

    async def exercise(session):
        _, data = await _call(session, "read_audio", request)
        assert [note["note"] for note in data["notes"]] == ["C2", "D2", "E2", "rest"]
        assert data["peak_amplitude"] > 0, data
        assert data["duration_seconds"] > 0, data
        assert Path(data["path"]) == Path(request["output_path"]).resolve()
        with wave.open(data["path"], "rb") as wav:
            assert wav.getnframes() > 0
            assert wav.getframerate() == data["sample_rate"]
            assert wav.getnchannels() == data["channels"]

    _run(server_parameters, exercise)
