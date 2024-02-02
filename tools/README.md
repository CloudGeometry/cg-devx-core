# CG DevX CLI

CG DevX CLI simplifies initial setup of CG DevX reference architecture.
The setup process is intended to be executed from an operator's machine and will create a local folder containing tools,
temporary, and configuration files.
All subsequent commands should be executed from the same machine, as they will rely on a data created by setup process.

## Getting Started

Required installations:

- **python 3.10 + pip**
- **[poetry](https://python-poetry.org/)** 1.6.*

If you don't have poetry installed, please follow official installation
instructions [here](https://python-poetry.org/docs/#installation).

```bash
# Assumed directory: GITROOT/tools
# NOTE: Poetry configuration and lock files are stored in the 'cli' directory.

# To install dependencies, use:
poetry install

# Activate the virtual environment with:
# By default, Poetry creates a virtual environment in {cache-dir}/virtualenvs
poetry shell
```

To find more on poetry commands, please [see](https://python-poetry.org/docs/basic-usage/).

## Local development

### Code Style

Run the command to validate code style:

```bash
flake8
```

To run provisioning using a local dev version of repository, instead of cloning GitOps template repo, you could use
environment variable `CGDEVX_CLI_CLONE_LOCAL=True`

## Build CLI tool

To build CLI tool, please run `PyInstaller`

directly

```bash 
# Current directory: GITROOT/tools
python -m PyInstaller --onefile cli/__main__.py --name cgdevxcli
```

or via python script

```bash 
# Current directory: GITROOT/tools
poetry run build
```

After that you could use and distribute `cgdexvcli` located at `GITROOT/dist/cgdevxcli`

## Use CG DevX CLI

You could run a Python script via poetry with the snippet below

```bash
 # Current directory: GITROOT/tools
poetry run cgdevxcli
```

or use a version build using the steps above

```bash
 # Current directory: GITROOT/tools
./dist/cgdevxcli
```

The usage pattern is `[OPTIONS] COMMAND [ARGS]`

CG DevX CLI support following:

Options:

- `--help` Show help message

Commands:

- `setup` Creates new CG DevX installation
- `destroy` Destroys existing CG DevX installation
- `workload` Commands related to Workload Management
    - `create` Generates configuration of key Workload resources
    - `bootstrap` Bootstraps Workload with configuration templates
    - `delete` Removes configuration of key Workload resources

Arguments:
Are command specific and could be supplied via command lime, environment variables, or file

For more details,
please check CG DevX quickstart [commands](cli/commands/README.md)
and [workload commands](cli/commands/workload/README.md)
