# CG DevX CLI

The CG DevX CLI simplifies the initial setup of the CG DevX reference architecture. This setup process is intended to be
executed from an operator's machine and will create a local folder containing tools, temporary, and configuration files.
All subsequent commands should be executed from the same machine, as they rely on data created during the setup process.

## Getting Started

### Required Installations

- **Python 3.10 + pip**
- **[Poetry](https://python-poetry.org/)** version 1.6.*

If you do not have Poetry installed, follow the official installation instructions
here: [Poetry Installation](https://python-poetry.org/docs/#installation).

```bash
# Assumed directory: GITROOT/tools
# Note: Poetry configuration and lock files are stored in the 'cli' directory.

# To install dependencies, use:
poetry install

# To activate the virtual environment, use:
# By default, Poetry creates a virtual environment in {cache-dir}/virtualenvs
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

Build the CLI Tool

To build the CLI tool, use `PyInstaller`:

```bash
# Current directory: GITROOT/tools
python -m PyInstaller --onefile cli/__main__.py --name cgdevxcli
```

Alternatively, you can build with `PyInstaller` via a Python script:

```bash
# Current directory: GITROOT/tools
poetry run build
```

After building, you can use and distribute `cgdexvcli` located at `GITROOT/dist/cgdevxcli`.

## Using CG DevX CLI

To run a Python script via Poetry, use the snippet below:

```bash
 # Current directory: GITROOT/tools
poetry run cgdevxcli
```

Or, use a version built using the steps above:

```bash
# Current directory: GITROOT/tools
./dist/cgdevxcli
```

The usage pattern is `[OPTIONS] COMMAND [ARGS]`.

CG DevX CLI Supports the Following:
Options:

- `--help` Shows the help message

Commands:

- `setup` - Creates a new CG DevX installation.
- `destroy` - Destroys an existing CG DevX installation.
- `workload` - Manages workloads with the following subcommands:
  - `create` - Generates configuration for key workload resources.
  - `bootstrap` - Bootstraps a workload with configuration templates.
  - `delete` - Removes configuration for key workload resources.

Arguments:
Arguments are command-specific and can be supplied via the command line, environment variables, or a file.

For more details,
please check CG DevX quickstart [commands](cli/commands/README.md)
and [workload commands](cli/commands/workload/README.md)
