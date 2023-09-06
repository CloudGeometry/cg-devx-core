# How to use this module to deploy a Kubernetes cluster on AWS
CGDevX is designed to take all of the relevant information for deploying a cluster on the command line, but for now you can use Terraform directly to deploy a cluster.
## Prerequisites:
- You must to have terraform installed and configured.
- You must to have the AWS CLI tool installed and configured with an AWS Access Key ID and AWS Secret Access Key.
- You must be able to clone the CGDevX repo.
Follow these steps:
1. Clone the repo: 
`git clone git@github.com:CloudGeometry/CGDevX-core.git`
2. Change to the folder with the template file, main.tf
`cd CGDevX-core/platform/terraform/hosting_provider`
3. Edit main.tf to include your own information. Because the file is structured to receive parameters from the Pythin CLI, you will need to manually replace the file’s content. Remove everything from main.tf and replace it with the terraform code block here:

```
terraform {
}

locals {
  name          = "demo-cluster"
  ProvisionedBy = "cgdevx"
}

# configure cloud provider through env variables
# AWS_REGION and AWS_PROFILE for local run and through assuming IAM role in CI runner
# so, for loval run required:
# export AWS_REGION="<CLOUD_REGION>"
# export AWS_PROFILE="<CLOUD_PROFILE>"
#
provider "aws" {
  default_tags {
    tags = {
      ClusterName   = local.name
      ProvisionedBy = local.ProvisionedBy
    }
  }
}

module "hosting-provider" {
#path to the module here
  source          = "../modules/cloud_aws"
  cluster_name    = local.name
  node_groups = [
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
4. Set the environment variables main.tf if you are using a named AWS profile
```
export AWS_REGION="us-west-1"
export AWS_PROFILE="REPLACE_HERE" # name of your profile here
```
5. Run `terraform init` and `apply`.
`terraform init & terraform apply -auto-approve`
6. Wait for 15-20 minutes. When the script is finished, you'll see the Kubernetes cluster running in your Amazone Elastic Kubernete Service console.
7. Remember, you're paying for these resources! You can clean up when you're finished with the `destroy` command.
`terrafrom destroy`

See module's variables [here](TERRAFORM-README.md)
