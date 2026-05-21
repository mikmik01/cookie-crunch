variable "github_repo" {
  description = "GitHub repo in owner/name format, e.g. mikmik01/cookie-crunch"
  type        = string
}

variable "github_repo_url" {
  description = "Full GitHub repo URL"
  type        = string
}

variable "branch" {
  type    = string
  default = "main"
}

variable "render_api_key" {
  type      = string
  sensitive = true
}

variable "render_owner_id" {
  type      = string
  sensitive = true
}

variable "vercel_api_token" {
  type      = string
  sensitive = true
}

variable "backend_name" {
  type    = string
  default = "cookie-crunch"
}

variable "frontend_name" {
  type    = string
  default = "cookie-crunch"
}

variable "database_url" {
  type      = string
  sensitive = true
}

variable "google_api_key" {
  type      = string
  sensitive = true
}

variable "frontend_domain" {
  description = "Optional final Vercel frontend URL for backend CORS later"
  type        = string
  default     = ""
}