# AWS provisioning module

This provisioning module is designed to hide the complexity associated with provisioning and management of EKS cluster
and all underlying and connected resources.
Our intention is to follow all the best practices described in, so you should not worry about them:

- [Well-Architected Framework](https://wa.aws.amazon.com/index.en.html)
- [EKS best practices](https://github.com/aws/aws-eks-best-practices)

CG DevX is designed to use this module internally, but you can use it directly to deploy a K8s cluster.

## Adding and testing your changes

To be able to contribute and rung this module, you should follow the simple steps described below.

### Prerequisites

You should have:

- terraform installed and configured;
- AWS CLI tool installed and configured to access your target AWS account;
- (optionally) K8s CLI - kubectl;
- CG DevX repo.

Please note that CG DevX uses specific versions of terraform and kubectl.

### Development

_Please note that cloud module must follow input and output parameter schema
described [here](../../hosting_provider/README.md). Cloud module serves as abstraction layer and hides cloud-specific
implementation details from the consumer. All the AWS specific configuration and services dependencies should be kept
within `cloud_aws`._

When done changes, please make sure that you've updated terraform docs and module architecture diagrams.

### How to run locally

1. Navigate to the terraform entry point [folder](../../hosting_provider) containing the template
   file [main.tf](../../hosting_provider/main.tf)
   `cd platform/terraform/hosting_provider`
2. As [main.tf](../../hosting_provider/main.tf) is a entry point with all the content generated programmatically, you
   must fill in terraform provider calls manually We suggest you remove all the content from main.tf and replace it with
   the snippet below:

```terraform
terraform {
}

locals {
  name          = "test-cluster"
  ProvisionedBy = "CGDevX"
}

# configure through env variables AWS_REGION and AWS_PROFILE for local
# export AWS_REGION="<CLOUD_REGION>"
# export AWS_PROFILE="<CLOUD_PROFILE>"

provider "aws" {
  default_tags {
    tags = {
      ClusterName   = local.name
      ProvisionedBy = local.ProvisionedBy
    }
  }
}

module "hosting-provider" {
  # path to the module here
  source       = "../modules/cloud_aws"
  cluster_name = local.name
  node_groups  = [
    {
      name           = "gr1"
      instance_types = ["t3.medium"]
      min_size       = 1
      max_size       = 3
      desired_size   = 2
      capacity_type  = "ON_DEMAND"

    },
    {
      name           = "gr2-spot"
      instance_types = ["t3.medium", "t3.small"]
      min_size       = 1
      max_size       = 3
      desired_size   = 2
      capacity_type  = "SPOT"
    }
  ]
}
```

3. Set the `AWS_REGION` and `AWS_PROFILE` environment variables in main.tf if you are using a named AWS profile, as
   shown in an example below:

```
export AWS_REGION="us-west-1"
export AWS_PROFILE="REPLACE_ME_WITH_PROFILE_NAME"
```

4. Run `terraform init` followed by `terraform apply`. You could use this one-liner with auto approve
   flag `terraform init & terraform apply -auto-approve`.

The whole process could take around 15-20 minutes, or more, depending on resource availability in a chosen region. When
finished, you should be able to see the K8s cluster running in
your [Amazon EKS console](https://console.aws.amazon.com/eks/home?#/clusters).

Remember, those resources are not free. Please clean up when you're done with your changes by
running `terraform destroy` command.

For more details, please see module's variables [here](TERRAFORM-README.md)
