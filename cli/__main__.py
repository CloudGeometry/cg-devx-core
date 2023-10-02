#!/usr/bin/env python
"""
CG DevX CLI
"""

import click

from cli.commands.destroy import destroy
from cli.commands.setup import setup
from cli.commands.workload.workload import workload


@click.group()
def entry_point():
    pass


entry_point.add_command(setup)
entry_point.add_command(destroy)
entry_point.add_command(workload)

if __name__ == '__main__':
    entry_point()
