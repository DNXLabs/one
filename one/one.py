#!/usr/bin/env python3

import os, sys
from os import path
from pathlib import Path
import click
from one.docker.image import Image
from one.docker.container import Container
from one.utils.environment import Environment, home, load_environments
from one.__init__ import __version__

if not path.exists(home + '/.one'):
	os.mkdir(home + '/.one')

load_environments()


from one.commands.login import login
from one.commands.terraform import terraform
from one.commands.workspace import workspace
from one.commands.idp import idp


@click.version_option(__version__)
@click.group()
def cli():
	"""CLI to manage all stacks from DNX."""
	pass


cli.add_command(login)
cli.add_command(terraform)
cli.add_command(workspace)
cli.add_command(idp)


if __name__ == "__main__":
	cli()