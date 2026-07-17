"""pytest configuration for the PythonSCAD Python test-suite.

The Python tests come in two flavours:

* Pure-Python unit tests (e.g. ``test_python_vectors.py``) that import the
  code under test directly and need nothing from the build.
* Integration tests that drive a built ``pythonscad`` binary in a
  subprocess. Those need to be told where that binary is, which is what the
  :func:`pythonscad_binary` fixture below provides.

The binary path comes from ``--pythonscad-binary`` or the
``PYTHONSCAD_BINARY`` environment variable (CMake sets the latter when it
registers the ``python-pytest`` test). When neither is given, the
integration tests skip rather than fail, so ``pytest tests/`` still works
from a source checkout with no build.
"""

from __future__ import annotations

import os
import subprocess

import pytest


#: Integration scripts run a full render; give them room on slow CI workers.
RUN_TIMEOUT_SECONDS = 120


def pytest_addoption(parser):
    parser.addoption(
        "--pythonscad-binary",
        action="store",
        default=None,
        help=(
            "Path to the built pythonscad binary used by the integration "
            "tests. Defaults to the PYTHONSCAD_BINARY environment variable."
        ),
    )


@pytest.fixture(scope="session")
def pythonscad_binary(request):
    """Absolute path to the pythonscad binary, or skip if unavailable."""
    path = request.config.getoption("--pythonscad-binary") or os.environ.get(
        "PYTHONSCAD_BINARY"
    )
    if not path:
        pytest.skip(
            "no pythonscad binary given "
            "(pass --pythonscad-binary or set PYTHONSCAD_BINARY)"
        )
    if not os.path.isfile(path):
        pytest.skip(f"pythonscad binary not found: {path}")
    return os.path.abspath(path)


@pytest.fixture
def run_pythonscad(pythonscad_binary, tmp_path):
    """Run a Python program inside the pythonscad interpreter.

    Returns the program's combined stdout+stderr. pythonscad routes the
    embedded interpreter's ``print()`` output to stderr, so callers that look
    for a marker must search both streams -- hence the merge here.

    An output file is always passed so the binary runs headless and exits
    instead of opening the GUI; the program is expected to ``show()``
    something for that export to succeed.
    """

    def _run(program: str, timeout: int = RUN_TIMEOUT_SECONDS) -> str:
        script = tmp_path / "program.py"
        script.write_text(program, encoding="utf-8")
        out_stl = tmp_path / "out.stl"
        proc = subprocess.run(
            [
                pythonscad_binary,
                "--trust-python",
                str(script),
                "-o",
                str(out_stl),
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        combined = (proc.stdout or "") + (proc.stderr or "")

        # A program that cannot run its checks (e.g. the interpreter has no
        # numpy -- it is an optional dependency that binary bundles do not
        # ship) prints a "SKIP: <reason>" line and bails out early. That path
        # legitimately exits non-zero: bailing out means never calling show(),
        # so the -o export has no top-level object, and sys.exit() surfaces as
        # a SystemExit inside the embedded interpreter. Honour the marker
        # before looking at the return code, or every skip reads as a failure.
        for line in combined.splitlines():
            if line.startswith("SKIP:"):
                pytest.skip(line[len("SKIP:"):].strip())

        assert proc.returncode == 0, (
            f"pythonscad exited with {proc.returncode}\n--- output ---\n{combined}"
        )
        return combined

    return _run
