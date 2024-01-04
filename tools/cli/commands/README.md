# CG DevX CLI commands

Below is a list of commands supported by CG DevX CLI tool.

## Setup

Creates and configures reference implementation of CG DevX K8s Internal Developer Platform (IDP) kit.
CLI tool saves intermediate state to a local file when running through multiple steps of the setup proces (AKA
checkpoints) and could be re-run

`setup` command checks:

- Cloud CLI tools presence
- Cloud account permission using profile or access keys you provided
- DNS provider permission using token or access keys you provided
- Domain ownership

`setup` command creates:

- SSH key pairs
- Remote backend storage (e.g., AWS S3) used for IaC
- GitOps repository created under Git provider of your choice
- K8s cluster and supporting cloud resources provisioned by CG DevX CLI

`setup` command could be executed using arguments, environment variables, or input file.

**Arguments**:

| Name (short, full)             | Type                                    | Description                                       |
|--------------------------------|-----------------------------------------|---------------------------------------------------|
| -e, --email                    | TEXT                                    | Email address used for alerts                     |
| -c, --cloud-provider           | [aws]                                   | Cloud provider type                               |
| -cp, --cloud-profile           | TEXT                                    | Cloud account profile                             |
| -cc, --cloud-account-key       | TEXT                                    | Cloud account access key                          |
| -cs, --cloud-account-secret    | TEXT                                    | Cloud account access secret                       |
| -r, --cloud-region             | TEXT                                    | Cloud regions                                     |
| -n, --cluster-name             | TEXT                                    | Cluster name                                      |
| -d, --dns-registrar            | [route53]                               | DNS registrar                                     |
| -dt, --dns-registrar-token     | TEXT                                    | DNS registrar token                               |
| -dk, --dns-registrar-key       | TEXT                                    | DNS registrar key                                 |
| -ds, --dns-registrar-secret    | TEXT                                    | DNS registrar secret                              |
| -dn, --domain-name             | TEXT                                    | Domain-name used by K8s cluster                   |
| -g, --git-provider             | [github]                                | Git provider                                      |
| -go, --git-org                 | TEXT                                    | Git organization name                             |
| -gt, --git-access-token        | TEXT                                    | Git access token                                  |
| -grn, --gitops-repo-name       | TEXT                                    | GitOps repository name                            |
| -gtu, --gitops-template-url    | TEXT                                    | GitOps repository template url                    |
| -gtb, --gitops-template-branch | TEXT                                    | GitOps repository template branch                 |
| -dw, --setup-demo-workload     | Flag                                    | Setup demo workload                               |
| -f, --config-file              | FILENAME                                | Load parameters from file                         |
| --verbosity                    | [DEBUG, INFO, WARNING, ERROR, CRITICAL] | Set the logging verbosity level, default CRITICAL |

> **Note!**: For all names use kebab-case.

`parameters.yaml` file example

```yaml
email: user@cgdevx.io
cloud-provider: aws
cloud-profile: profile-name
cloud-region: eu-west-1
cluster-name: cluster-name
dns-registrar: route53
domain-name: demo.cgdevx.io
git-provider: github
git-org: CGDevX
git-access-token: ghp_xxx
gitops-repo-name: cgdevx-gitops
```

**Command snippet**

Using command arguments

```bash
cgdevxcli setup --email user@cgdevx.io \ 
                --cloud-provider aws 
                --cloud-profile your-profile-name \ 
                --cluster-name cluster-name \ 
                --dns-registrar route53 \
                --domain-name example.com \ 
                --git-provider github \
                --git-org acmeinc \
                --git-access-token ghp_xxx \
                --gitops-repo-name gitops-repo-name
```

Using parameter file

```bash
cgdevxcli setup -f path/to/your/parameters.yaml
```

### Troubleshooting

Installation of a reference architecture is a complex process depending on multiple factors, e.g., cloud resource
availability, connection speed, image registry rate limits, etc. While we do our best to handle the most common problems
and provide uninterrupted experience, the setup process could still fail.
If you have connectivity or resource availability errors, please try restarting the
setup.
It should resume from the step when it failed previously.

## Destroy

Destroys all the resources created by setup process AKA reverse setup. It uses local state data created by setup
process.

`destroy` command deletes:

- K8s cluster and supporting cloud resources provisioned by CG DevX CLI
- GitOps repository created under Git provider of your choice
- Remote backend storage (e.g., AWS S3) used for IaC
- All local files created by CG DevX CLI

> **NOTE!**: this process is irreversible

> **NOTE!**: This operation will delete all workload repositories if you have them.
> If workloads have any out of the cluster (cloud provider) resources, they will become orphaned,
> and should be deleted manually.
> It is highly recommended prior to destroying your installation to delete all active workloads first also deleting all
> the resources.
> Please see more on `workload delete` command with `--destroy-resources` flag [here](workload/README.md#delete).


**Arguments**:

| Name (short, full) | Type                                    | Description                                       |
|--------------------|-----------------------------------------|---------------------------------------------------|
| --verbosity        | [DEBUG, INFO, WARNING, ERROR, CRITICAL] | Set the logging verbosity level, default CRITICAL |

**Command snippet**

```bash
cgdevxcli destroy
```

### Troubleshooting

Some of the resources used by reference architecture are created dynamically in a run time.
When doing cleanup, we are trying to destroy those temporary resources,
and then all other resources created by our automation.
The cleanup process could still fail.
If you have any issues, please try restarting the process.
If it fails to delete your K8s cluster, please try deleting Load Balancer(s) manually and restart the process.
For GitHub, external action runners should be removed prior to repository deletion.
If it fails to delete your GitOps repo - please check and remove runners and restart the process.