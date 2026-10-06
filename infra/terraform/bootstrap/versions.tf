terraform {
  required_version = ">= 1.16"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.67"
    }
  }

  # The state of this configuration lives in the bucket it creates. First run: apply with a
  # local backend_override.tf, then delete it and run `terraform init -migrate-state`
  # (docs/en/INFRA.md).
  backend "s3" {
    bucket       = "votely-tfstate-08da0d86"
    key          = "bootstrap/terraform.tfstate"
    region       = "eu-west-1"
    encrypt      = true
    use_lockfile = true # native S3 locking, no DynamoDB table
  }
}

provider "aws" {
  region = var.region

  # Every resource is tagged, so costs and ownership are visible in the AWS console.
  default_tags {
    tags = {
      Project   = "votely"
      ManagedBy = "terraform"
      Stack     = "bootstrap"
    }
  }
}
