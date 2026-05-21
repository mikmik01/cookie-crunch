output "frontend_project_id" {
  value = vercel_project.frontend.id
}

output "backend_service_id" {
  value = render_web_service.backend.id
}