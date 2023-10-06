from pathlib import Path

import PyInstaller.__main__

path_to_main = str(Path(__file__).parent.absolute() / "__main__.py")
print(path_to_main)


def install():
    PyInstaller.__main__.run([
        path_to_main,
        "--name",
        "cgdevxcli",
        "--onefile",
        "--console",
        "--add-data",
        "cli/services/k8s/kubeconfig.yaml:services/k8s"
    ])
