import os
import shutil

from ghrepo import GHRepo
from git import Repo, GitError, Actor

from common.const.common_path import LOCAL_WORKLOAD_TEMP_FOLDER
from common.const.const import WL_REPOSITORY_URL, WL_REPOSITORY_BRANCH
from common.tracing_decorator import trace


class WorkloadTemplateManager:
    """CG DevX Workload templates manager."""

    def __init__(self, org_name: str, repo_name: str, key_path: str, template_url: str = None,
                 template_branch: str = None):
        if template_url is None:
            self._url = WL_REPOSITORY_URL
        else:
            self._url = template_url

        if template_branch is None:
            self._branch = WL_REPOSITORY_BRANCH
        else:
            self._branch = template_branch

        self._git_org_name = org_name
        self._repo_name = repo_name
        self._key_path = key_path
        self._wl_template_repo = None
        self._wl_repo = None

        self._wl_repo_folder = LOCAL_WORKLOAD_TEMP_FOLDER / self._repo_name
        self._wl_template_repo_folder = LOCAL_WORKLOAD_TEMP_FOLDER / GHRepo.parse(self._url).name

    @trace()
    def clone_template(self):
        if os.path.exists(self._wl_template_repo_folder):
            shutil.rmtree(self._wl_template_repo_folder)

        os.makedirs(self._wl_template_repo_folder)

        try:
            self._wl_template_repo = Repo.clone_from(self._url,
                                                     self._wl_template_repo_folder,
                                                     branch=self._branch,
                                                     env={
                                                         "GIT_SSH_COMMAND": f'ssh -o StrictHostKeyChecking=no -i {self._key_path}'})
            return self._wl_template_repo_folder
        except GitError as e:
            return None

    @trace()
    def clone_wl(self):
        if os.path.exists(self._wl_repo_folder):
            shutil.rmtree(self._wl_repo_folder)
        os.makedirs(self._wl_repo_folder)

        try:
            self._wl_repo = Repo.clone_from(GHRepo(self._git_org_name, self._repo_name).ssh_url,
                                            self._wl_repo_folder,
                                            env={
                                                "GIT_SSH_COMMAND": f'ssh -o StrictHostKeyChecking=no -i {self._key_path}'})
            return self._wl_repo_folder
        except GitError as e:
            return None

    @trace()
    def bootstrap(self, services: [str]):
        if os.path.exists(self._wl_template_repo_folder / ".git"):
            shutil.rmtree(self._wl_template_repo_folder / ".git")
        shutil.copytree(self._wl_template_repo_folder, self._wl_repo_folder, dirs_exist_ok=True)
        for wl_svc_name in services:
            shutil.copytree(self._wl_repo_folder / "wl-service-name", self._wl_repo_folder / wl_svc_name,
                            dirs_exist_ok=True)
        shutil.rmtree(self._wl_repo_folder / "wl-service-name")

    @trace()
    def parametrise(self, params: dict = {}):
        for root, dirs, files in os.walk(self._wl_repo_folder):
            for name in files:
                if name.endswith(".tf") or name.endswith(".yaml") or name.endswith(".yml") or name.endswith(".md"):
                    file_path = os.path.join(root, name)
                    with open(file_path, "r") as file:
                        data = file.read()
                        for k, v in params.items():
                            data = data.replace(k, v)
                    with open(file_path, "w") as file:
                        file.write(data)

    @trace()
    def upload(self, name: str = None, email: str = None):
        self._wl_repo.git.add(all=True)
        author = Actor(name=name, email=email)
        self._wl_repo.index.commit("initial", author=author, committer=author)

        self._wl_repo.remotes.origin.push(self._wl_repo.active_branch.name)

    @trace()
    def cleanup(self):
        if os.path.exists(self._wl_template_repo_folder):
            shutil.rmtree(self._wl_template_repo_folder)
        if os.path.exists(self._wl_repo_folder):
            shutil.rmtree(self._wl_repo_folder)
