terraform {
  required_version = ">= 1.5.0"

  required_providers {
    vercel = {
      source  = "vercel/vercel"
      version = "~> 3.0"
    }

    render = {
      source  = "render-oss/render"
      version = "~> 1.6"
    }
  }
}

provider "vercel" {
  api_token = var.vercel_api_token
}

provider "render" {
  api_key = var.render_api_key
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
}

resource "render_web_service" "backend" {
  name   = var.backend_name
  region = "singapore"

  runtime_source = {
    docker = {
      repo_url        = "https://github.com/${var.github_repo}"
      branch          = "main"
      dockerfile_path = "backend/Dockerfile"
      docker_context  = "."
    }
  }

  plan = "free"

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