# kaniko-cache project
resource "harbor_project" "kaniko-cache" {
  name = "kaniko-cache"
  vulnerability_scanning      = false
}

resource "harbor_retention_policy" "main" {
    scope = harbor_project.kaniko-cache.id
    schedule = "Daily"
    rule {
        n_days_since_last_pull = 5
        repo_matching = "**"
        tag_matching = "**"
    }
    rule {
        n_days_since_last_push = 10
        repo_matching = "**"
        tag_matching = "**"
    }

}
