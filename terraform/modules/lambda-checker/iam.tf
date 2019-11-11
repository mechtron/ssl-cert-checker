resource "aws_iam_role" "lambda_role" {
  name = "${var.function_name}-${var.environment}"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF

}

resource "aws_iam_role_policy_attachment" "amazon_lambda_exec_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "send_sns_sms" {
  name = "send-sns-email-messages"
  role = aws_iam_role.lambda_role.name

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "SetupSnsTopic",
            "Effect": "Allow",
            "Action": [
                "SNS:GetSubscriptionAttributes",
                "SNS:ListSubscriptionsByTopic",
                "SNS:Publish",
                "SNS:Subscribe"
            ],
            "Resource": "${aws_sns_topic.email_notifications.arn}"
        },
        {
            "Sid": "SendSnsEmail",
            "Effect": "Allow",
            "Action": [
                "SNS:Publish"
            ],
            "Resource": "*"
        },
        {
            "Sid": "DynamoDbScanGetPutUpdate",
            "Effect": "Allow",
            "Action": [
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:GetItem",
                "dynamodb:BatchGetItem",
                "dynamodb:UpdateItem",
                "dynamodb:PutItem"
            ],
            "Resource": [
              "${aws_dynamodb_table.dynamodb_table_checks.arn}",
              "${aws_dynamodb_table.dynamodb_table_failures.arn}"
            ]
        }
    ]
}
EOF
}
