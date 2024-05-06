import os
import shutil
from pathlib import Path
from typing import Optional, Union, List, Dict

from ghrepo import GHRepo
from git import Repo, GitError, Actor

from common.const.common_path import LOCAL_WORKLOAD_TEMP_FOLDER
from common.const.const import WL_REPOSITORY_BRANCH, WL_REPOSITORY_URL
from common.custom_excpetions import RepositoryNotInitializedError
from common.logging_config import logger
from common.tracing_decorator import trace


class WorkloadManager:
    """CG DevX Workload templates manager."""

    def __init__(
            self,
            org_name: str,
            wl_repo_name: str,
            ssh_pkey_path: str,
            template_url: Optional[str] = WL_REPOSITORY_URL,
            template_branch: Optional[str] = WL_REPOSITORY_BRANCH
    ):
        self._template_url = template_url
        self._branch = template_branch
        self._git_org_name = org_name
        self.wl_repo_name = wl_repo_name
        self.ssh_pkey_path = ssh_pkey_path
        self.wl_repo_folder = LOCAL_WORKLOAD_TEMP_FOLDER / wl_repo_name
        self.template_repo_folder = LOCAL_WORKLOAD_TEMP_FOLDER / GHRepo.parse(self._template_url).name
        self.wl_repo = None
        self.template_repo = None

    @trace()
    def clone_template(self) -> str:
        """
        Clone the Git repository template.
        """
        self._prepare_clone_folder(folder=self.template_repo_folder)
        self._clone_repository(url=self._template_url, branch=self._branch, folder=self.template_repo_folder)
        return self.template_repo_folder

    @trace()
    def clone_wl(self) -> str:
        """
        Clone the workload Git repository.
        """
        wl_repo_url = GHRepo(owner=self._git_org_name, name=self.wl_repo_name).ssh_url
        self._prepare_clone_folder(folder=self.wl_repo_folder)
        self.wl_repo = self._clone_repository(url=wl_repo_url, folder=self.wl_repo_folder)
        return self.wl_repo_folder

    @trace()
    def bootstrap(self, services: Optional[List[str]] = None) -> None:
        """
        Sets up the workload repository using the cloned template.

        Args:
            services (Optional[List[str]]): A list of service names to be set up in the workload repository.
        """
        logger.info("Starting bootstrap process for the workload repository.")
        try:
            self._remove_git_directory()
            self._copy_template_to_workload_repo()
            self._setup_services(services)
            logger.info("Bootstrap completed successfully.")
        except GitError as e:
            logger.error(f"Git error during bootstrap process: {e}")
            raise
        except shutil.Error as e:
            logger.error(f"Shutil error during file operations: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during bootstrap process: {e}")
            raise

    @trace()
    def parametrise(self, params: Optional[Dict[str, str]] = None) -> None:
        """
        Update file contents within the workload repository, replacing placeholders with actual values.

        Args:
            params (Optional[Dict[str, str]]): Key-value pairs where the key is a placeholder and the value is the actual value.
        """
        if not params:
            logger.info("No parameters provided for parameterization. Skipping process.")
            return

        logger.info(f"Parameterizing workload repository '{self.wl_repo_name}' with provided parameters.")
        try:
            # Processing each file in the repository and replacing placeholders
            self._replace_placeholders_in_folder(folder=self.wl_repo_folder, params=params)
            logger.info(f"Parameterization of repository '{self.wl_repo_name}' completed successfully.")
        except GitError as git_err:
            logger.error(f"Git error during parameterization: {git_err}")
            raise
        except shutil.Error as shutil_err:
            logger.error(f"Error during file copying operations: {shutil_err}")
            raise
        except IOError as io_err:
            logger.error(f"I/O error during file processing: {io_err}")
            raise

    @trace()
    def upload(self, author_name: str, author_email: str) -> None:
        """
        Commit and push changes to the workload repository.

        Args:
            author_name (str): The name of the author for the commit.
            author_email (str): The email of the author for the commit.
        """
        if not self.wl_repo:
            logger.error("Workload repository is not initialized. Please clone it first.")
            raise RepositoryNotInitializedError("Workload repository not initialized")

        logger.info(f"Uploading changes to the repository '{self.wl_repo_name}'.")

        try:
            self.wl_repo.git.add(all=True)
            author = Actor(name=author_name, email=author_email)
            self.wl_repo.index.commit("initial commit", author=author, committer=author)
            self.wl_repo.remotes.origin.push(self.wl_repo.active_branch.name)
            logger.info(f"Changes by {author_name} <{author_email}> uploaded successfully.")
        except GitError as e:
            logger.error(f"GitError during upload: {e}")
            raise

    @trace()
    def cleanup(self) -> None:
        """
        Clean up the cloned template and workload repositories by removing their folders.
        """
        try:
            self._remove_folder(self.template_repo_folder)
            self._remove_folder(self.wl_repo_folder)
            logger.info("Cleanup completed successfully for both template and workload repositories.")
        except shutil.Error as e:
            logger.error(f"Error during cleanup process: {e}")
            raise

    @trace()
    def update(self):
        if not self.wl_repo:
            self.wl_repo = Repo(self.wl_repo_folder)
        with self.wl_repo.git.custom_environment(GIT_SSH_COMMAND=f"ssh -o StrictHostKeyChecking=no -i {self.ssh_pkey_path}"):
            # clean stale branches
            self.wl_repo.remotes.origin.fetch(prune=True)
            self.wl_repo.heads.main.checkout()
            self.wl_repo.remotes.origin.pull(self.wl_repo.active_branch)

    @trace()
    def branch_exist(self, branch_name):
        return branch_name in self.wl_repo.branches

    @trace()
    def create_branch(self, branch_name):
        current = self.wl_repo.create_head(branch_name)
        current.checkout()

    @trace()
    def switch_to_branch(self, branch_name: str = "main"):
        self.wl_repo.heads[branch_name].checkout()

    def _replace_placeholders_in_folder(self, folder: Union[str, Path], params: Dict[str, str]) -> None:
        """
        Replace placeholders in all eligible files within the specified folder.

        Args:
            folder (Union[str, Path]): Directory containing files to process.
            params (Dict[str, str]): Key-value pairs for placeholder replacement.
        """
        logger.debug(f"Scanning folder '{folder}' for files to parameterize.")
        for root, dirs, files in os.walk(folder):
            for name in files:
                if self._is_parametrizable_file(name):
                    file_path = Path(root) / name
                    # Process individual file
                    self._replace_placeholder_in_file(file_path, params)

    @staticmethod
    def _is_parametrizable_file(file_name: str) -> bool:
        """
        Check if a file is eligible for parameterization based on its extension.

        Args:
            file_name (str): Name of the file to check.

        Returns:
            bool: True if the file is eligible for parameterization, False otherwise.
        """
        is_parametrizable = file_name.endswith((".tf", ".yaml", ".yml", ".md"))
        if is_parametrizable:
            logger.debug(f"File '{file_name}' is eligible for parameterization.")
        return is_parametrizable

    @staticmethod
    def _replace_placeholder_in_file(file_path: Path, params: Dict[str, str]) -> None:
        """
        Process a single file, replacing placeholders with actual values.

        Args:
            file_path (Path): Path of the file to process.
            params (Dict[str, str]): Key-value pairs for placeholder replacement.
        """
        with open(file_path, "r") as file:
            data = file.read()

        # Replace each placeholder in the file
        for placeholder, value in params.items():
            data = data.replace(placeholder, value)

        with open(file_path, "w") as file:
            file.write(data)

        logger.debug(f"File '{file_path}' parameterized successfully.")

    def _remove_git_directory(self) -> None:
        """Removes the .git directory from the template repository folder if it exists."""
        git_dir = self.template_repo_folder / ".git"
        self._remove_folder(folder=git_dir)

    def _copy_template_to_workload_repo(self) -> None:
        """Copies the entire contents of the template repository to the workload repository."""
        logger.debug(f"Copying template from {self.template_repo_folder} to {self.wl_repo_folder}.")
        shutil.copytree(self.template_repo_folder, self.wl_repo_folder, dirs_exist_ok=True)

    def _setup_services(self, services: Optional[List[str]]) -> None:
        """
        Sets up individual services in the workload repository based on the provided list.

        Args:
            services (Optional[List[str]]): A list of service names to set up.
        """
        if not services:
            logger.debug("No additional services to set up.")
            return

        service_src = self.wl_repo_folder / "wl-service-name"
        if not os.path.exists(service_src):
            logger.warning(f"Service template directory '{service_src}' does not exist.")
            return

        for wl_svc_name in services:
            service_dst = self.wl_repo_folder / wl_svc_name
            logger.debug(f"Setting up service: {wl_svc_name}")
            shutil.copytree(src=service_src, dst=service_dst, dirs_exist_ok=True)

        logger.debug(f"Cleaning up template service directory: {service_src}.")
        self._remove_folder(folder=service_src)

    def _prepare_clone_folder(self, folder: Union[str, Path]) -> None:
        """
        Prepares the folder for cloning by removing it if it exists and then creating it.

        Args:
            folder (Union[str, Path]): Local directory path to prepare for cloning.
        """
        self._remove_folder(folder=folder)
        logger.debug(f"Creating folder: {folder}")
        os.makedirs(name=folder, exist_ok=True)
        logger.info(f"Folder '{folder}' prepared for cloning.")

    def _clone_repository(self, url: str, folder: Union[str, Path], branch: Optional[str] = None) -> Repo:
        """
        Clones the repository into the specified folder. If the branch is not specified,
        clones the default branch.

        Args:
            url (str): URL of the repository to clone.
            folder (Union[str, Path]): Local directory path to clone the repository into.
            branch (Optional[str]): Branch name to clone. If None, the default branch is cloned.

        Returns:
            Repo: The cloned Git repository object.
        """
        logger.info(f"Cloning repository from {url} into {folder}")

        clone_kwargs = {
            "url": url,
            "to_path": folder,
            "env": {"GIT_SSH_COMMAND": f"ssh -o StrictHostKeyChecking=no -i {self.ssh_pkey_path}"}
        }

        if branch:
            clone_kwargs["branch"] = branch

        try:
            repo = Repo.clone_from(**clone_kwargs)
            logger.info("Repository cloned successfully.")
            return repo
        except GitError as e:
            logger.error(f"Error while cloning repository: {e}")
            raise

    @staticmethod
    def _remove_folder(folder: Union[str, Path]) -> None:
        """
        Remove the specified folder if it exists.

        Args:
            folder (Union[str, Path]): The path to the folder to be removed.
        """
        if os.path.exists(path=folder):
            logger.debug(f"Removing folder: {folder}")
            shutil.rmtree(path=folder)
            logger.info(f"Folder {folder} removed successfully.")
        else:
            logger.debug(f"Folder {folder} does not exist. No action needed.")
