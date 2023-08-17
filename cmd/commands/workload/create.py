import click


@click.command()
@click.option('--workload-name', '-w', 'wl_name', help='Workload name', type=click.STRING, prompt=True)
@click.option('--workload-repository-name', '-wrn', 'wl_repo_name', help='Workload repository name', type=click.STRING,
              prompt=True)
@click.option('--workload-gitops-repository-name', '-wgrn', 'wl_gitops_repo_name',
              help='Workload GitOps repository name', type=click.STRING, prompt=True)
@click.option('--workload-template-url', '-wtu', 'wl_template_url', help='Workload repository template',
              type=click.STRING)
@click.option('--workload-template-branch', '-wtb', 'wl_template_branch', help='Workload repository template',
              type=click.STRING)
@click.option('--workload-gitops-template-url', '-wgu', 'wl_gitops_template_url',
              help='Workload GitOps repository template', type=click.STRING)
@click.option('--workload-gitops-template-branch', '-wgb', 'wl_gitops_template_branch',
              help='Workload GitOps repository template',
              type=click.STRING)
def create(wl_name: str, wl_repo_name: str, wl_gitops_repo_name: str, wl_template_url: str, wl_template_branch: str,
           wl_gitops_template_url: str, wl_gitops_template_branch: str):
    """Create workload boilerplate."""
    click.echo("Create workload.")
