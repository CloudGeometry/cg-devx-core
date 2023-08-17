#!/usr/bin/env python

"""
CG DevX CLI
"""

__author__ = "Alexander Ulyanov <alexu@cloudgeometry.io>"
__version__ = "0.1.0"
__license__ = "Apache 2.0"

import click

from commands.destroy import destroy
from commands.workload.workload import workload
from commands.setup import setup


@click.group()
def entry_point():
    pass


entry_point.add_command(setup)
entry_point.add_command(destroy)
entry_point.add_command(workload)

if __name__ == '__main__':
    entry_point()
