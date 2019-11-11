variable "aws_region" {
  description = "The AWS region"
}

variable "environment" {
  description = "The service's environment"
}

variable "function_name" {
  description = "The Lambda function's name"
  default     = "ssl-cert-checker"
}

variable "repo_root_path" {
  description = "The hard path of this repository"
}
