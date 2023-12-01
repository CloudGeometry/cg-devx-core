locals {
  b64_docker_auth = base64encode("robot@${var.project_name}+robot:${random_password.robot_password.result}")
}

resource "vault_generic_secret" "docker_config" {
  path = "workloads/${var.project_name}/dockerconfigjson"

  data_json = jsonencode(
    {
      dockerconfig = jsonencode({ "auths" : { "<REGISTRY_INGRESS_URL>" : { "auth" : "${local.b64_docker_auth}" } } }),
    }
  )

}

resource "vault_generic_secret" "harbor_main_robot_secret" {
  path = "workloads/${var.project_name}/workload-robot-auth"

  data_json = jsonencode(
    {
      HARBOR_ROBOT_NAME     = "robot@${var.project_name}+robot",
      HARBOR_ROBOT_PASSWORD = random_password.robot_password.result,
      HARBOR_ROBOT_B64_AUTH = local.b64_docker_auth,
    }
  )

}