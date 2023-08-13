cluster_name = "pzdc"
node_groups = [
  {
    #  name          = "gr1"
    instance_type = "t3.small"
  },
  {
    #instance_type = "t3.medium"
    override_instance_types = ["t3.medium", "t3.small"]
    instance_market_options = {
      market_type = "spot"
    }
  }
]
