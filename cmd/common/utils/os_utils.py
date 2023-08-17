from shutil import which


def detect_command_presence(command: str) -> bool:
    """Check whether `command` is on PATH and marked as executable."""
    return which(command) is not None
