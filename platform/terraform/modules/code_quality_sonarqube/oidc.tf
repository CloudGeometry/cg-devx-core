resource "sonarqube_setting" "oidc_enabled" {
  key   = "sonar.auth.oidc.enabled"
  value = "true"
}

# Auto-Login can be skipped by using the URL "<sonarServerBaseURL>/?auto-login=false".
resource "sonarqube_setting" "oidc_autologin" {
  key   = "sonar.auth.oidc.autoLogin"
  value = "false"
}

resource "sonarqube_setting" "oidc_scopes" {
  key   = "sonar.auth.oidc.scopes"
  value = "openid groups user profile email"
}

resource "sonarqube_setting" "oidc_idtokensigalg" {
  key   = "sonar.auth.oidc.idTokenSigAlg"
  value = "RS256"
}

resource "sonarqube_setting" "oidc_allowuserstosignup" {
  key   = "sonar.auth.oidc.allowUsersToSignUp"
  value = "true"
}

resource "sonarqube_setting" "oidc_loginstrategy" {
  key   = "sonar.auth.oidc.loginStrategy"
  value = "Preferred username"
}

resource "sonarqube_setting" "oidc_loginstrategy_customclaim" {
  key   = "sonar.auth.oidc.loginStrategy.customClaim.name"
  value = "upn"
}

resource "sonarqube_setting" "oidc_groupssync" {
  key   = "sonar.auth.oidc.groupsSync"
  value = "true"
}

resource "sonarqube_setting" "oidc_groupssync_claimmame" {
  key   = "sonar.auth.oidc.groupsSync.claimName"
  value = "groups"
}

resource "sonarqube_setting" "oidc_loginbuttontext" {
  key   = "sonar.auth.oidc.loginButtonText"
  value = "OpenID SSO Connect"
}


