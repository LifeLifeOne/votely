# Public address of the server, kept when the server is destroyed between work sessions: the
# hostname (votely.<ip>.sslip.io) and its HTTPS certificate stay the same. The server stack
# finds it by its Name tag.
resource "aws_eip" "server" {
  domain = "vpc"

  tags = {
    Name = "votely-server"
  }

  lifecycle {
    prevent_destroy = true
  }
}
