output "state_bucket" {
  description = "S3 bucket holding the Terraform states of the project."
  value       = aws_s3_bucket.state.id
}

output "server_public_ip" {
  description = "Permanent public IP address of the server."
  value       = aws_eip.server.public_ip
}

output "cosign_key_alias" {
  description = "KMS alias used by Cosign (awskms:///alias/...)."
  value       = aws_kms_alias.cosign.name
}
