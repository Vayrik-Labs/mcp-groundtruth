"""`mcpgt demo`: the bundled fixture runs with no setup and shows a VIOLATION."""

import importlib.resources
import tempfile
from pathlib import Path

from mcpgt import cli
from mcpgt.provenance import git_state

FIXTURE = Path(__file__).parent.parent / "fixtures" / cli.DEMO


def test_packaged_demo_is_identical_to_the_fixture():
    packaged = importlib.resources.files("mcpgt") / "demo" / cli.DEMO
    files = {p.name: p.read_bytes() for p in FIXTURE.iterdir() if p.is_file()}
    bundled = {p.name: p.read_bytes() for p in packaged.iterdir() if p.is_file()}
    assert bundled == files


def test_demo_shows_a_violation_and_exits_0(capsys, monkeypatch):
    # The demo runs from a temporary copy: no git checkout around it, so
    # provenance must cope without a commit for the definition.
    assert git_state(Path(tempfile.gettempdir())) == (None, None)
    written = []
    real_write = cli.reports.write
    monkeypatch.setattr(
        cli.reports, "write", lambda report, runs_dir: written.append(report) or real_write(report, runs_dir)
    )

    assert cli.main(["demo"]) == cli.EXIT_OK
    out = capsys.readouterr().out
    assert "concurrent_idempotence" in out
    assert "VIOLATION" in out
    assert "mcpgt init my-server" in out
    (report,) = written
    definition = report["provenance"]["definition"]
    assert definition["git_sha"] is None
    assert definition["content_sha256"]
