# Shared by every Terraform stack: run `tflint --chdir=<stack> --config=$PWD/.tflint.hcl`.
plugin "terraform" {
  enabled = true
  preset  = "recommended"
  version = "0.15.0"
  source  = "github.com/terraform-linters/tflint-ruleset-terraform"
}

# AWS-specific checks: invalid instance types, regions, deprecated arguments…
plugin "aws" {
  enabled = true
  version = "0.49.0"
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
}
