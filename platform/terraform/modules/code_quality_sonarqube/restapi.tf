# check the issue later, probably they will resolve soon
#https://github.com/jdamata/terraform-provider-sonarqube/issues/91

resource "restapi_object" "put_issueruri" {

  create_method  = "POST"
  create_path    = "/api/settings/set"
  update_method  = "POST"
  update_path    = "/api/settings/set"
  destroy_method = "POST"
  destroy_path   = "/api/settings/reset"
  read_method    = "GET"
  read_path      = "/api/settings/values"


  debug        = true
  path         = "/api/settings/"
  query_string = "key=sonar.auth.oidc.issuerUri&value=${var.oidc_endpoint}"
  data         = "{}"
  object_id    = "sonar.auth.oidc.issuerUri"
}

resource "restapi_object" "put_oidc_clientid" {

  create_method  = "POST"
  create_path    = "/api/settings/set"
  update_method  = "POST"
  update_path    = "/api/settings/set"
  destroy_method = "POST"
  destroy_path   = "/api/settings/reset"
  read_method    = "GET"
  read_path      = "/api/settings/values"


  debug        = true
  path         = "/api/settings/"
  query_string = "key=sonar.auth.oidc.clientId.secured&value=${var.oidc_client_id}"
  data         = "{}"
  object_id    = "sonar.auth.oidc.clientId.secured"
}

resource "restapi_object" "put_oidc_clientsecret" {

  create_method  = "POST"
  create_path    = "/api/settings/set"
  update_method  = "POST"
  update_path    = "/api/settings/set"
  destroy_method = "POST"
  destroy_path   = "/api/settings/reset"
  read_method    = "GET"
  read_path      = "/api/settings/values"


  debug        = true
  path         = "/api/settings/"
  query_string = "key=sonar.auth.oidc.clientSecret.secured&value=${var.oidc_client_secret}"
  data         = "{}"
  object_id    = "sonar.auth.oidc.clientSecret.secured"
}
