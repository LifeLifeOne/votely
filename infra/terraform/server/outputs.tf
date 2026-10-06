output "instance_id" {
  description = "ID of the server, used by Systems Manager."
  value       = aws_instance.server.id
}

output "public_ip" {
  description = "Permanent public address of the server."
  value       = data.aws_eip.server.public_ip
}

output "shell" {
  description = "Open a shell on the server (no SSH)."
  value       = "aws ssm start-session --target ${aws_instance.server.id}"
}
