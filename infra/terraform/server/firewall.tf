# Only the web ports are open to the internet. There is no SSH and the Kubernetes API is not
# exposed: administration goes through AWS Systems Manager (outbound connection from the server).
resource "aws_security_group" "server" {
  name        = "votely-server"
  description = "Votely server: HTTP and HTTPS in, everything out"
  vpc_id      = aws_vpc.main.id

  tags = {
    Name = "votely-server"
  }
}

resource "aws_vpc_security_group_ingress_rule" "web" {
  for_each = { http = 80, https = 443 }

  security_group_id = aws_security_group.server.id
  description       = upper(each.key)
  ip_protocol       = "tcp"
  from_port         = each.value
  to_port           = each.value
  cidr_ipv4         = "0.0.0.0/0"
}

# Outbound: package and image downloads, Let's Encrypt, Systems Manager.
resource "aws_vpc_security_group_egress_rule" "all" {
  security_group_id = aws_security_group.server.id
  description       = "All outbound traffic"
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}
