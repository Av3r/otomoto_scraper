################################################################################
# TERRAFORM OUTPUTS - Wartości zwracane po deploy
################################################################################
# Outputs = informacje wyświetlane po "terraform apply"
# Przydatne do:
# 1. Sprawdzenia URL/ARN utworzonych zasobów
# 2. Użycia w innych modułach Terraform
# 3. Integracji z CI/CD (GitHub Actions może czytać outputy)
################################################################################

output "ecr_repository_url" {
  description = "URL ECR repository (gdzie push Docker image)"
  value       = aws_ecr_repository.scraper.repository_url
}

output "ecr_registry_id" {
  description = "ID rejestru ECR"
  value       = aws_ecr_repository.scraper.registry_id
}

output "lambda_function_name" {
  description = "Nazwa funkcji Lambda"
  value       = aws_lambda_function.scraper.function_name
}

output "lambda_function_arn" {
  description = "ARN funkcji Lambda (pełny identyfikator w AWS)"
  value       = aws_lambda_function.scraper.arn
}

output "lambda_invoke_command" {
  description = "Komenda CLI do ręcznego uruchomienia Lambda"
  value       = "aws lambda invoke --function-name ${aws_lambda_function.scraper.function_name} --region ${var.aws_region} response.json"
}

output "cloudwatch_log_group" {
  description = "CloudWatch Log Group gdzie znajdziesz logi Lambda"
  value       = aws_cloudwatch_log_group.lambda.name
}

output "cloudwatch_logs_url" {
  description = "URL do CloudWatch Logs w AWS Console"
  value       = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#logsV2:log-groups/log-group/${replace(aws_cloudwatch_log_group.lambda.name, "/", "$252F")}"
}

output "eventbridge_rule_name" {
  description = "Nazwa EventBridge rule (scheduler)"
  value       = aws_cloudwatch_event_rule.scraper_schedule.name
}

output "eventbridge_schedule" {
  description = "Aktualny harmonogram uruchamiania"
  value       = aws_cloudwatch_event_rule.scraper_schedule.schedule_expression
}

output "eventbridge_enabled" {
  description = "Czy automatyczne uruchamianie jest włączone"
  value       = aws_cloudwatch_event_rule.scraper_schedule.is_enabled
}

output "s3_bucket_name" {
  description = "Nazwa S3 bucket gdzie zapisywane są wyniki"
  value       = var.s3_bucket_name
}

output "s3_console_url" {
  description = "URL do S3 bucket w AWS Console"
  value       = "https://s3.console.aws.amazon.com/s3/buckets/${var.s3_bucket_name}?region=${var.aws_region}"
}

################################################################################
# Jak używać outputs:
################################################################################
# 1. Wyświetl wszystkie outputs:
#    terraform output
#
# 2. Wyświetl konkretny output:
#    terraform output lambda_function_arn
#
# 3. Użyj w skrypcie bash:
#    LAMBDA_ARN=$(terraform output -raw lambda_function_arn)
#    aws lambda invoke --function-name $LAMBDA_ARN response.json
#
# 4. Eksportuj jako JSON:
#    terraform output -json > outputs.json
################################################################################
