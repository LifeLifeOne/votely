# GitLab CI authenticates to AWS with OpenID Connect: each job receives a short-lived token
# signed by GitLab, exchanged for temporary credentials. No AWS key is stored in GitLab.
resource "aws_iam_openid_connect_provider" "gitlab" {
  url            = "https://gitlab.com"
  client_id_list = ["sts.amazonaws.com"]
}

locals {
  # Token subject: which project and which branch the job runs for.
  gitlab_subject = "project_path:${var.gitlab_project_path}:ref_type:branch:ref"
}

# Assume-role policy shared by the CI roles; only the subject differs.
data "aws_iam_policy_document" "gitlab_assume" {
  for_each = {
    plan   = "${local.gitlab_subject}:*"                  # any branch of the project
    signer = "${local.gitlab_subject}:${var.gitlab_main}" # the default branch only
  }

  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.gitlab.arn]
    }
    condition {
      test     = "StringEquals"
      variable = "gitlab.com:aud"
      values   = ["sts.amazonaws.com"]
    }
    # Pipelines of forks carry their own project path, so they can never match.
    condition {
      test     = "StringLike"
      variable = "gitlab.com:sub"
      values   = [each.value]
    }
  }
}

# Read-only role for `terraform plan` in merge requests: it can see, never change.
resource "aws_iam_role" "ci_plan" {
  name                 = "votely-ci-plan"
  assume_role_policy   = data.aws_iam_policy_document.gitlab_assume["plan"].json
  max_session_duration = 3600
}

resource "aws_iam_role_policy_attachment" "ci_plan_read_only" {
  role       = aws_iam_role.ci_plan.name
  policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}

# Signing role, for pipelines of the default branch only: it may sign with the Cosign key and
# nothing else.
resource "aws_iam_role" "ci_signer" {
  name                 = "votely-ci-signer"
  assume_role_policy   = data.aws_iam_policy_document.gitlab_assume["signer"].json
  max_session_duration = 3600
}

data "aws_iam_policy_document" "ci_signer" {
  statement {
    actions   = ["kms:Sign", "kms:GetPublicKey", "kms:DescribeKey"]
    resources = [aws_kms_key.cosign.arn]
  }
}

resource "aws_iam_role_policy" "ci_signer" {
  name   = "cosign-sign"
  role   = aws_iam_role.ci_signer.id
  policy = data.aws_iam_policy_document.ci_signer.json
}
