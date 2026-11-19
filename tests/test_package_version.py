"""Tests for ``bump_version.__version__``: the installed version, or a marked fallback."""

from __future__ import annotations

import importlib.metadata
import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

import bump_version

INIT = Path(bump_version.__file__)


def _fresh_package() -> ModuleType:
    """Execute the package's ``__init__.py`` as a new, unregistered module.

    A fresh module rather than ``importlib.reload``: reloading would rebind
    ``bump_version.__version__`` under every other test in the session.
    """
    spec = importlib.util.spec_from_file_location("_bump_version_under_test", INIT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_version_is_the_installed_distributions() -> None:
    assert bump_version.__version__ == importlib.metadata.version("bump-version")


def test_version_falls_back_when_the_distribution_is_not_installed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _not_installed(name: str) -> str:
        raise importlib.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(importlib.metadata, "version", _not_installed)
    assert _fresh_package().__version__ == "0.0.0+unknown"
