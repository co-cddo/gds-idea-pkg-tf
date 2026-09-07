"""Tests for tf.prerequisites."""

import subprocess
from unittest.mock import MagicMock

import pytest

from tf.prerequisites import _check_prerequisites


def test_check_prerequisites_all_present(monkeypatch):
    """When every check command succeeds, nothing is raised."""
    monkeypatch.setattr("tf.prerequisites.subprocess.run", MagicMock())

    _check_prerequisites()


def test_check_prerequisites_missing_tool_exits(monkeypatch):
    """A missing executable (FileNotFoundError) causes a hard exit."""
    monkeypatch.setattr(
        "tf.prerequisites.subprocess.run",
        MagicMock(side_effect=FileNotFoundError),
    )

    with pytest.raises(SystemExit) as exc_info:
        _check_prerequisites()

    assert exc_info.value.code == 1


def test_check_prerequisites_called_process_error_exits(monkeypatch):
    """A non-zero exit from the check command also causes a hard exit."""
    monkeypatch.setattr(
        "tf.prerequisites.subprocess.run",
        MagicMock(side_effect=subprocess.CalledProcessError(1, ["terraform", "--version"])),
    )

    with pytest.raises(SystemExit) as exc_info:
        _check_prerequisites()

    assert exc_info.value.code == 1


def test_check_prerequisites_prints_missing_tools(monkeypatch, capsys):
    """The install hint for each missing tool is reported to stderr."""
    monkeypatch.setattr(
        "tf.prerequisites.subprocess.run",
        MagicMock(side_effect=FileNotFoundError),
    )

    with pytest.raises(SystemExit):
        _check_prerequisites()

    captured = capsys.readouterr()
    assert "terraform" in captured.err
    assert "brew install tfenv" in captured.err


def test_check_prerequisites_only_filter_runs_matching(monkeypatch):
    """The `only` filter restricts which prerequisites are checked."""
    run = MagicMock()
    monkeypatch.setattr("tf.prerequisites.subprocess.run", run)

    _check_prerequisites(only=["terraform"])

    run.assert_called_once()


def test_check_prerequisites_only_filter_excludes_non_matching(monkeypatch):
    """Tools not present in the `only` filter are skipped entirely."""
    run = MagicMock()
    monkeypatch.setattr("tf.prerequisites.subprocess.run", run)

    _check_prerequisites(only=["nonexistent-tool"])

    run.assert_not_called()
