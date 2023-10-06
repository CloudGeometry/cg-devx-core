import click

from .bootstrap import bootstrap
from .create import create
from .delete import delete


@click.group()
def workload():
    pass


workload.add_command(bootstrap)
workload.add_command(create)
workload.add_command(delete)
