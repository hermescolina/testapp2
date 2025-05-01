provider "github" {
  token = var.github_token
  owner = "hermescolina"
}

resource "github_repository" "testapp" {
  name        = "testapp"
  description = "A test app created via Terraform"
  visibility  = "public" # or "private"
  auto_init   = true
}

