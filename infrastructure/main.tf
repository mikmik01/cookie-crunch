resource "render_web_service" "backend" {
  name   = var.backend_name
  plan   = "free"
  region = "singapore"

  runtime_source = {
    docker = {
      auto_deploy     = true
      branch          = var.branch
      repo_url        = var.github_repo_url
      dockerfile_path = "backend/Dockerfile"
      docker_context  = "."
    }
  }

  env_vars = {
    DATABASE_URL = {
      value = var.database_url
    }

    GOOGLE_API_KEY = {
      value = var.google_api_key
    }

    RUN_MIGRATIONS_ON_STARTUP = {
      value = "true"
    }

    RUN_SCRAPE_ON_STARTUP = {
      value = "true"
    }
  }
}

data "vercel_project_directory" "frontend" {
  path = "../frontend"
}

resource "vercel_deployment" "frontend" {
  project_id  = vercel_project.frontend.id
  files       = data.vercel_project_directory.frontend.files
  path_prefix = "../frontend"
  production  = true

  depends_on = [
    vercel_project.frontend,
    render_web_service.backend
  ]
}

resource "vercel_project" "frontend" {
  name      = var.frontend_name
  framework = "vite"

  git_repository = {
    type = "github"
    repo = var.github_repo
  }

  root_directory = "frontend"

  build_command    = "npm run build"
  output_directory = "dist"

  environment = [
    {
      key    = "VITE_API_BASE_URL"
      value  = "https://${render_web_service.backend.name}.onrender.com"
      target = ["production", "preview"]
      sensitive = false
    }
  ]
}