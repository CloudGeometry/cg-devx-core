# CG DevX CLI

## Getting Started

You need to install:
* **python 3.10 + pip**: 

Using Python virtualenv is recommended. You can init the virtual environment with the following command:
```bash
# Current directory: GITROOT

# Initialize venv in ./venv
# You only need to execute this once
python3 -m cmd

# Install dependencies
pip install -r requirements.txt

# Activate the venv
# You need to run this whenever you work with the codebase
source cmd/bin/activate
```

## Code Style
Run the command to validate code style:
```bash
flake8
```