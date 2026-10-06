output "state_bucket" {
  description = "S3 bucket holding the Terraform states of the project."
  value       = aws_s3_bucket.state.id
}
