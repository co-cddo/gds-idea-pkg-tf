import os
import shutil
import subprocess
import sys

import click


def _execute_command(command: list[str], capture_output=False):
    try:
        completed_process = subprocess.run(command, check=True, capture_output=capture_output, text=True)
    except subprocess.CalledProcessError:
        sys.exit(1)

    return completed_process


def _init():
    command = ["terraform", "init", "--upgrade"]
    _execute_command(command)
    subfolder = "modules"
    if os.path.isdir(subfolder):
        modules = [d for d in os.listdir(subfolder) if os.path.isdir(os.path.join(subfolder, d))]
        for module in modules:
            command = ["terraform", f"-chdir={subfolder}/{module}", "init", "--upgrade"]
            _execute_command(command)


def _fmt():
    command = ["terraform", "fmt", "--recursive"]
    _execute_command(command)


def _plan():
    command = ["terraform", "plan", "-out", "tf.plan"]
    _execute_command(command)


def _show():
    command = ["terraform", "show", "-no-color", "tf.plan"]
    completed_process = _execute_command(command, capture_output=True)
    with open("tfplan.txt", "w") as f:
        f.write(completed_process.stdout)


def _apply():
    command = ["terraform", "apply", "tf.plan"]
    _execute_command(command)


def _clear():
    folder_rm = ".terraform"
    file_rm = ".terraform.lock.hcl"
    dirs = os.listdir()
    if folder_rm in dirs:
        click.echo(f"remove {folder_rm} folder")
        shutil.rmtree(folder_rm)
    if file_rm in dirs:
        click.echo(f"remove {file_rm} file")
        os.remove(file_rm)

    subfolder = "modules"
    if os.path.isdir(subfolder):
        modules = [d for d in os.listdir(subfolder) if os.path.isdir(os.path.join(subfolder, d))]
        for module in modules:
            dirs = os.listdir(os.path.join(subfolder, module))
            if folder_rm in dirs:
                click.echo(f"remove modules/{module}/{folder_rm} folder")
                shutil.rmtree(os.path.join(subfolder, module, folder_rm))
            if file_rm in dirs:
                click.echo(f"remove modules/{module}/{file_rm} file")
                os.remove(os.path.join(subfolder, module, file_rm))


def _cache():
    os.makedirs(os.path.join(os.path.expanduser("~"), "backup", "terraform-cache"), exist_ok=True)

    with open(os.path.join(os.path.expanduser("~"), ".terraformrc"), "w") as f:
        f.write('plugin_cache_dir = "$HOME/backup/terraform-cache"' + "\n")
        f.write("disable_checkpoint = true" + "\n")
        f.write("plugin_cache_may_break_dependency_lock_file = true")


def _workspace(workspace):
    click.echo("Available workspaces:")
    command = ["terraform", "workspace", "list"]
    _execute_command(command)

    if workspace == "dev":
        workspace = "development"
    elif workspace == "prod":
        workspace = "production"

    command = ["terraform", "workspace", "select", workspace]
    _execute_command(command)

    click.echo("Current workspace:")
    command = ["terraform", "workspace", "show"]
    _execute_command(command)
