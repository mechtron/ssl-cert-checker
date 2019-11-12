locals {
  zip_output_path = "ssl-cert-checker.zip"
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${var.repo_root_path}/checker/"
  output_path = local.zip_output_path
}

resource "aws_lambda_function" "lambda_function" {
  filename         = local.zip_output_path
  function_name    = "${var.function_name}-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "checker.handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime          = "python3.6"
  memory_size      = "256"
  timeout          = "30"

  environment {
    variables = {
      DYNAMODB_TABLE_NAME_CHECKS = aws_dynamodb_table.dynamodb_table_checks.id
      DYNAMODB_TABLE_NAME_FAILURES = aws_dynamodb_table.dynamodb_table_failures.id
      SES_FROM_EMAIL = var.ses_from_email
    }
  }

  tags = {
    Name        = var.function_name
    Environment = var.environment
  }
}
