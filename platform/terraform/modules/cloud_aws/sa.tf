/*
 resource "kubernetes_service_account" "this" {
  metadata {
    name = "service-account2"
    namespace = "example"
    annotations = {
      "eks.amazonaws.com/role-arn" = "ROLE_ARN"
    }
  }
  automount_service_account_token = true
}

*/
