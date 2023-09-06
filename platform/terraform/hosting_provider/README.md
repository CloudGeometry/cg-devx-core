# Platform IaC - Cloud Infrastructure

This is your platform Infrastructure as Code (IaC) Cloud Infrastructure main folder.
CGDevX is designed to manage (generate, parametrise, and execute) IaC programmatically.

## Modules

All the cloud resources are isolated within "provisioning modules" designed to hide the complexity associated with
provisioning and management of a specific resource(s).
They serve as abstraction layer and hides cloud specific implementation details from the consumer.

### Cloud provisioning module parameter

#### Input

```terraform
# cloud region
region = "provider specific"
# K8s cluster network CIDR
cluster_network_cidr = "10.0.0.0/16"
# K8s cluster name
cluster_name = "cgdevx"
# Number of availability zones
az_count = 3
# K8s cluster version
cluster_version = "provider specific"
# array, represents K8s node groups
node_groups = [
    {
        # optional, node group name
        name           = "default"
        # compute node type (size), will fall back to the next value when the
        # first specified instance type is not available, 
        # could be used in combination with capacity_type = "spot"
        instance_types = ["provider specific"]
        # min node count for cluster
        min_size       = 3
        # max node count for cluster
        max_size       = 5
        # desired node count for cluster
        desired_size   = 3
        # "on-demand" or "spot"
        capacity_type  = "ON_DEMAND"
    }
]
# K8s node labels
cluster_node_labels = ["cgdevx"]
# ssh public keys used to connect to nodes
ssh_public_key = ""
# list of emails subscribed to cloud native resource downtime alarms
alert_emails = [""]


```

#### Output

