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
  description = "Size of the encrypted system disk (cluster data lives on the persistent disk)."
  type        = number
  default     = 20
}

variable "k3s_version" {
  description = "k3s release installed at first boot (same Kubernetes minor as the local kind cluster)."
  type        = string
  default     = "v1.36.5+k3s1"
}
