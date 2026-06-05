output "render_backend_service_id" {
  value = render_web_service.backend.id
}

output "render_backend_url" {
  value = "https://${render_web_service.backend.name}.onrender.com"
}

output "vercel_frontend_project_id" {
  value = vercel_project.frontend.id
}

output "vercel_frontend_deployment_url" {
  value = "https://${vercel_deployment.frontend.url}"
}