import click


@click.command()
def destroy():
    """Destroy existing CG DevX installation."""
    click.echo("Destroy CG DevX installation.")
