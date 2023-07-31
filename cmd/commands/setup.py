import click

from cmd.common.const.const import GITOPS_REPOSITORY_URL, GITOPS_REPOSITORY_BRANCH
from cmd.common.enums.cloud_providers import CloudProviders
from cmd.common.enums.dns_registrars import DnsRegistrars
from cmd.common.enums.git_providers import GitProviders

"""  
    (optional) cloud profile OR cloud key+cloud secret
    
    (optional) setup-demo-workload
    (hidden) gitops-template-url
    (hidden) gitops-template-branch"""


@click.command()
@click.option('--email', '-e', 'email', help='Email address used for alerts', type=click.STRING, prompt=True)
@click.option('--cloud-provider', '-c', 'cloud_provider', help='Cloud provider type',
              type=click.Choice([e.value for e in CloudProviders], case_sensitive=False), prompt=True)
@click.option('--cloud-profile', '-cp', 'cloud_profile', help='Cloud account profile', default='default',
              type=click.STRING)
@click.option('--cloud-account-key', '-cc', 'cloud_key', help='Cloud account access key', type=click.STRING)
@click.option('--cloud-account-secret', '-cs', 'cloud_secret', help='Cloud account access secret', type=click.STRING)
@click.option('--cloud-region', '-r', 'cloud_region', help='Cloud regions', type=click.STRING, prompt=True)
@click.option('--cluster-name', '-n', 'cluster_name', help='Cluster name', default='cg-devx-cc', type=click.STRING,
              prompt=True)
@click.option('--dns-registrar', '-d', 'dns_reg', help='DNS registrar',
              type=click.Choice([e.value for e in DnsRegistrars], case_sensitive=False), prompt=True)
@click.option('--dns-registrar-token', '-dt', 'dns_reg_token', help='DNS registrar token', type=click.STRING)
@click.option('--dns-registrar-key', '-dk', 'dns_reg_key', help='DNS registrar key', type=click.STRING)
@click.option('--dns-registrar-secret', '-ds', 'dns_reg_secret', help='DNS registrar secret', type=click.STRING)
@click.option('--domain-name', '-dn', 'domain', help='Domain-name', type=click.STRING, prompt=True)
@click.option('--git-provider', '-g', 'git_provider', help='Git provider', default=GitProviders.GitHub,
              type=click.Choice([e.value for e in GitProviders], case_sensitive=False))
@click.option('--git-org', '-go', 'git_org', help='Git organization name', type=click.STRING, prompt=True)
@click.option('--git-access-token', '-gt', 'git_token', help='Git access token', type=click.STRING, prompt=True)
@click.option('--gitops-repo-name', '-grn', 'gitops_repo_name', help='GitOps repository name', default='gitops',
              type=click.STRING)
@click.option('--gitops-template-url', '-gtu', 'gitops_template_url', help='GitOps repository template url',
              default=GITOPS_REPOSITORY_URL, type=click.STRING)
@click.option('--gitops-template-branch', '-gtb', 'gitops_template_branch', help='GitOps repository template branch',
              default=GITOPS_REPOSITORY_BRANCH, type=click.STRING)
@click.option('--setup-demo-workload', '-dw', 'install_demo', help='Setup demo workload', default=False,
              flag_value='setup-demo')
@click.option('--config-file', '-f', 'config', help='Load parameters from file', type=click.File())
def setup(email: str, cloud_provider: CloudProviders, cloud_profile: str, cloud_key: str, cloud_secret: str,
          cloud_region: str, cluster_name: str, dns_reg: DnsRegistrars, dns_reg_token: str, dns_reg_key: str,
          dns_reg_secret: str, domain: str, git_provider: GitProviders, git_org: str, git_token: str,
          gitops_repo_name: str, gitops_template_url: str, gitops_template_branch: str, install_demo: bool, config):
    """Creates new CG DevX installation."""
    click.echo("Setup CG DevX installation.")
