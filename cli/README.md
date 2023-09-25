# CG DevX CLI

CG DevX CLI simplifies initial setup of CG DevX reference architecture.
The setup process is intended to be executed from an operator's machine and will create a local folder containing tools,
temporary, and configuration files.
All subsequent commands should be executed from the same machine, as they will rely on a data created by setup process.

## Getting Started


Required installations:
* **python 3.10 + pip**:

Although Python's virtualenv is an option, it's recommended to utilize `Poetry` for dependency management and virtual environment handling. To initiate a virtual environment using Poetry, follow these steps:

# CG DevX CLI

## Getting Started

Required installations:
* **python 3.10 + pip**:

Although Python's virtualenv is an option, it's recommended to utilize `Poetry` for dependency management and virtual environment handling. To initiate a virtual environment using Poetry, follow these steps:

```bash
# Assumed directory: GITROOT

# If Poetry isn't installed yet, you can do so via pip
pip install poetry

# To install dependencies, use:
# NOTE: Poetry configuration and lock files are stored in the 'cli' directory.
poetry install

# Activate the virtual environment with:
poetry shell
```

## Local development

### Code Style

Run the command to validate code style:

```bash
flake8
```

To run provisioning using a local dev version of repository, instead of cloning GitOps template repo, you could use
environment variable `CGDEVX_CLI_CLONE_LOCAL=True`

## Build CLI tool

To build CLI tool run `PyInstaller` directly

```bash 
# Current directory: GITROOT/cli
python -m PyInstaller --onefile main.py --name cgdevxcli
```

or via python script

```bash 
# Current directory: GITROOT/cli
python build.py
```

After that you could use and distribute `cgdexvcli` located at `GITROOT/dist/cgdevxcli`

## Use CG DevX CLI

You could run a Python script directly with the snippet below or use a version build using the steps above

```bash 
python main.py
```

The usage pattern is `[OPTIONS] COMMAND [ARGS]`

CG DevX CLI support following:

Options:

- `--help` Show help message

Commands:

- `setup` Creates new CG DevX installation
- `destroy` Destroys existing CG DevX installation

Arguments:
Are command specific and could be supplied via command lime, environment variables, or file

For more details, please check [commands](./commands/README.md)
