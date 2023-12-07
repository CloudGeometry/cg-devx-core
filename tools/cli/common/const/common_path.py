import os
from pathlib import Path

# todo: add override using env var
LOCAL_FOLDER = Path().home() / os.environ.get("CGDEVX_LOCAL_FOLDER", ".cgdevx")
LOCAL_GITOPS_FOLDER = LOCAL_FOLDER / "gitops"
LOCAL_TF_FOLDER = LOCAL_GITOPS_FOLDER / "terraform"
LOCAL_TF_FOLDER_HOSTING_PROVIDER = LOCAL_TF_FOLDER / "hosting_provider"
LOCAL_TF_FOLDER_SECRETS_MANAGER = LOCAL_TF_FOLDER / "secrets"
LOCAL_TF_FOLDER_USERS = LOCAL_TF_FOLDER / "users"
LOCAL_TF_FOLDER_VCS = LOCAL_TF_FOLDER / "vcs"
LOCAL_TF_FOLDER_CORE_SERVICES = LOCAL_TF_FOLDER / "core_services"
LOCAL_TOOLS_FOLDER = LOCAL_FOLDER / "tools"
LOCAL_TF_TOOL = LOCAL_TOOLS_FOLDER / "terraform"
LOCAL_KCTL_TOOL = LOCAL_TOOLS_FOLDER / "kubectl"
LOCAL_STATE_FILE = LOCAL_FOLDER / "state.yaml"
LOCAL_CC_CLUSTER_WORKLOAD_FOLDER = LOCAL_GITOPS_FOLDER / "gitops-pipelines/delivery/clusters/cc-cluster/workloads"
