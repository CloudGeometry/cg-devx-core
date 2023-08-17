import click


@click.command()
@click.option('--workload-name', '-w', 'wl_name', help='Workload name', type=click.STRING, prompt=True)
def delete(wl_name: str):
    """Deletes all the workload boilerplate."""
    click.echo("Delete workload.")
