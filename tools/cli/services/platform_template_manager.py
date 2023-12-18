import os
import pathlib
import shutil
from pathlib import Path
from urllib.error import HTTPError

import requests
from ghrepo import GHRepo
from git import Repo, RemoteProgress, GitError, Actor

from common.const.common_path import LOCAL_TF_FOLDER, LOCAL_GITOPS_FOLDER
from common.const.const import GITOPS_REPOSITORY_URL, GITOPS_REPOSITORY_BRANCH
from common.state_store import StateStore
from common.tracing_decorator import trace


class GitOpsTemplateManager:
    """CG DevX Git repo templates manager."""

    def __init__(self, gitops_template_url: str = None, gitops_template_branch: str = None, token=None):
        if gitops_template_url is None:
            self._url = GITOPS_REPOSITORY_URL
        else:
            self._url = gitops_template_url

        if gitops_template_branch is None:
            self._branch = GITOPS_REPOSITORY_BRANCH
        else:
            self._branch = gitops_template_branch

        # TODO: DEBUG, remove
        self._token = token

    @trace()
    def check_repository_existence(self):
        """
        Check if the repository exists
        :return: True or False
        """
        repo = GHRepo.parse(self._url)
        headers = {}
        if self._token is not None:
            headers['Authorization'] = f'token {self._token}'

        try:
            response = requests.get(f'{repo.api_url}/branches/{self._branch}',
                                    headers=headers)
            if response.status_code == requests.codes["not_found"]:
                return False
            elif response.ok:
                return True
        except HTTPError as e:
            raise e

    @trace()
    def clone(self):
        temp_folder = LOCAL_GITOPS_FOLDER / ".tmp"

        if os.path.exists(LOCAL_GITOPS_FOLDER):
            shutil.rmtree(LOCAL_GITOPS_FOLDER)

        if os.environ.get("CGDEVX_CLI_CLONE_LOCAL", False):
            source_dir = pathlib.Path().resolve().parent
            shutil.copytree(source_dir, temp_folder)
            return

        os.makedirs(temp_folder)
        try:
            repo = Repo.clone_from(self._url, temp_folder, progress=ProgressPrinter(), branch=self._branch)
        except GitError as e:
            raise e

    @staticmethod
    @trace()
    def upload(path: str, key_path: str, git_user_name: str, git_user_email: str):

        if not os.path.exists(LOCAL_GITOPS_FOLDER):
            raise Exception("GitOps repo does not exist")

        try:
            ssh_cmd = f'ssh -o StrictHostKeyChecking=no -i {key_path}'

            repo = Repo.init(LOCAL_GITOPS_FOLDER)

            with repo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):
                if not any(repo.remotes):
                    origin = repo.create_remote(name='origin', url=path)

                repo.git.add(all=True)
                author = Actor(name=git_user_name, email=git_user_email)
                repo.index.commit("initial", author=author, committer=author)

                repo.remotes.origin.push(repo.active_branch.name)

        except GitError as e:
            raise e

    @staticmethod
    @trace()
    def build_repo_from_template():
        temp_folder = LOCAL_GITOPS_FOLDER / ".tmp"

        os.makedirs(LOCAL_GITOPS_FOLDER, exist_ok=True)
        # workaround for local development mode, this should not happen in prod
        for root, dirs, files in os.walk(temp_folder):
            for name in files:
                if name.endswith(".DS_Store") or name.endswith(".terraform") \
                        or name.endswith(".github") or name.endswith(".idea"):
                    path = os.path.join(root, name)
                    if os.path.isfile(path):
                        os.remove(path)
                    if os.path.isdir(path):
                        os.rmdir(path)

        # restructure gitops
        shutil.copytree(temp_folder / "platform" / "terraform", LOCAL_GITOPS_FOLDER / "terraform")
        shutil.copytree(temp_folder / "platform" / "gitops-pipelines", LOCAL_GITOPS_FOLDER / "gitops-pipelines")
        for src_file in Path(temp_folder / "platform").glob('*.*'):
            shutil.copy(src_file, LOCAL_GITOPS_FOLDER)

        # drop all non template readme files
        for root, dirs, files in os.walk(LOCAL_GITOPS_FOLDER):
            for name in files:
                if name.endswith(".md") and not name.startswith("tpl_"):
                    os.remove(os.path.join(root, name))

        # rename readme file templates
        for root, dirs, files in os.walk(LOCAL_GITOPS_FOLDER):
            for name in files:
                if name.startswith("tpl_") and name.endswith(".md"):
                    s = os.path.join(root, name)
                    os.rename(s, s.replace("tpl_", ""))

        shutil.rmtree(temp_folder)
        return

    @trace()
    def parametrise_tf(self, state: StateStore):
        self.__file_replace(state, LOCAL_TF_FOLDER)

    @trace()
    def parametrise(self, state: StateStore):
        self.__file_replace(state, LOCAL_GITOPS_FOLDER)

    @staticmethod
    def __file_replace(state: StateStore, folder):
        try:
            for root, dirs, files in os.walk(folder):
                for name in files:
                    if name.endswith(".tf") or name.endswith(".yaml") or name.endswith(".yml") or name.endswith(".md"):
                        file_path = os.path.join(root, name)
                        with open(file_path, "r") as file:
                            data = file.read()
                            for k, v in state.fragments.items():
                                data = data.replace(k, v)
                            for k, v in state.parameters.items():
                                data = data.replace(k, v)
                        with open(file_path, "w") as file:
                            file.write(data)
        except Exception as e:
            raise Exception(f"Error while parametrizing file: {file_path}", e)


class ProgressPrinter(RemoteProgress):
    @trace()
    def update(self, op_code, cur_count, max_count=None, message=""):
        # TODO: forward to CLI progress bar
        pass
