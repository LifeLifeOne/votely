# Persistent cluster data: k3s keeps everything here (database volumes, certificates, cluster
# state). The server is created and destroyed at will; this disk is attached to each new one,
# so the cluster comes back as it was. A disk can only be attached in its own availability zone:
# the server stack reads the zone from this volume.
resource "aws_ebs_volume" "data" {
  availability_zone = "${var.region}a"
  size              = var.data_volume_size_gb
  type              = "gp3"
  encrypted         = true

  tags = {
    Name = "votely-data"
  }

  lifecycle {
    prevent_destroy = true
  }
}
