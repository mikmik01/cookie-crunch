variable "github_repo" {
  type        = string
  description = "GitHub repo in owner/name format, e.g. mikmik01/cookie-crunch"
}

variable "render_api_key" {
  type        = string
  sensitive   = true
}

variable "vercel_api_token" {
  type        = string
  sensitive   = true
}

variable "database_url" {
  type        = string
  sensitive   = true
}

variable "google_api_key" {
  type        = string
  sensitive   = true
}

variable "frontend_name" {
  type    = string
  default = "mlbb-drafter-frontend"
}

variable "backend_name" {
  type    = string
  default = "mlbb-drafter-backend"
}