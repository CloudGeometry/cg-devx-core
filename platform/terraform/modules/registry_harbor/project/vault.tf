locals {
  b64_docker_auth = base64encode("robot@${var.project_name}+robot:${random_password.robot_password.result}")
  push_b64_docker_auth = base64encode("push-robot@${var.project_name}+robot:${random_password.push_robot_password.result}")
}

resource "vault_generic_secret" "docker_config" {
  path = "workloads/${var.project_name}/dockerconfigjson"

  data_json = jsonencode(
    {
      dockerconfig = jsonencode({ "auths" : { "<REGISTRY_INGRESS_URL>" : { "auth" : "${local.b64_docker_auth}" } } }),
    }
  )

}

resource "vault_generic_secret" "push_docker_config" {
  path = "workloads/${var.project_name}/push_dockerconfigjson"

  data_json = jsonencode(
    {
      dockerconfig = jsonencode({ "auths" : { "<REGISTRY_INGRESS_URL>" : { "auth" : "${local.push_b64_docker_auth}" } } }),
    }
  )

}

resource "vault_generic_secret" "harbor_workload_robot_secret" {
  path = "workloads/${var.project_name}/workload-robots-auth"

  data_json = jsonencode(
    {
      WL_ROBOT_NAME     = "robot@${var.project_name}+robot",
      WL_ROBOT_PASSWORD = random_password.robot_password.result,
      WL_ROBOT_B64_AUTH = local.b64_docker_auth,
      WL_PUSH_ROBOT_NAME     = "push-robot@${var.project_name}+robot",
      WL_PUSH_ROBOT_PASSWORD = random_password.push_robot_password.result,
      WL_PUSH_ROBOT_B64_AUTH = local.push_b64_docker_auth,
    }
  )

}