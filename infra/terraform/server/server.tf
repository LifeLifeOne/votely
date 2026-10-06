# Latest Amazon Linux 2023 image, published by AWS (Systems Manager agent included).
data "aws_ssm_parameter" "al2023" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

# Permanent address created by the bootstrap stack.
data "aws_eip" "server" {
  tags = {
    Name = "votely-server"
  }
}

resource "aws_instance" "server" {
  ami                    = data.aws_ssm_parameter.al2023.value
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.server.id]
  iam_instance_profile   = aws_iam_instance_profile.server.name

  # IMDSv2 only, one network hop: containers cannot read the instance credentials.
  metadata_options {
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }

  root_block_device {
    volume_type           = "gp3"
    volume_size           = var.root_volume_size_gb
    encrypted             = true
    delete_on_termination = true
  }

  tags = {
    Name = "votely-server"
  }

  lifecycle {
    # A newer image is picked when the server is recreated, never by replacing a running one.
    ignore_changes = [ami]
  }
}

resource "aws_eip_association" "server" {
  instance_id   = aws_instance.server.id
  allocation_id = data.aws_eip.server.id
}
