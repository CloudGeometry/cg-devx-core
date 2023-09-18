import os
import shutil
from pathlib import Path
from urllib.error import HTTPError

import requests
from ghrepo import GHRepo
from git import Repo, RemoteProgress, GitError, Actor

from cli.common.const.const import LOCAL_FOLDER, GITOPS_REPOSITORY_URL, GITOPS_REPOSITORY_BRANCH
import logging

logging.basicConfig(level=logging.INFO)


class GitOpsTemplateManager:
    """CG DevX Git repo templates manager."""

    def __init__(self, gitops_template_url: str, gitops_template_branch: str, token=None):
        if gitops_template_url is None:
            self.__url = GITOPS_REPOSITORY_URL
        else:
            self.__url = gitops_template_url

        if gitops_template_branch is None:
            self.__branch = GITOPS_REPOSITORY_BRANCH
        else:
            self.__branch = gitops_template_branch

        # TODO: DEBUG, remove
        self.__token = token

    def check_repository_existence(self):
        """
        Check if repository exists
        :return: True or False
        """
        repo = GHRepo.parse(self.__url)
        headers = {}
        if self.__token is not None:
            headers['Authorization'] = f'token {self.__token}'

        try:
            response = requests.get(f'https://api.github.com/repos/{repo.owner}/{repo.name}/branches/{self.__branch}',
                                    headers=headers)
            if response.status_code == requests.codes["not_found"]:
                return False
            elif response.ok:
                return True
        except HTTPError as e:
            raise e

    def clone(self):
        gitops_folder = Path().home() / LOCAL_FOLDER / "gitops"
        if os.path.exists(gitops_folder):
            shutil.rmtree(gitops_folder)
        os.makedirs(gitops_folder)
        try:
            repo = Repo.clone_from(self.__url, gitops_folder, progress=ProgressPrinter(), branch=self.__branch)
        except GitError as e:
            raise e

    def upload(self, path: str, key_path: str, git_user_name: str, git_user_email: str):
        gitops_folder = Path().home() / LOCAL_FOLDER / "gitops"
        if not os.path.exists(gitops_folder):
            raise Exception("GitOps repo does not exist")

        try:
            ssh_cmd = f'ssh -o StrictHostKeyChecking=no -i {key_path}'

            repo = Repo.init(gitops_folder)

            with repo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):
                if not any(repo.remotes):
                    origin = repo.create_remote(name='origin', url=path)

                repo.git.add(all=True)
                author = Actor(name=git_user_name, email=git_user_email)
                repo.index.commit("initial", author=author, committer=author)

                repo.remotes.origin.push(repo.active_branch.name)

        except GitError as e:
            raise e

    def restructure_template(self):
        gitops_folder = Path().home() / LOCAL_FOLDER / "gitops"
        # remove git reference
        shutil.rmtree(gitops_folder / ".git", ignore_errors=True)
        # remove cli
        shutil.rmtree(gitops_folder / "cli", ignore_errors=True)
        # restructure gitops
        shutil.move(gitops_folder / "platform" / "terraform", gitops_folder / "terraform")
        shutil.move(gitops_folder / "platform" / "gitops-pipelines", gitops_folder / "gitops-pipelines")
        for src_file in Path(gitops_folder / "platform").glob('*.*'):
            shutil.move(src_file, gitops_folder)
        shutil.rmtree(gitops_folder / "platform")

        # drop all non template readme files
        for root, dirs, files in os.walk(gitops_folder):
            for name in files:
                if name.endswith(".md") and not name.startswith("tpl_"):
                    os.remove(os.path.join(root, name))

        # rename readme file templates
        for root, dirs, files in os.walk(gitops_folder):
            for name in files:
                if name.startswith("tpl_") and name.endswith(".md"):
                    s = os.path.join(root, name)
                    os.rename(s, s.replace("tpl_", ""))

    def parametrise_tf(self, params: dict):
        tf_folder = Path().home() / LOCAL_FOLDER / "gitops" / "terraform"

        self.__file_replace(params, tf_folder)

    def parametrise_registry(self, params: dict):
        pipelines_folder = Path().home() / LOCAL_FOLDER / "gitops" / "gitops-pipelines"

        self.__file_replace(params, pipelines_folder)

    def parametrise_root(self, params: dict):
        for src_file in Path(Path().home() / LOCAL_FOLDER / "gitops").glob('*.md'):
            with open(src_file, "r") as file:
                data = file.read()
                for k, v in params.items():
                    data = data.replace(k, v)
            with open(src_file, "w") as file:
                file.write(data)

    @staticmethod
    def __file_replace(params, folder):
        for root, dirs, files in os.walk(folder):
            for name in files:
                file_path = os.path.join(root, name)
                with open(file_path, "r") as file:
                    data = file.read()
                    for k, v in params.items():
                        data = data.replace(k, v)
                with open(file_path, "w") as file:
                    file.write(data)

        # tf_executable = Path().home() / LOCAL_FOLDER / "tools" / "terraform"
        # if os.path.exists(tf_executable):
        # t = Terraform(terraform_bin_path=str(tf_executable))
        # t.replace("hello world", "/w.*d/", "everybody")


class ProgressPrinter(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=""):
        # TODO: forward to CLI (Click) progress bar
        pass
