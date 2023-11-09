resource "sonarqube_group" "admins" {
  name        = "admins"
  description = "This is a vault admin group"
}

resource "sonarqube_group" "developers" {
  name        = "developers"
  description = "This is a vault developers group"
}

resource "sonarqube_permissions" "admins" {
  depends_on  = [sonarqube_group.admins]
  group_name  = "admins"
  permissions = ["admin"]
}

# Valid values are [admin, gateadmin, profileadmin, provisioning, scan]
# incorrect documentation here https://registry.terraform.io/providers/jdamata/sonarqube/latest/docs/resources/sonarqube_permissions
resource "sonarqube_permissions" "developers" {
  depends_on  = [sonarqube_group.developers]
  group_name  = "developers"
  permissions = ["gateadmin", "scan"]
}