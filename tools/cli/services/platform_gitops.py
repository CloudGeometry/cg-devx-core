import json
import os

from ghrepo import GHRepo
from git import Repo, Actor, RemoteReference

from common.const.common_path import LOCAL_GITOPS_FOLDER, LOCAL_TF_FOLDER_VCS, LOCAL_TF_FOLDER_SECRETS_MANAGER, \
    LOCAL_TF_FOLDER_CORE_SERVICES, LOCAL_CC_CLUSTER_WORKLOAD_FOLDER
from common.const.const import FALLBACK_AUTHOR_NAME, FALLBACK_AUTHOR_EMAIL
from common.tracing_decorator import trace
from services.vcs.git_provider_manager import GitProviderManager


class PlatformGitOpsRepo:
    def __init__(self, git_man: GitProviderManager, key_path: str = None, author_name: str = FALLBACK_AUTHOR_NAME,
                 author_email: str = FALLBACK_AUTHOR_EMAIL):
        self._repo = Repo(LOCAL_GITOPS_FOLDER)
        self._git_man = git_man
        self._ssh_key_path = key_path
        self._ssh_cmd = f'ssh -o StrictHostKeyChecking=no -i {self._ssh_key_path}'
        self._author_name = author_name
        self._author_email = author_email

    @trace()
    def update(self):
        with self._repo.git.custom_environment(GIT_SSH_COMMAND=self._ssh_cmd):
            # clean stale branches
            self._repo.remotes.origin.fetch(prune=True)
            self._repo.heads.main.checkout()
            self._repo.remotes.origin.pull(self._repo.active_branch)

    @trace()
    def branch_exist(self, branch_name):
        return branch_name in self._repo.branches

    @trace()
    def create_branch(self, branch_name):
        current = self._repo.create_head(branch_name)
        current.checkout()

    @trace()
    def upload_changes(self):
        with self._repo.git.custom_environment(GIT_SSH_COMMAND=self._ssh_cmd):
            self._repo.git.add(all=True)
            author = Actor(name=self._author_name, email=self._author_email)
            self._repo.index.commit("initial", author=author, committer=author)

            self._repo.remotes.origin.push(self._repo.active_branch.name)

    @trace()
    def switch_to_branch(self, branch_name: str = "main"):
        self._repo.heads[branch_name].checkout()

    @trace()
    def delete_branch(self, branch_name: str):
        ref = self._repo.heads[branch_name]
        # use force delete as branch is not fully merged yet
        self._repo.delete_head(ref, force=True)

    @trace()
    def create_pr(self, repo_name: str, head_branch: str, base_branch: str, title: str, body: str) -> str:
        return self._git_man.create_pr(repo_name, head_branch, base_branch, title, body)

    @trace()
    def add_workload(self, wl_name: str, wl_repo_name: str, wl_gitops_repo_name: str):
        # repos
        self._add_wl_vars(LOCAL_TF_FOLDER_VCS, wl_name, {
            "description": f"CG DevX {wl_name} workload definition",
            "repos": {
                wl_repo_name: {},
                wl_gitops_repo_name: {
                    "atlantis_enabled": True,
                }
            }
        })
        # secrets
        self._add_wl_vars(LOCAL_TF_FOLDER_SECRETS_MANAGER, wl_name, {
            "description": f"CG DevX {wl_name} workload definition"
        })
        # core services
        self._add_wl_vars(LOCAL_TF_FOLDER_CORE_SERVICES, wl_name, {
            "description": f"CG DevX {wl_name} workload definition"
        })

        # prepare ArgoCD manifest
        wl_gitops_repo = GHRepo(self._git_man.organization, wl_gitops_repo_name)
        params = {
            "<WL_NAME>": wl_name,
            "<WL_GITOPS_REPOSITORY_GIT_URL>": wl_gitops_repo.ssh_url,
        }

        workload_template_file = LOCAL_CC_CLUSTER_WORKLOAD_FOLDER / "workload-template.yaml"
        with open(workload_template_file, "r") as file:
            data = file.read()
            for k, v in params.items():
                data = data.replace(k, v)

        workload_file = LOCAL_CC_CLUSTER_WORKLOAD_FOLDER / f"{wl_name}.yaml"
        with open(workload_file, "w") as file:
            file.write(data)

    @trace()
    def rm_workload(self, wl_name: str):
        # repos
        self._rm_wl_vars(LOCAL_TF_FOLDER_VCS, wl_name)
        # secrets
        self._rm_wl_vars(LOCAL_TF_FOLDER_SECRETS_MANAGER, wl_name)
        # core services
        self._rm_wl_vars(LOCAL_TF_FOLDER_CORE_SERVICES, wl_name)

        # delete ArgoCD manifest
        wl_argo_manifest = LOCAL_CC_CLUSTER_WORKLOAD_FOLDER / f"{wl_name}.yaml"
        if os.path.exists(wl_argo_manifest):
            os.remove(wl_argo_manifest)

    @staticmethod
    def _add_wl_vars(tf_module_path, wl_name: str, payload=None):
        if payload is None:
            payload = {}

        with open(tf_module_path / "terraform.tfvars.json", "r") as file:
            services_tf_vars = json.load(file)

        services_tf_vars["workloads"][wl_name] = payload

        with open(tf_module_path / "terraform.tfvars.json", "w") as file:
            file.write(json.dumps(services_tf_vars, indent=2))

    @staticmethod
    def _rm_wl_vars(tf_module_path, wl_name: str):
        with open(tf_module_path / "terraform.tfvars.json", "r") as file:
            vcs_tf_vars = json.load(file)

        if wl_name in vcs_tf_vars["workloads"]:
            del vcs_tf_vars["workloads"][wl_name]

            with open(tf_module_path / "terraform.tfvars.json", "w") as file:
                file.write(json.dumps(vcs_tf_vars, indent=2))
