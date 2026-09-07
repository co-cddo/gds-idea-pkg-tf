"""Tests for tf.tf."""

import subprocess
from unittest.mock import MagicMock

import pytest

from tf import tf


@pytest.fixture
def mock_execute_command(monkeypatch):
    """Replace tf._execute_command so higher-level functions can be tested in isolation."""
    mock = MagicMock()
    monkeypatch.setattr(tf, "_execute_command", mock)
    return mock


class TestExecuteCommand:
    def test_success_returns_completed_process(self, monkeypatch):
        completed = subprocess.CompletedProcess(args=["echo", "hi"], returncode=0, stdout="hi")
        mock_run = MagicMock(return_value=completed)
        monkeypatch.setattr(tf.subprocess, "run", mock_run)

        result = tf._execute_command(["echo", "hi"])

        assert result is completed
        mock_run.assert_called_once_with(["echo", "hi"], check=True, capture_output=False, text=True)

    def test_success_forwards_capture_output(self, monkeypatch):
        mock_run = MagicMock(return_value=subprocess.CompletedProcess(args=[], returncode=0))
        monkeypatch.setattr(tf.subprocess, "run", mock_run)

        tf._execute_command(["terraform", "show"], capture_output=True)

        mock_run.assert_called_once_with(["terraform", "show"], check=True, capture_output=True, text=True)

    def test_failure_exits_with_code_one(self, monkeypatch):
        mock_run = MagicMock(side_effect=subprocess.CalledProcessError(1, ["terraform"]))
        monkeypatch.setattr(tf.subprocess, "run", mock_run)

        with pytest.raises(SystemExit) as exc_info:
            tf._execute_command(["terraform", "plan"])

        assert exc_info.value.code == 1


class TestInit:
    def test_without_modules_subfolder(self, tmp_path, monkeypatch, mock_execute_command):
        monkeypatch.chdir(tmp_path)

        tf._init()

        mock_execute_command.assert_called_once_with(["terraform", "init", "--upgrade"])

    def test_with_modules_subfolder(self, tmp_path, monkeypatch, mock_execute_command):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "modules" / "network").mkdir(parents=True)
        (tmp_path / "modules" / "app").mkdir(parents=True)
        (tmp_path / "modules" / "not_a_dir.txt").write_text("x")

        tf._init()

        calls = [c.args[0] for c in mock_execute_command.call_args_list]
        assert calls[0] == ["terraform", "init", "--upgrade"]
        assert ["terraform", "-chdir=modules/network", "init", "--upgrade"] in calls
        assert ["terraform", "-chdir=modules/app", "init", "--upgrade"] in calls
        assert len(calls) == 3


def test_fmt(mock_execute_command):
    tf._fmt()

    mock_execute_command.assert_called_once_with(["terraform", "fmt", "--recursive"])


def test_plan(mock_execute_command):
    tf._plan()

    mock_execute_command.assert_called_once_with(["terraform", "plan", "-out", "tf.plan"])


def test_apply(mock_execute_command):
    tf._apply()

    mock_execute_command.assert_called_once_with(["terraform", "apply", "tf.plan"])


class TestShow:
    def test_writes_stdout_to_file(self, tmp_path, monkeypatch, mock_execute_command):
        monkeypatch.chdir(tmp_path)
        mock_execute_command.return_value = subprocess.CompletedProcess(args=[], returncode=0, stdout="plan output")

        tf._show()

        mock_execute_command.assert_called_once_with(["terraform", "show", "-no-color", "tf.plan"], capture_output=True)
        assert (tmp_path / "tfplan.txt").read_text() == "plan output"


class TestClear:
    def test_removes_folder_and_file(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".terraform").mkdir()
        (tmp_path / ".terraform.lock.hcl").write_text("lock")

        tf._clear()

        assert not (tmp_path / ".terraform").exists()
        assert not (tmp_path / ".terraform.lock.hcl").exists()
        captured = capsys.readouterr()
        assert "remove .terraform folder" in captured.out
        assert "remove .terraform.lock.hcl file" in captured.out

    def test_noop_when_nothing_to_remove(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)

        tf._clear()

        assert capsys.readouterr().out == ""

    def test_removes_from_modules_subfolder(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        module_dir = tmp_path / "modules" / "network"
        module_dir.mkdir(parents=True)
        (module_dir / ".terraform").mkdir()
        (module_dir / ".terraform.lock.hcl").write_text("lock")

        tf._clear()

        assert not (module_dir / ".terraform").exists()
        assert not (module_dir / ".terraform.lock.hcl").exists()
        captured = capsys.readouterr()
        assert "remove modules/network/.terraform folder" in captured.out
        assert "remove modules/network/.terraform.lock.hcl file" in captured.out


class TestCache:
    def test_creates_terraformrc_and_cache_dir(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))

        tf._cache()

        cache_dir = tmp_path / "backup" / "terraform-cache"
        rc_file = tmp_path / ".terraformrc"
        assert cache_dir.is_dir()
        assert rc_file.is_file()
        content = rc_file.read_text()
        assert 'plugin_cache_dir = "$HOME/backup/terraform-cache"' in content
        assert "disable_checkpoint = true" in content
        assert "plugin_cache_may_break_dependency_lock_file = true" in content


class TestWorkspace:
    @pytest.mark.parametrize(
        ("shortcut", "expected"),
        [
            ("dev", "development"),
            ("prod", "production"),
        ],
    )
    def test_shortcut_expands_to_full_name(self, shortcut, expected, mock_execute_command):
        tf._workspace(shortcut)

        select_call = mock_execute_command.call_args_list[1].args[0]
        assert select_call == ["terraform", "workspace", "select", expected]

    def test_passthrough_workspace_name(self, mock_execute_command):
        tf._workspace("staging")

        select_call = mock_execute_command.call_args_list[1].args[0]
        assert select_call == ["terraform", "workspace", "select", "staging"]

    def test_calls_list_select_show_in_order(self, mock_execute_command):
        tf._workspace("dev")

        calls = [c.args[0] for c in mock_execute_command.call_args_list]
        assert calls == [
            ["terraform", "workspace", "list"],
            ["terraform", "workspace", "select", "development"],
            ["terraform", "workspace", "show"],
        ]
