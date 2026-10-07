# Minimal network: one VPC, one public subnet, an internet gateway. No NAT gateway (it would cost
# more than the server): the only instance has a public address of its own.
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16" # distinct from the k3s pod (10.42/16) and service (10.43/16) ranges
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "votely"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "votely"
  }
}

resource "aws_subnet" "public" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = data.aws_ebs_volume.data.availability_zone # where the persistent disk is

  tags = {
    Name = "votely-public"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "votely-public"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# The default security group of the VPC is emptied: nothing can use it by accident.
resource "aws_default_security_group" "default" {
  vpc_id = aws_vpc.main.id
}
