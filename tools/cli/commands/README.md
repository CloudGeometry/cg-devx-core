# CG DevX CLI Commands

This document outlines the commands supported by the CG DevX CLI tool, which configures the CG DevX Kubernetes Internal Developer Platform (IDP) kit.

## Setup

The `setup` command initializes and configures the reference implementation, saving intermediate states to a local file for checkpointing, allowing the command to be rerun if necessary.

**Key Operations Performed:**
- Checks cloud CLI tool presence and permissions using provided profiles or access keys.
- Validates DNS provider permissions and domain ownership.
- Creates SSH key pairs, remote backend storage (e.g., AWS S3), and a GitOps repository under the chosen Git provider.
- Provisions a Kubernetes cluster and associated cloud resources.

**Usage Options:**
- **Arguments**: Command-line arguments directly.
- **Environment Variables**: Via the system environment.
- **Input File**: Specifying parameters in a YAML file.

### Command Arguments

| Name (short, full)             | Type                                    | Description                                       |
|--------------------------------|-----------------------------------------|---------------------------------------------------|
| -e, --email                    | TEXT                                    | Email address for alerts                          |
| -c, --cloud-provider           | [aws]                                   | Cloud provider type                               |
| -cp, --cloud-profile           | TEXT                                    | Cloud account profile                             |
| -cc, --cloud-account-key       | TEXT                                    | Cloud account access key                          |
| -cs, --cloud-account-secret    | TEXT                                    | Cloud account access secret                       |
| -r, --cloud-region             | TEXT                                    | Cloud region                                      |
| -n, --cluster-name             | TEXT                                    | Cluster name                                      |
| -d, --dns-registrar            | [route53]                               | DNS registrar                                     |
| -dt, --dns-registrar-token     | TEXT                                    | DNS registrar token                               |
| -dk, --dns-registrar-key       | TEXT                                    | DNS registrar key                                 |
| -ds, --dns-registrar-secret    | TEXT                                    | DNS registrar secret                              |
| -dn, --domain-name             | TEXT                                    | Domain name for the Kubernetes cluster            |
| -g, --git-provider             | [github]                                | Git provider                                      |
| -go, --git-org                 | TEXT                                    | Git organization name                             |
| -gt, --git-access-token        | TEXT                                    | Git access token                                  |
| -grn, --gitops-repo-name       | TEXT                                    | GitOps repository name                            |
| -gtu, --gitops-template-url    | TEXT                                    | GitOps repository template URL                    |
| -gtu, --gitops-template-url    | TEXT                                    | GitOps repository template URL                    |
| -gtb, --gitops-template-branch | TEXT                                    | GitOps repository template branch                 |
| -dw, --setup-demo-workload     | Flag                                    | Flag to set up a demo workload                    |
| -f, --config-file              | FILENAME                                | File to load setup parameters from                |
| --verbosity                    | [DEBUG, INFO, WARNING, ERROR, CRITICAL] | Logging verbosity level, defaults to CRITICAL     |

> **Note!**: Use kebab-case for all parameter names.

### Examples

**Using command arguments:**

```bash
cgdevxcli setup --email user@cgdevx.io \
                --cloud-provider aws \
                --cloud-profile your-profile-name \
                --cluster-name cluster-name \
                --dns-registrar route53 \
                --domain-name example.com \
                --git-provider github \
                --git-org acmeinc \
                --git-access-token ghp_xxx \
                --gitops-repo-name gitops-repo-name

Using a parameter file:
cgdevxcli setup -f path/to/your/parameters.yaml

Troubleshooting
The installation of a reference architecture is a complex process that depends on multiple factors, such as cloud resource availability, connection speed, and image registry rate limits. While we do our best to handle common problems and provide an uninterrupted experience, the setup process may still fail. If you encounter connectivity or resource availability errors, please try restarting the setup process. It should resume from the step where it previously failed.

Destroy

This command destroys all resources created during the setup process, effectively reversing the setup. It uses local state data created during the setup.

What the destroy command deletes:
K8s cluster and supporting cloud resources provisioned by the CG DevX CLI
GitOps repository created under the Git provider of your choice
Remote backend storage (e.g., AWS S3) used for IaC
All local files created by the CG DevX CLI
NOTE: This process is irreversible.
NOTE: This operation will delete all workload repositories. If workloads have any out-of-cluster (cloud provider) resources, they will become orphaned and should be manually deleted. It is highly recommended to delete all active workloads and associated resources before destroying your installation. See more on the workload delete command with the --destroy-resources flag here.
Arguments:

Name (short, full)	Type	Description
--verbosity	[DEBUG, INFO, WARNING, ERROR, CRITICAL]	Set the logging verbosity level, default CRITICAL

Command Snippet:
cgdevxcli destroy
```

### Troubleshooting

Setup Troubleshooting:
If the setup process encounters errors related to connectivity or resource availability, restart the process to resume from the last checkpoint.

Destroy Troubleshooting:
If destroying resources fails, especially the Kubernetes cluster, manual intervention may be required, such as deleting Load Balancers. For GitOps repository issues, ensure external action runners are removed before attempting deletion again.
