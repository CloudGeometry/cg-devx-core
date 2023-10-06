#!/usr/bin/env python
"""
CG DevX CLI
"""

import click

from commands.destroy import destroy
from commands.setup import setup
from commands.workload.workload import workload


@click.group()
def entry_point():
    pass


entry_point.add_command(setup)
entry_point.add_command(destroy)
entry_point.add_command(workload)

if __name__ == '__main__':
    entry_point()
