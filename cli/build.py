import PyInstaller.__main__

PyInstaller.__main__.run([
    "--name",
    "cgdevxcli",
    "--onefile",
    "--console",
    "main.py"
])
