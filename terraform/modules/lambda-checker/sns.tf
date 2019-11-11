resource "aws_sns_topic" "email_notifications" {
  name = "${var.function_name}-email-notifications-${var.environment}"
}
