variable "region" {
  description = "AWS region of the state bucket and of the whole project."
  type        = string
  default     = "eu-west-1"
}

variable "budget_limit_usd" {
  description = "Monthly cost alert threshold, in the account currency (USD)."
  type        = number
  default     = 10
}

variable "budget_email" {
  description = "Address that receives the budget alerts. Kept out of Git (terraform.tfvars)."
  type        = string
  sensitive   = true
}
