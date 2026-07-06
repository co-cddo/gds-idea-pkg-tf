import click


@click.group()
@click.pass_context
@click.version_option(prog_name="tf", package_name="gds-idea-pkg-tf")
def cli(ctx):
    """tf - terraform alias."""


@cli.command()
def init():
    """'terraform init --upgrade' command executed in working folder and modules subfolders"""
    from tf.prerequisites import _check_prerequisites
    from tf.tf import _init

    _check_prerequisites()
    _init()


@cli.command()
def fmt():
    """'terraform fmt --recursive' command executed"""
    from tf.tf import _fmt

    _fmt()


@cli.command()
def plan():
    """'terraform plan -out tf.plan' command executed"""
    from tf.tf import _plan

    _plan()


@cli.command()
def show():
    """'terraform show -no-color tf.plan > tfplan.txt' command executed"""
    from tf.tf import _show

    _show()


@cli.command()
def apply():
    """'terraform apply tf.plan' command executed"""
    from tf.tf import _apply

    _apply()


@cli.command()
def clear():
    """removes '.terraform' folders and  '.terraform.lock.hcl' files in working folder and modules subfolders"""
    from tf.tf import _clear

    _clear()


@cli.command()
def cache():
    """creates .terraformrc file and required folders to cache tf providers"""
    from tf.tf import _cache

    _cache()


@cli.command()
@click.argument("workspace", default="dev")
def w(workspace: str):
    """show or select workspace"""
    from tf.tf import _workspace

    _workspace(workspace)
