# Image signing key (Cosign). The private key never leaves KMS: the CI asks AWS to sign a digest.
# Asymmetric keys cannot be rotated automatically; a new key means a new public key in the repo.
# nosemgrep: terraform.aws.security.aws-kms-no-rotation.aws-kms-no-rotation -- not available for asymmetric keys
resource "aws_kms_key" "cosign" {
  description              = "Votely container image signing (Cosign)"
  customer_master_key_spec = "ECC_NIST_P256"
  key_usage                = "SIGN_VERIFY"
  deletion_window_in_days  = 30

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_kms_alias" "cosign" {
  name          = "alias/votely-cosign"
  target_key_id = aws_kms_key.cosign.key_id
}
