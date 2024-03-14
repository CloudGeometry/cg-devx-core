module "vpc" {
  source  = "terraform-google-modules/network/google"
  version = "~> 9.0.0"
  project_id   = local.project_id
  network_name = "${local.name}-vpc"
  routing_mode = "GLOBAL"
  subnets = [
    {
      subnet_name           = "${local.name}-public"
      subnet_ip             = cidrsubnet(local.vpc_cidr, 8, 100)
      subnet_region         = local.region
      subnet_private_access = "true"
      subnet_flow_logs      = "true"
      description           = "Public subnet for ${local.name}."
      subnet_labels         = {
        "Tier" = "public"
      }
    },
    {
      subnet_name           = "${local.name}-private"
      subnet_ip             = cidrsubnet(local.vpc_cidr, 4, 0)
      subnet_region         = local.region
      subnet_private_access = "true"
      subnet_flow_logs      = "true"
      description           = "Private subnet for ${local.name}."
      subnet_labels         = {
        "Tier" = "private"
      }
    },
    {
      subnet_name           = "${local.name}-infra"
      subnet_ip             = cidrsubnet(local.vpc_cidr, 8, 101)
      subnet_region         = local.region
      subnet_private_access = "true"
      subnet_flow_logs      = "true"
      description           = "Infrastructure subnet for ${local.name}."
      subnet_labels         = {
        "Tier" = "infra"
      }
    }
  ]
  secondary_ranges = {
    "${local.name}-private" = [
      # Secondary range for Pods
      {
        range_name    = "${local.name}-gke-pods"
        ip_cidr_range = cidrsubnet(local.vpc_cidr, 4, 1)
      },
      # Secondary range for services
      {
        range_name    = "${local.name}-gke-services"
        ip_cidr_range = cidrsubnet(local.vpc_cidr, 4, 2)
      }
    ]
  }
  routes = [
    {
      name              = "egress-internet-${local.name}"
      description       = "route through IGW to access internet"
      destination_range = "0.0.0.0/0"
      tags              = "egress-inet"
      next_hop_internet = "true"
    }
  ]
  depends_on = [
    google_project_service.kms_service,
    google_project_service.resource_manager_service,
    google_project_service.compute_engine_service,
    google_project_service.iam_service,
    google_project_service.iam_credentials_service,
    google_project_service.kubernetes_engine_service
  ]
}