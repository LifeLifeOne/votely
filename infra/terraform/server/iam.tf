# The server's identity: it may only register with Systems Manager, which gives a shell
# (`aws ssm start-session`) to people signed in through IAM Identity Center. No SSH key exists.
resource "aws_iam_role" "server" {
  name = "votely-server"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.server.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "server" {
  name = "votely-server"
  role = aws_iam_role.server.name
}
