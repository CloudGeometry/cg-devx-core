import shutil
import time
import webbrowser
from typing import Dict

import click

from common.const.common_path import LOCAL_WORKLOAD_TEMP_FOLDER
from common.const.const import WL_REPOSITORY_URL, WL_GITOPS_REPOSITORY_URL, WL_GITOPS_REPOSITORY_BRANCH, \
    TERRAFORM_VERSION, WL_PR_BRANCH_NAME_PREFIX, WL_REPOSITORY_BRANCH, WL_SERVICE_NAME
from common.custom_excpetions import WorkloadManagerError, GitBranchAlreadyExists
from common.enums.cloud_providers import CloudProviders
from common.logging_config import configure_logging, logger
from common.state_store import StateStore
from common.utils.command_utils import init_cloud_provider, preprocess_workload_names, \
    init_git_provider, construct_wl_iam_role
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
    type=click.STRING,
    default=WL_SERVICE_NAME
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
        dockerhub_proxy = state_store.parameters["<REGISTRY_DOCKERHUB_PROXY>"]
        gcr_proxy = state_store.parameters["<REGISTRY_GCR_PROXY>"]
        k8s_gcr_proxy = state_store.parameters["<REGISTRY_K8S_GCR_PROXY>"]
        quay_proxy = state_store.parameters["<REGISTRY_QUAY_PROXY>"]
        git_runner_group_name = state_store.parameters["<GIT_RUNNER_GROUP_NAME>"]
        git_organisation_name = state_store.parameters["<GIT_ORGANIZATION_NAME>"]
        cluster_name = state_store.parameters["<PRIMARY_CLUSTER_NAME>"]
        cloud_account = state_store.internals["CLOUD_ACCOUNT"]
        domain_name = state_store.parameters["<DOMAIN_NAME>"]
        cloud_region = state_store.parameters["<CLOUD_REGION>"]
        owner_email = state_store.parameters["<OWNER_EMAIL>"]
        ci_iam_role_rn = state_store.parameters["<CI_IAM_ROLE_RN>"]
        artifact_store = state_store.parameters["<CLOUD_BINARY_ARTIFACTS_STORE>"]
        ci_ingress_url = state_store.parameters["<CI_INGRESS_URL>"]

        click.echo("1/11: Configuration loaded.")
    except KeyError as e:
        error_message = f'Configuration loading failed due to missing key: {e}. ' \
                        'Please verify the state store configuration and ensure all required keys are present. ' \
                        'Review the documentation for the necessary configuration keys and try again.'
        logger.error(error_message)
        raise click.ClickException(error_message)

    # Initialize cloud manager for GitOps parameters
    cloud_man, _ = init_cloud_provider(state_store)
    click.echo("2/11: Cloud manager initialized for GitOps.")

    # Initialize WorkloadManager for the workload repository
    wl_name, wl_repo_name, wl_gitops_repo_name = preprocess_workload_names(
        logger=logger,
        wl_name=wl_name,
        wl_repo_name=wl_repo_name,
        wl_gitops_repo_name=wl_gitops_repo_name
    )
    click.echo("3/11: Workload names processed.")

    # Prepare parameters for workload and GitOps repositories
    wl_repo_params = {
        "<WL_NAME>": wl_name,
        "<WL_SERVICE_NAME>": wl_svc_name,
        "<REGISTRY_REGISTRY_URL>": registry_url,
        "<REGISTRY_DOCKERHUB_PROXY>": dockerhub_proxy,
        "<REGISTRY_GCR_PROXY>": gcr_proxy,
        "<REGISTRY_K8S_GCR_PROXY>": k8s_gcr_proxy,
        "<REGISTRY_QUAY_PROXY>": quay_proxy,
        "<WL_REPO_NAME>": wl_repo_name,
        "<WL_GITOPS_REPO_NAME>": wl_gitops_repo_name,
        "<GIT_ORGANIZATION_NAME>": git_organisation_name,
        "<GIT_RUNNER_GROUP_NAME>": git_runner_group_name,
        "<CI_INGRESS_URL>": ci_ingress_url,
    }

    wl_gitops_params = {
        "<WL_NAME>": wl_name,
        "<WL_SERVICE_NAME>": wl_svc_name,
        "<WL_SERVICE_URL>": f'{wl_svc_name}.{wl_name}.{cc_cluster_fqdn}',
        "<WL_SERVICE_IMAGE>": f'{registry_url}/{wl_name}/{wl_svc_name}',
        "<WL_SERVICE_PORT>": str(wl_svc_port),
        "# <K8S_ROLE_MAPPING>": cloud_man.create_k8s_cluster_role_mapping_snippet(),
        "# <ADDITIONAL_LABELS>": cloud_man.create_additional_labels(),
        "# <TF_WL_SECRETS_REMOTE_BACKEND>": cloud_man.create_iac_backend_snippet(
            location=tf_backend_storage_name,
            service=f"workloads/{wl_name}/secrets"
        ),
        "# <TF_WL_HOSTING_REMOTE_BACKEND>": cloud_man.create_iac_backend_snippet(
            location=tf_backend_storage_name,
            service=f"workloads/{wl_name}/hosting_provider"
        ),
        "# <TF_HOSTING_PROVIDER>": cloud_man.create_hosting_provider_snippet(),
        "<REGISTRY_DOCKERHUB_PROXY>": dockerhub_proxy,
        "<REGISTRY_GCR_PROXY>": gcr_proxy,
        "<REGISTRY_K8S_GCR_PROXY>": k8s_gcr_proxy,
        "<REGISTRY_QUAY_PROXY>": quay_proxy,
        "<GIT_RUNNER_GROUP_NAME>": git_runner_group_name,
        "<TERRAFORM_VERSION>": TERRAFORM_VERSION,
        "<CLUSTER_NAME>": cluster_name,
        "<DOMAIN_NAME>": domain_name,
        "<TF_BACKEND_STORAGE_NAME>": tf_backend_storage_name,
        "<CLOUD_REGION>": cloud_region,
        "<OWNER_EMAIL>": owner_email,
        "<REGISTRY_URL>": registry_url,
        "<CI_IAM_ROLE_RN>": ci_iam_role_rn,
        "<CLOUD_ACCOUNT>": cloud_account,
        "<WL_IAM_ROLE_RN>": construct_wl_iam_role(
            state_store.cloud_provider, cloud_account, cluster_name, wl_name, wl_svc_name
        ),
        "<CLOUD_BINARY_ARTIFACTS_STORE>": artifact_store
    }

    # set cloud provider specific params
    cloud_provider = state_store.parameters["<CLOUD_PROVIDER>"]
    if cloud_provider == CloudProviders.AWS:
        wl_gitops_params["<CLUSTER_OIDC_PROVIDER_ARN>"] = state_store.parameters["<CC_CLUSTER_OIDC_PROVIDER>"]
    elif cloud_provider == CloudProviders.Azure:
        pass
    else:
        raise click.ClickException("Unknown cloud provider")

    click.echo("4/11: Parameters for workload and GitOps repositories prepared.")

    # Initialize WorkloadManager for the workload repository
    wl_manager = WorkloadManager(
        org_name=org_name,
        wl_repo_name=wl_repo_name,
        ssh_pkey_path=key_path,
        template_url=wl_template_url,
        template_branch=wl_template_branch
    )
    click.echo("5/11: Workload repository manager initialized.")

    try:
        # Perform bootstrap steps for the workload repository
        perform_bootstrap(workload_manager=wl_manager, params=wl_repo_params,
                          author_name=state_store.internals["GIT_USER_NAME"],
                          author_email=state_store.internals["GIT_USER_EMAIL"])
        click.echo("6/11: Workload repository bootstrap process completed.")
    except WorkloadManagerError as e:
        raise click.ClickException(str(e))

    # Cleanup temporary folder for workload repository
    wl_manager.cleanup()
    click.echo("7/11: Workload repository cleanup completed.")

    # Initialize WorkloadManager for the GitOps repository
    wl_gitops_manager = WorkloadManager(
        org_name=org_name,
        wl_repo_name=wl_gitops_repo_name,
        ssh_pkey_path=key_path,
        template_url=wl_gitops_template_url,
        template_branch=wl_gitops_template_branch
    )
    click.echo("8/11: GitOps repository manager initialized.")

    try:
        # Perform bootstrap steps for the GitOps repository
        perform_bootstrap(
            workload_manager=wl_gitops_manager,
            params=wl_gitops_params,
            author_name=state_store.internals["GIT_USER_NAME"],
            author_email=state_store.internals["GIT_USER_EMAIL"],
        )
        click.echo("9/11: GitOps repository bootstrap process completed.")
    except WorkloadManagerError as e:
        raise click.ClickException(str(e))

    try:
        # Create a PR in GitOps repository to trigger IaC execution
        branch_name = f"{WL_PR_BRANCH_NAME_PREFIX}{wl_name}-iac-init"
        git_man = init_git_provider(state_store)
        wl_gitops_manager.update()
        wl_gitops_manager.create_branch(branch_name)

        perform_gitops_iac_bootstrap(state_store, wl_gitops_repo_name, wl_gitops_params)

        wl_gitops_manager.upload(author_name=state_store.internals["GIT_USER_NAME"],
                                 author_email=state_store.internals["GIT_USER_EMAIL"])
        wl_gitops_manager.switch_to_branch()

        pr_url = git_man.create_pr(wl_gitops_repo_name, branch_name, "main",
                                   f"Execute IaC changes for {wl_name}", "Setup default secrets.")
        webbrowser.open(pr_url, autoraise=False)

        click.echo("10/11: Created PR for GitOps repository.")

    except WorkloadManagerError as e:
        raise click.ClickException(str(e))
    except GitBranchAlreadyExists as e:
        raise click.ClickException(str(e))

    # Cleanup temporary folder for GitOps repository
    wl_gitops_manager.cleanup()
    click.echo("11/11: GitOps repository cleanup completed.")

    click.echo(f"Bootstrapping workload completed in {time.time() - func_start_time:.2f} seconds.")


def perform_gitops_iac_bootstrap(state_store, wl_gitops_repo_name, wl_gitops_params):
    """
    Perform the GitOps repo IaC bootstrap process.

    Args:
        state_store (StateStore): An instance of StateStore containing configuration and state information.
        wl_gitops_repo_name (str): Name of the workload GitOps repository.
        wl_gitops_params (Dict[str, str]): Dictionary containing parameters for bootstrap.

    """
    cloud_provider = state_store.parameters["<CLOUD_PROVIDER>"]
    identity_template_file = LOCAL_WORKLOAD_TEMP_FOLDER / f"{wl_gitops_repo_name}/terraform/infrastructure/samples/{cloud_provider}/"
    if cloud_provider == CloudProviders.AWS:
        identity_template_file = identity_template_file / "irsa_role.tf"
    elif cloud_provider == CloudProviders.Azure:
        identity_template_file = identity_template_file / "managed_identity.tf"
    else:
        raise click.ClickException("Unknown cloud provider")

    identity_file = LOCAL_WORKLOAD_TEMP_FOLDER / f"{wl_gitops_repo_name}/terraform/infrastructure/wl_identities.tf"
    # with open(identity_template_file, "r") as file:
    #     data = file.read()
    #     for k, v in wl_gitops_params.items():
    #         data = data.replace(k, v)
    #
    #     with open(identity_file, "w") as file:
    #         file.write(data)

    shutil.copy(identity_template_file, identity_file)

    # modify secrets.tf to trigger atlantis
    with open(LOCAL_WORKLOAD_TEMP_FOLDER / f"{wl_gitops_repo_name}/terraform/secrets/secrets.tf", "a") as file:
        file.write("\n")


def perform_bootstrap(workload_manager: WorkloadManager, params: Dict[str, str], author_name: str, author_email: str):
    """
    Perform the bootstrap process using the WorkloadManager.

    Args:
        workload_manager (WorkloadManager): The workload manager instance.
        params (Dict[str, str]): Dictionary containing parameters for bootstrap.
        author_name (str): Git commit author name.
        author_email (str): Git commit author email.
    Raises:
        WorkloadManagerError: If cloning, templating, or uploading process fails.
    """
    if not workload_manager.clone_template():
        raise WorkloadManagerError("Failed to clone template repository")

    if not workload_manager.clone_wl():
        raise WorkloadManagerError("Failed to clone workload repository")

    # Bootstrap workload with the given service names
    service_names = [params.get("<WL_SERVICE_NAME>")]
    workload_manager.bootstrap(service_names)

    workload_manager.parametrise(params)

    workload_manager.upload(
        author_name=author_name,
        author_email=author_email
    )
