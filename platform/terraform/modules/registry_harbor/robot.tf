resource "harbor_robot_account" "main" {
  name        = "main-robot"
  description = "server level robot account"
  level       = "system"
  secret      = var.registry_main_robot_password
  #modify permissions to required later

  permissions {
    kind      = "project"
    namespace = "*"

    access {
      action   = "create"
      resource = "scan"
    }
    access {
      action   = "create"
      effect   = "allow"
      resource = "artifact-label"
    }
    access {
      action   = "create"
      effect   = "allow"
      resource = "tag"
    }
    access {
      action   = "delete"
      effect   = "allow"
      resource = "tag"
    }
    access {
      action   = "list"
      resource = "tag"
    }
    access {
      action   = "list"
      effect   = "allow"
      resource = "artifact"
    }
    access {
      action   = "list"
      effect   = "allow"
      resource = "repository"
    }
    access {
      action   = "pull"
      effect   = "allow"
      resource = "repository"
    }
    access {
      action   = "push"
      effect   = "allow"
      resource = "repository"
    }
    access {
      action   = "read"
      effect   = "allow"
      resource = "artifact"
    }
    access {
      action   = "stop"
      resource = "scan"
    }
    access {
      action   = "delete"
      effect   = "allow"
      resource = "artifact-label"
    }
    access {
      action   = "delete"
      effect   = "allow"
      resource = "repository"
    }
    access {
      action   = "delete"
      effect   = "allow"
      resource = "artifact"
    }
  }
}

resource "harbor_robot_account" "proxy" {
  name        = "proxy-robot"
  description = "server level robot account for proxies"
  level       = "system"
  secret      = random_password.harbor_proxy_robot_password.result
  #modify permissions to required later

  permissions {
    kind      = "project"
    namespace = harbor_project.docker-hub-proxy.name

    access {
      action   = "pull"
      effect   = "allow"
      resource = "repository"
    }
  }
  permissions {
    kind      = "project"
    namespace = harbor_project.gcr-proxy.name

    access {
      action   = "pull"
      effect   = "allow"
      resource = "repository"
    }
  }
  permissions {
    kind      = "project"
    namespace = harbor_project.k8s-gcr-proxy.name

    access {
      action   = "pull"
      effect   = "allow"
      resource = "repository"
    }
  }
  permissions {
    kind      = "project"
    namespace = harbor_project.quay-proxy.name

    access {
      action   = "pull"
      effect   = "allow"
      resource = "repository"
    }
  }
}


resource "random_password" "harbor_proxy_robot_password" {
  length      = 22
  special     = false
  min_lower   = 1
  min_upper   = 1
  min_numeric = 1
}

resource "vault_generic_secret" "harbor_proxy_robot_secret" {
  path = "secret/harbor/proxy-robot-auth"

  data_json = jsonencode(
    {
      HARBOR_ROBOT_NAME     = "robot@proxy-robot",
      HARBOR_ROBOT_PASSWORD = random_password.harbor_proxy_robot_password.result,
      HARBOR_ROBOT_B64_AUTH = local.b64_proxy_docker_auth,
    }
  )
}


locals {
  b64_proxy_docker_auth = base64encode("robot@proxy-robot:${random_password.harbor_proxy_robot_password.result}")
}

resource "vault_generic_secret" "proxy_docker_config" {
  path = "secret/proxy_dockerconfigjson"

  data_json = jsonencode(
    {
      dockerconfig = jsonencode({ "auths" : { "<REGISTRY_INGRESS_URL>" : { "auth" : "${local.b64_proxy_docker_auth}" } } }),
    }
  )

}
