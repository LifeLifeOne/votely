variable "region" {
  description = "AWS region of the server."
  type        = string
  default     = "eu-west-1"
}

variable "instance_type" {
  description = "EC2 instance type: 2 vCPU / 8 GiB fits k3s, Argo CD, monitoring and both environments."
  type        = string
  default     = "t3a.large"
}

variable "root_volume_size_gb" {
  description = "Size of the encrypted root volume (images, database volumes, logs)."
  type        = number
  default     = 30
}
