cluster_name = "gxc"
node_groups = [
  {
    name           = "gr1"
    instance_types = ["t3.small"]
    desired_size   = 3
    min_size       = 2
    max_size       = 5
    capacity_type  = "on-demand"

  },
  {
    instance_types = ["t3.medium", "t3.small"]
    desired_size   = 2
    capacity_type  = "spot"
  }
]
#cluster_node_labels = "label1=value1,label2=value2"
