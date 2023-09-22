# CG DevX CLI

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

## SDKs

### Cloud providers

- [AWS SDK](https://github.com/boto/boto3)
- [Azure SDK](https://github.com/Azure/azure-sdk-for-python)
- [GCP SDK](https://github.com/googleapis/google-cloud-python#google-cloud-datastore)

### DNS registrars 


### Git

[GitHub]() over REST API