class GitBranchAlreadyExists(Exception):
    """Exception raised when a branch already exists in the GitOps repository."""

    def __init__(self, branch_name: str, message: str = "Branch already exists"):
        self.branch_name = branch_name
        self.message = f"{message} '{branch_name}'"
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} in the repository."


class PullRequestCreationError(Exception):
    """Exception raised when creating a pull request fails."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class RepositoryNotInitializedError(Exception):
    """Exception raised when trying to access an uninitialized repository."""

    def __init__(self, message: str):
        super().__init__(message)


class WorkloadManagerError(Exception):
    """Custom exception for errors in the WorkloadManager."""

    def __init__(self, message: str):
        super().__init__(message)
