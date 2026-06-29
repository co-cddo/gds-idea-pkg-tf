import os
import shutil
import subprocess

import click


def _execute_command(command: list[str]):
    try:
        completed_process = subprocess.run(command, check=True, capture_output=False, text=True)
    except subprocess.CalledProcessError as e:
        raise e

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
    command = ["terraform", "show", "-no-color", "tf.plan", ">", "tfplan.txt"]
    _execute_command(command)


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
