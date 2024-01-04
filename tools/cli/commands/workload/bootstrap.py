import time
from typing import Dict

import click

from common.const.const import WL_REPOSITORY_URL, WL_GITOPS_REPOSITORY_URL, WL_GITOPS_REPOSITORY_BRANCH, \
    WL_REPOSITORY_BRANCH
from common.custom_excpetions import WorkloadManagerError
from common.logging_config import configure_logging, logger
from common.state_store import StateStore
from common.utils.command_utils import str_to_kebab, init_cloud_provider
from services.wl_template_manager import WorkloadManager


@click.command()
@click.option('--workload-name', '-wl', 'wl_name', help='Workload name', type=click.STRING, prompt=True)
@click.option(
    '--workload-repository-name',
    '-wlrn',
    'wl_repo_name',
    help='Workload repository name',
    type=click.STRING
)
@click.option(
    '--workload-gitops-repository-name',
    '-wlgrn',
    'wl_gitops_repo_name',
    help='Workload GitOps repository name',
    type=click.STRING
)
@click.option(
    '--workload-template-url',
    '-wltu',
    'wl_template_url',
    help='Workload repository template',
    type=click.STRING,
    default=WL_REPOSITORY_URL
)
@click.option(
    '--workload-template-branch',
    '-wltb',
    'wl_template_branch',
    help='Workload repository template branch',
    type=click.STRING,
    default=WL_REPOSITORY_BRANCH

)
@click.option(
    '--workload-gitops-template-url',
    '-wlgu',
    'wl_gitops_template_url',
    help='Workload GitOps repository template',
    type=click.STRING,
    default=WL_GITOPS_REPOSITORY_URL
)
@click.option(
    '--workload-gitops-template-branch',
    '-wlgb',
    'wl_gitops_template_branch',
    help='Workload GitOps repository template branch',
    type=click.STRING,
    default=WL_GITOPS_REPOSITORY_BRANCH
)
@click.option(
    '--workload-service-name',
    '-wls',
    'wl_svc_name',
    help='Workload service name',
    type=click.STRING
)
@click.option(
    '--workload-service-port',
    '-wlsp',
    'wl_svc_port',
    help='Workload service port',
    type=click.INT,
    default=3000
)
@click.option(
    '--verbosity',
    type=click.Choice(
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        case_sensitive=False
    ),
    default='CRITICAL',
    help='Set the verbosity level (DEBUG, INFO, WARNING, ERROR, CRITICAL)'
)
def bootstrap(
        wl_name: str, wl_repo_name: str, wl_gitops_repo_name: str, wl_template_url: str, wl_template_branch: str,
        wl_gitops_template_url: str, wl_gitops_template_branch: str, wl_svc_name: str, wl_svc_port: int, verbosity: str
):
    """
    Bootstrap a new workload environment by setting up the necessary repositories and configurations.

    This command initializes and configures a workload repository and a GitOps repository based on provided templates.
    It handles the entire setup process, including the cloning of template repositories, parameter customization,
    and finalization of the workload setup.

    Args:
        wl_name (str): The name of the workload.
        wl_repo_name (str): The name of the workload repository.
        wl_gitops_repo_name (str): The name of the GitOps repository for the workload.
        wl_template_url (str): The URL of the template for the workload repository.
        wl_template_branch (str): The branch of the workload repository template.
        wl_gitops_template_url (str): The URL of the template for the GitOps repository.
        wl_gitops_template_branch (str): The branch of the GitOps repository template.
        wl_svc_name (str): The name of the service within the workload.
        wl_svc_port (int): The service port number for the workload service.
        verbosity (str): The logging level for the process (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Raises:
        ClickException: An exception is raised if there are issues in the configuration loading,
        or if the bootstrap process for either the workload or GitOps repository fails.

    Returns:
        None: The function does not return anything but completes the bootstrap process.
    """
    click.echo("Bootstrapping workload...")
    func_start_time = time.time()
    state_store = StateStore()
    configure_logging(verbosity)

    try:
        org_name = state_store.parameters["<GIT_ORGANIZATION_NAME>"]
        key_path = state_store.internals["DEFAULT_SSH_PRIVATE_KEY_PATH"]
        cc_cluster_fqdn = state_store.parameters["<CC_CLUSTER_FQDN>"]
        registry_url = state_store.parameters["<REGISTRY_REGISTRY_URL>"]
        tf_backend_storage_name = state_store.internals["TF_BACKEND_STORAGE_NAME"]
        click.echo("1/10: Configuration loaded.")
    except KeyError as e:
        error_message = f'Configuration loading failed due to missing key: {e}. ' \
                        'Please verify the state store configuration and ensure all required keys are present. ' \
                        'Review the documentation for the necessary configuration keys and try again.'
        logger.error(error_message)
        raise click.ClickException(error_message)

    # Initialize cloud manager for GitOps parameters
    cloud_man, _ = init_cloud_provider(state_store)
    click.echo("2/10: Cloud manager initialized for GitOps.")

    # Initialize WorkloadManager for the workload repository
    wl_name, wl_repo_name, wl_gitops_repo_name = process_workload_names(
        wl_name=wl_name,
        wl_repo_name=wl_repo_name,
        wl_gitops_repo_name=wl_gitops_repo_name
    )
    click.echo("3/10: Workload names processed.")

    # Prepare parameters for workload and GitOps repositories
    wl_repo_params = _prepare_workload_params(wl_name=wl_name, wl_svc_name=wl_repo_name, wl_svc_port=wl_svc_port)
    wl_gitops_params = _prepare_gitops_params(
        wl_name=wl_name,
        wl_svc_name=wl_svc_name,
        wl_svc_port=wl_svc_port,
        cc_cluster_fqdn=cc_cluster_fqdn,
        registry_url=registry_url,
        k8s_role_mapping=cloud_man.create_k8s_cluster_role_mapping_snippet(),
        additional_labels=cloud_man.create_additional_labels(),
        tf_secrets_backend=cloud_man.create_iac_backend_snippet(
            location=tf_backend_storage_name,
            service=f"workloads/{wl_name}/secrets"
        ),
        tf_hosting_backend=cloud_man.create_iac_backend_snippet(
            location=tf_backend_storage_name,
            service=f"workloads/{wl_name}/hosting_provider"
        ),
        hosting_provider_snippet=cloud_man.create_hosting_provider_snippet()
    )
    click.echo("4/10: Parameters for workload and GitOps repositories prepared.")

    # Initialize WorkloadManager for the workload repository
    wl_manager = WorkloadManager(
        org_name=org_name,
        repo_name=wl_repo_name,
        key_path=key_path,
        template_url=wl_template_url,
        template_branch=wl_template_branch
    )
    click.echo("5/10: Workload repository manager initialized.")

    try:
        # Perform bootstrap steps for the workload repository
        perform_bootstrap(
            workload_manager=wl_manager,
            params=wl_repo_params
        )
        click.echo("6/10: Workload repository bootstrap process completed.")
    except WorkloadManagerError as e:
        raise click.ClickException(str(e))

    # Cleanup temporary folder for workload repository
    wl_manager.cleanup()
    click.echo("7/10: Workload repository cleanup completed.")

    # Initialize WorkloadManager for the GitOps repository
    wl_gitops_manager = WorkloadManager(
        org_name=org_name,
        repo_name=wl_gitops_repo_name,
        key_path=key_path,
        template_url=wl_gitops_template_url,
        template_branch=wl_gitops_template_branch
    )
    click.echo("8/10: GitOps repository manager initialized.")

    try:
        # Perform bootstrap steps for the GitOps repositoryR
        perform_bootstrap(
            workload_manager=wl_gitops_manager,
            params=wl_gitops_params
        )
        click.echo("9/10: GitOps repository bootstrap process completed.")
    except WorkloadManagerError as e:
        raise click.ClickException(str(e))

    # Cleanup temporary folder for GitOps repository
    wl_gitops_manager.cleanup()
    click.echo("10/10: GitOps repository cleanup completed.")

    click.echo(f"Bootstrapping workload completed in {time.time() - func_start_time:.2f} seconds.")


def process_workload_names(wl_name: str, wl_repo_name: str, wl_gitops_repo_name: str):
    """
    Process and normalize workload names to a standard format.

    Args:
        wl_name (str): Name of the workload.
        wl_repo_name (str): Name of the workload repository.
        wl_gitops_repo_name (str): Name of the workload GitOps repository.

    Returns:
        tuple[str, str, str]: Tuple of processed workload name, workload repository name, and GitOps repository name.
    """
    processed_wl_name = str_to_kebab(wl_name)
    processed_wl_repo_name = str_to_kebab(wl_repo_name or wl_name)
    processed_wl_gitops_repo_name = str_to_kebab(wl_gitops_repo_name or f"{wl_repo_name}-gitops")

    return processed_wl_name, processed_wl_repo_name, processed_wl_gitops_repo_name


def perform_bootstrap(
        workload_manager: WorkloadManager,
        params: Dict[str, str]
):
    """
    Perform the bootstrap process using the WorkloadManager.

    Args:
        workload_manager (WorkloadManager): The workload manager instance.
        params (Dict[str, str]): Dictionary containing parameters for bootstrap.

    Raises:
        WorkloadManagerError: If cloning, templating, or uploading process fails.
    """
    if not workload_manager.clone_template():
        raise WorkloadManagerError("Failed to clone template repository")

    if not workload_manager.clone_wl():
        raise WorkloadManagerError("Failed to clone workload repository")

    # Bootstrap workload with the given service names
    service_names = [params.get("<WL_SERVICE_NAME>", "default-service")]
    workload_manager.bootstrap(service_names)

    workload_manager.parametrise(params)

    workload_manager.upload(
        author_name=params.get("<AUTHOR_NAME>"),
        author_email=params.get("<AUTHOR_EMAIL>")
    )


def _prepare_workload_params(wl_name: str, wl_svc_name: str, wl_svc_port: str | int):
    """
    Prepare parameters for the workload repository bootstrap process.

    Args:
        wl_name: Workload name.
        wl_svc_name: Workload service name.
        wl_svc_port: Workload service port.

    Returns:
        dict: Dictionary of parameters.
    """
    return {
        "<WL_NAME>": wl_name,
        "<WL_SERVICE_NAME>": wl_svc_name,
        "<WL_SERVICE_PORT>": str(wl_svc_port)
    }


def _prepare_gitops_params(
        wl_name: str,
        wl_svc_name: str,
        wl_svc_port: str | int,
        cc_cluster_fqdn: str,
        registry_url: str,
        k8s_role_mapping: str,
        additional_labels: str,
        tf_secrets_backend: str,
        tf_hosting_backend: str,
        hosting_provider_snippet: str
) -> Dict[str, str]:
    """
    Prepare parameters for the GitOps repository bootstrap process.

    Args:
        wl_name (str): Name of the workload.
        wl_svc_name (str): Name of the workload service.
        wl_svc_port (int): Port number for the workload service.
        cc_cluster_fqdn (str): Fully qualified domain name for the cluster.
        registry_url (str): URL for the registry.
        k8s_role_mapping (str): Kubernetes role mapping snippet.
        additional_labels (str): Additional labels snippet.
        tf_secrets_backend (str): Terraform secrets backend snippet.
        tf_hosting_backend (str): Terraform hosting backend snippet.
        hosting_provider_snippet (str): Hosting provider snippet.

    Returns:
        Dict[str, str]: A dictionary containing prepared parameters for the GitOps repository bootstrap process.
    """
    logger.debug(f"Preparing GitOps parameters for workload '{wl_name}' with service '{wl_svc_name}'.")

    params = {
        "<WL_NAME>": wl_name,
        "<WL_SERVICE_NAME>": wl_svc_name,
        "<WL_SERVICE_URL>": f'{wl_svc_name}.{wl_name}.{cc_cluster_fqdn}',
        "<WL_SERVICE_IMAGE>": f'{registry_url}/{wl_name}/{wl_svc_name}',
        "<WL_SERVICE_PORT>": str(wl_svc_port),
        "<K8S_ROLE_MAPPING>": k8s_role_mapping,
        "<WL_IAM_ROLE_RN>": "[Put your workload service role mapping]",
        "<ADDITIONAL_LABELS>": additional_labels,
        "<TF_WL_SECRETS_REMOTE_BACKEND>": tf_secrets_backend,
        "<TF_WL_HOSTING_REMOTE_BACKEND>": tf_hosting_backend,
        "<TF_HOSTING_PROVIDER>": hosting_provider_snippet,
    }

    logger.debug(f"GitOps parameters prepared: {params}")
    return params
