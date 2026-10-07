# Latest Amazon Linux 2023 image, published by AWS (Systems Manager agent included).
data "aws_ssm_parameter" "al2023" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

# Permanent address and data disk, created by the bootstrap stack.
data "aws_eip" "server" {
  tags = {
    Name = "votely-server"
  }
}

data "aws_ebs_volume" "data" {
  filter {
    name   = "tag:Name"
    values = ["votely-data"]
  }
}

locals {
  # Fixed private address: Kubernetes identifies the node by name and address, so a new server
  # takes over the cluster stored on the data disk instead of appearing as an unknown node.
  private_ip = cidrhost(aws_subnet.public.cidr_block, 10)
}

resource "aws_instance" "server" {
  ami                    = data.aws_ssm_parameter.al2023.value
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.server.id]
  iam_instance_profile   = aws_iam_instance_profile.server.name
  private_ip             = local.private_ip

  # First boot: mount the data disk, then install k3s on it (cloud-init.sh.tftpl).
  user_data_replace_on_change = true
  user_data = templatefile("${path.module}/cloud-init.sh.tftpl", {
    k3s_version    = var.k3s_version
    data_volume_id = replace(data.aws_ebs_volume.data.id, "-", "")
    public_ip      = data.aws_eip.server.public_ip
  })

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

resource "aws_volume_attachment" "data" {
  device_name = "/dev/sdf"
  volume_id   = data.aws_ebs_volume.data.id
  instance_id = aws_instance.server.id

  # On destroy, stop the instance first so the disk is detached cleanly.
  stop_instance_before_detaching = true
}

resource "aws_eip_association" "server" {
  instance_id   = aws_instance.server.id
  allocation_id = data.aws_eip.server.id
}
