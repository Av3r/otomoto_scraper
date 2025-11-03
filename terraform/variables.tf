################################################################################
# TERRAFORM VARIABLES - Input parameters (konfiguracja)
################################################################################
# Variables = parametry wejściowe dla Terraform
# Możesz je ustawić:
# 1. W pliku terraform.tfvars (wartości domyślne)
# 2. Przez CLI: terraform apply -var="aws_region=us-east-1"
# 3. Environment variables: TF_VAR_aws_region=us-east-1
################################################################################

variable "aws_region" {
  description = "AWS Region gdzie deploy infrastructure (Frankfurt = eu-central-1)"
  type        = string
  default     = "eu-central-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name używany w nazwach zasobów"
  type        = string
  default     = "otomoto-scraper"
}

################################################################################
# ECR (Docker Registry)
################################################################################

variable "ecr_repository_name" {
  description = "Nazwa ECR repository dla Docker images"
  type        = string
  default     = "otomoto-scraper"
}

################################################################################
# Lambda Configuration
################################################################################

variable "lambda_function_name" {
  description = "Nazwa funkcji Lambda"
  type        = string
  default     = "otomoto-scraper"
}

variable "lambda_memory_size" {
  description = "RAM dla Lambda w MB (128-10240). Więcej RAM = więcej CPU"
  type        = number
  default     = 512
  
  validation {
    condition     = var.lambda_memory_size >= 128 && var.lambda_memory_size <= 10240
    error_message = "Lambda memory musi być między 128 MB a 10240 MB."
  }
}

variable "lambda_timeout" {
  description = "Max czas wykonania Lambda w sekundach (1-900)"
  type        = number
  default     = 900  # 15 minut (max dla Lambda)
  
  validation {
    condition     = var.lambda_timeout >= 1 && var.lambda_timeout <= 900
    error_message = "Lambda timeout musi być między 1 a 900 sekund (15 minut)."
  }
}

################################################################################
# Application Configuration
################################################################################

variable "otomoto_url" {
  description = "URL Otomoto do scrapowania"
  type        = string
  default     = "https://www.otomoto.pl/osobowe/audi/a4"
}

variable "s3_bucket_name" {
  description = "Nazwa S3 bucket gdzie zapisywać wyniki"
  type        = string
  default     = "otomoto-scraper-2025"
}

################################################################################
# EventBridge (Scheduler) Configuration
################################################################################

variable "schedule_expression" {
  description = <<-EOT
    Wyrażenie cron/rate dla EventBridge.
    
    Przykłady:
    - "rate(6 hours)"         = co 6 godzin
    - "rate(1 day)"           = raz dziennie
    - "cron(0 2 * * ? *)"     = codziennie o 2:00 UTC
    - "cron(0 */4 * * ? *)"   = co 4 godziny
    - "cron(0 0 * * MON *)"   = każdy poniedziałek o północy
    
    Format cron: minute hour day month dayOfWeek year
    Uwaga: EventBridge używa UTC timezone!
  EOT
  type        = string
  default     = "rate(12 hours)"  # Domyślnie: co 12 godzin
}

variable "schedule_enabled" {
  description = "Czy włączyć automatyczne uruchamianie (true/false)"
  type        = bool
  default     = false  # Domyślnie wyłączone (uruchamiaj ręcznie)
}

################################################################################
# PRZYKŁADY UŻYCIA:
################################################################################
# 1. Użyj domyślnych wartości:
#    terraform apply
#
# 2. Nadpisz pojedynczą zmienną:
#    terraform apply -var="schedule_enabled=true"
#
# 3. Stwórz plik terraform.tfvars:
#    schedule_expression = "rate(6 hours)"
#    schedule_enabled    = true
#    lambda_memory_size  = 1024
#
# 4. Użyj environment variables:
#    export TF_VAR_aws_region="us-east-1"
#    terraform apply
################################################################################
