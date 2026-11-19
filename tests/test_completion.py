"""Tests for the bash completion script: drift from the parser, and what Tab offers."""

from __future__ import annotations

import shutil
import subprocess
import tomllib
from pathlib import Path

import pytest

from bump_version.cli import _create_parser
from bump_version.completion import render_bash

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "completions" / "bump-version.bash"


def test_shipped_script_matches_parser() -> None:
    assert SCRIPT.read_text(encoding="utf-8") == render_bash(_create_parser()), (
        "completions/bump-version.bash is stale; run `make completions`"
    )


def test_wheel_ships_script_where_bash_completion_looks() -> None:
    with open(REPO / "pyproject.toml", "rb") as fh:
        shared = tomllib.load(fh)["tool"]["hatch"]["build"]["targets"]["wheel"]["shared-data"]
    assert shared == {
        "completions/bump-version.bash": "share/bash-completion/completions/bump-version.bash"
    }


def _bash() -> str | None:
    """A bash new enough for the script (mapfile is bash 4+), or None."""
    bash = shutil.which("bash")
    if bash is None:
        return None
    major = subprocess.run(
        [bash, "-c", "echo ${BASH_VERSINFO[0]}"],
        capture_output=True,
        encoding="utf-8",
        check=True,
    ).stdout.strip()
    return bash if int(major) >= 4 else None


BASH = _bash()


def _tab(*words: str) -> list[str]:
    """What Tab offers with the cursor on the last of ``bump-version WORDS``."""
    assert BASH is not None
    words_literal = " ".join(f"'{w}'" for w in ("bump-version", *words))
    program = (
        f"source '{SCRIPT}'\n"
        f"COMP_WORDS=({words_literal}); COMP_CWORD={len(words)}\n"
        "_bump_version; printf '%s\\n' \"${COMPREPLY[@]}\"\n"
    )
    out = subprocess.run(
        [BASH, "-c", program], capture_output=True, encoding="utf-8", check=True
    ).stdout
    return [line for line in out.splitlines() if line]


needs_bash = pytest.mark.skipif(BASH is None, reason="needs bash 4 or later")


@needs_bash
@pytest.mark.parametrize(
    ("words", "expected"),
    [
        ([""], ["major", "minor", "patch", "current", "dynamic-pyproject"]),
        (["m"], ["major", "minor"]),
        (["minor", "--p"], ["--push", "--prefix"]),
        (["dynamic-pyproject", "--"], ["--help", "--dry-run", "--yes", "--prefix"]),
        (["patch", "-m", ""], []),  # a message is free text
        (["-m", "major", ""], ["major", "minor", "patch", "current", "dynamic-pyproject"]),
    ],
)
def test_tab_offers(words: list[str], expected: list[str]) -> None:
    assert _tab(*words) == expected


@needs_bash
def test_top_level_options_include_version() -> None:
    assert "--version" in _tab("--")
    assert "--version" not in _tab("patch", "--")
