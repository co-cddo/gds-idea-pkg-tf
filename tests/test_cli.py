"""Tests for tf.cli."""

from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from tf.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_group_help(runner):
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "terraform alias" in result.output


def test_cli_version(runner):
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert "tf" in result.output


def test_init_command_checks_prerequisites_then_inits(runner, monkeypatch):
    check_prerequisites = MagicMock()
    init = MagicMock()
    monkeypatch.setattr("tf.prerequisites._check_prerequisites", check_prerequisites)
    monkeypatch.setattr("tf.tf._init", init)

    result = runner.invoke(cli, ["init"])

    assert result.exit_code == 0
    check_prerequisites.assert_called_once_with()
    init.assert_called_once_with()


def test_fmt_command(runner, monkeypatch):
    fmt = MagicMock()
    monkeypatch.setattr("tf.tf._fmt", fmt)

    result = runner.invoke(cli, ["fmt"])

    assert result.exit_code == 0
    fmt.assert_called_once_with()


def test_plan_command(runner, monkeypatch):
    plan = MagicMock()
    monkeypatch.setattr("tf.tf._plan", plan)

    result = runner.invoke(cli, ["plan"])

    assert result.exit_code == 0
    plan.assert_called_once_with()


def test_show_command(runner, monkeypatch):
    show = MagicMock()
    monkeypatch.setattr("tf.tf._show", show)

    result = runner.invoke(cli, ["show"])

    assert result.exit_code == 0
    show.assert_called_once_with()


def test_apply_command(runner, monkeypatch):
    apply_ = MagicMock()
    monkeypatch.setattr("tf.tf._apply", apply_)

    result = runner.invoke(cli, ["apply"])

    assert result.exit_code == 0
    apply_.assert_called_once_with()


def test_clear_command(runner, monkeypatch):
    clear = MagicMock()
    monkeypatch.setattr("tf.tf._clear", clear)

    result = runner.invoke(cli, ["clear"])

    assert result.exit_code == 0
    clear.assert_called_once_with()


def test_cache_command(runner, monkeypatch):
    cache = MagicMock()
    monkeypatch.setattr("tf.tf._cache", cache)

    result = runner.invoke(cli, ["cache"])

    assert result.exit_code == 0
    cache.assert_called_once_with()


def test_workspace_command_defaults_to_dev(runner, monkeypatch):
    workspace = MagicMock()
    monkeypatch.setattr("tf.tf._workspace", workspace)

    result = runner.invoke(cli, ["w"])

    assert result.exit_code == 0
    workspace.assert_called_once_with("dev")


def test_workspace_command_accepts_argument(runner, monkeypatch):
    workspace = MagicMock()
    monkeypatch.setattr("tf.tf._workspace", workspace)

    result = runner.invoke(cli, ["w", "prod"])

    assert result.exit_code == 0
    workspace.assert_called_once_with("prod")
