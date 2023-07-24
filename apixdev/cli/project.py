import sys

import click

from apixdev.cli.tools import abort_if_false, print_list
from apixdev.core.odoo import Odoo
from apixdev.core.project import Project


@click.group()
def pj():
    """Manage apix project"""


@click.command()
@click.argument("name")
@click.option("--local", "-l", is_flag=True, help="Create blank project")
def new(name, **kwargs):
    """Create new project"""

    is_local = kwargs.get("local", False)
    database = False
    urls = []

    project = Project(name)

    if not is_local:
        odoo = Odoo.new()
        database = odoo.get_databases(name, strict=True, limit=1)

        if not database:
            click.echo(f"No '{name}' database found.")
            project.delete()
            sys.exit(1)

        urls = [
            ("manifest.yaml", database.manifest_url),
            ("repositories.yaml", database.repositories_url),
            ("docker-compose.yaml", database.compose_url),
        ]

        for name, url in urls:
            try:
                project.download(name, url)
            except Exception as error:
                click.echo(error)
                sys.exit(1)

        project.pull_repositories()
        project.merge_requirements()


@click.command()
@click.option(
    "--yes",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="Are you sure you want to overwrite project ?",
)
@click.argument("name")
def update(name, **kwargs):
    """Update project"""

    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        return False

    project.load_manifest()
    project.pull_repositories()
    project.merge_requirements()


@click.command()
@click.argument("name")
def merge(name, **kwargs):
    """Merge requirements"""

    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        return False

    project.merge_requirements()


@click.command()
@click.argument("name")
def pull(name, **kwargs):
    """Pull repositories"""

    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        return False

    project.pull_repositories()


@click.command()
@click.argument("name")
def search(name, **kwargs):
    """Search for online project"""

    odoo = Odoo.new()
    databases = odoo.get_databases(name, strict=False)
    results = sorted(databases.mapped("name"))

    print_list(results)


@click.command()
@click.option(
    "--yes",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="Are you sure you want to delete project ?",
)
@click.argument("name")
def delete(name, **kwargs):
    """Delete local project"""

    project = Project(name)
    project.delete()


@click.command()
@click.option("--background", "-b", is_flag=True, help="Run on background")
@click.argument("name")
def run(name, **kwargs):
    """Run project"""

    run_on_background = kwargs.get("background", False)
    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        return False

    if run_on_background:
        project.run(detach=True)
    else:
        project.run()
        project.down()


@click.command()
@click.argument("name")
def stop(name):
    """Stop project containers"""

    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        return False

    project.down()


@click.command()
@click.option(
    "--yes",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="Are you sure you want to clear project containers (databsae will be lost) ?",
)
@click.argument("name")
def clear(name, **kwargs):
    """Clear project containers"""

    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        return False

    project.clear()


@click.command()
@click.argument("name")
def show(name):
    """Ps project containers"""

    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        return False

    project.ps()


@click.command()
@click.argument("name")
@click.argument("service")
def logs(name, service):
    """Show container logs"""

    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        return False

    project.logs(service)


@click.command()
@click.argument("name")
def bash(name):
    """Attach to Odoo container bash"""

    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        return False

    project.bash("odoo")


@click.command()
@click.argument("name")
@click.argument("database")
def shell(name, database):
    """Attach to Odoo shell"""

    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        return False

    project.shell(database)


@click.command()
@click.argument("name")
@click.argument("database")
@click.argument("modules")
def install_modules(name, database, modules):
    """Update modules on database"""

    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        return False

    project.update_modules(database, modules, install=True)


@click.command()
@click.argument("name")
@click.argument("database")
@click.argument("modules")
def update_modules(name, database, modules):
    """Update modules on database"""

    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        return False

    project.update_modules(database, modules)


pj.add_command(new)
pj.add_command(update)
pj.add_command(search)
pj.add_command(delete)
pj.add_command(merge)
pj.add_command(pull)
pj.add_command(run)
pj.add_command(stop)
pj.add_command(clear)
pj.add_command(show)
pj.add_command(logs)
pj.add_command(bash)
pj.add_command(shell)
pj.add_command(install_modules)
pj.add_command(update_modules)
