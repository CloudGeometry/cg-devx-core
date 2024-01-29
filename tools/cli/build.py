import importlib.util
import os
from pathlib import Path
import PyInstaller.__main__

# Get the absolute path to the main script.
path_to_main = str(Path(__file__).parent.absolute() / "__main__.py")

# Reference: This fix for 'grapheme' is in response to a specific issue discussed on Stack Overflow.
# The 'alive-progress' library relies on the 'grapheme' library, which requires a specific JSON file.
# This file is not included by default by PyInstaller during the build.
# The following lines dynamically find the installation path of 'grapheme'.
# Issue link: https://stackoverflow.com/questions/74256747/python-exe-containing-alive-progress-bar-error-filenotfound
grapheme_path = importlib.util.find_spec("grapheme").origin
grapheme_json_file_path = os.path.join(os.path.dirname(grapheme_path), "data", "grapheme_break_property.json")


def install():
    PyInstaller.__main__.run([
        path_to_main,
        "--name",
        "cgdevxcli",
        "--onefile",
        "--console",
        "--add-data",
        "cli/services/k8s/kubeconfig.yaml:services/k8s",
        "--add-data",
        f"{grapheme_json_file_path}:grapheme/data"  # Include the 'grapheme' JSON file required by 'alive-progress'.
    ])
