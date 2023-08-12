cluster_name = "pzdc"
node_groups = [{
  #  name          = "gr1"
  instance_type = "t3.medium"
  capacity_type = "on-demand"
  min_size      = 3
  max_size      = 5
  desired_size  = 3
  },
  {
    #  name          = "gr2"
    instance_type = "t3.medium"
    capacity_type = "on-demand"
    min_size      = 3
    max_size      = 5
    desired_size  = 3
  }
]
