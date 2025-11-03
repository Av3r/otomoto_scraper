################################################################################
# TERRAFORM EDUKACYJNY - Main Configuration
################################################################################
# Ten plik to "serce" infrastruktury. Definiuje:
# 1. Terraform settings (wersja, required providers)
# 2. AWS provider (jak łączyć się z AWS)
# 3. Resources (zasoby AWS: Lambda, IAM, EventBridge, ECR)
#
# Infrastructure as Code (IaC):
# - Kod opisuje infrastrukturę (zamiast klikać w konsoli AWS)
# - Wersjonowanie (git) = historia zmian infrastruktury
# - Powtarzalność (destroy + apply = identyczna infrastruktura)
################################################################################

terraform {
  # Minimalna wersja Terraform wymagana do uruchomienia
  required_version = ">= 1.0"

  # Providers = plugins do komunikacji z cloud providerami (AWS, Azure, GCP)
  required_providers {
    aws = {
      source  = "hashicorp/aws"  # Oficjalny provider AWS
      version = "~> 5.0"          # Wersja 5.x (kompatybilność wsteczna)
    }
  }

  # Backend = gdzie Terraform przechowuje "state" (stan infrastruktury)
  # OPCJONALNE: Zakomentowane dla początkujących (używa lokalnego pliku terraform.tfstate)
  # W produkcji: użyj S3 + DynamoDB dla współdzielenia state między teamem
  # backend "s3" {
  #   bucket         = "your-terraform-state-bucket"
  #   key            = "otomoto-scraper/terraform.tfstate"
  #   region         = "eu-central-1"
  #   dynamodb_table = "terraform-locks"
  #   encrypt        = true
  # }
}

################################################################################
# AWS PROVIDER - Konfiguracja połączenia z AWS
################################################################################
provider "aws" {
  region = var.aws_region  # Region AWS (eu-central-1 = Frankfurt)

  # Credentials: Terraform szuka w kolejności:
  # 1. Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
  # 2. Shared credentials file: ~/.aws/credentials (użyj: aws configure)
  # 3. IAM role (jeśli uruchamiasz z EC2/Lambda)
  
  # WAŻNE: NIGDY nie hardcode credentials w .tf files!
  # ❌ access_key = "AKIAXXXXX"  # ŹLE!
  # ✅ Użyj: aws configure --profile otomoto-proffile

  default_tags {
    tags = {
      Project     = "otomoto-scraper"
      ManagedBy   = "Terraform"
      Environment = var.environment
    }
  }
}

################################################################################
# ECR REPOSITORY - Elastic Container Registry (Docker registry AWS)
################################################################################
# ECR = miejsce na przechowywanie Docker images w AWS (jak Docker Hub)
resource "aws_ecr_repository" "scraper" {
  name                 = var.ecr_repository_name
  image_tag_mutability = "MUTABLE"  # Możesz nadpisywać tagi (np. "latest")

  # Skanowanie obrazów pod kątem vulnerabilities
  image_scanning_configuration {
    scan_on_push = true  # Automatyczne skanowanie przy każdym push
  }

  # Encryption at rest (szyfrowanie w spoczynku)
  encryption_configuration {
    encryption_type = "AES256"  # Darmowe szyfrowanie AWS
  }

  tags = {
    Name = "otomoto-scraper-ecr"
  }
}

# Lifecycle policy = automatyczne usuwanie starych images
resource "aws_ecr_lifecycle_policy" "scraper" {
  repository = aws_ecr_repository.scraper.name

  # Zachowaj tylko 5 ostatnich obrazów (oszczędność miejsca)
  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last 5 images"
      selection = {
        tagStatus     = "any"
        countType     = "imageCountMoreThan"
        countNumber   = 5
      }
      action = {
        type = "expire"
      }
    }]
  })
}

################################################################################
# IAM ROLE - Identity and Access Management (uprawnienia dla Lambda)
################################################################################
# Lambda potrzebuje "roli" (kto może co robić w AWS)
resource "aws_iam_role" "lambda_execution" {
  name = "${var.project_name}-lambda-role"

  # Trust policy = kto może "assume" tę rolę
  # Tutaj: tylko serwis Lambda może użyć tej roli
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })

  tags = {
    Name = "otomoto-scraper-lambda-role"
  }
}

# Załącz managed policy dla podstawowych logów CloudWatch
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Custom policy dla dostępu do S3 (upload wyników)
resource "aws_iam_role_policy" "lambda_s3" {
  name = "${var.project_name}-lambda-s3-policy"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:GetObject"
      ]
      Resource = "arn:aws:s3:::${var.s3_bucket_name}/*"
    }]
  })
}

################################################################################
# LAMBDA FUNCTION - Serverless compute (uruchamia scraper)
################################################################################
# Lambda = funkcja uruchamiana "na żądanie" (nie musisz płacić za serwer 24/7)
resource "aws_lambda_function" "scraper" {
  function_name = var.lambda_function_name
  role          = aws_iam_role.lambda_execution.arn

  # Package type = IMAGE (używamy Docker z ECR)
  # Alternatywa: ZIP (kod Python spakowany w .zip)
  package_type = "Image"
  image_uri    = "${aws_ecr_repository.scraper.repository_url}:latest"

  # Timeout = max czas wykonania (15 min = max dla Lambda)
  timeout = 900  # 15 minut (900 sekund)

  # Memory = RAM alokowana dla funkcji (128 MB - 10 GB)
  # WAŻNE: Więcej RAM = więcej CPU + drożej
  memory_size = 512  # 512 MB (wystarczające dla scrapera)

  # Ephemeral storage = /tmp space (512 MB - 10 GB)
  ephemeral_storage {
    size = 512  # 512 MB (Free Tier)
  }

  # Environment variables = konfiguracja dla aplikacji
  environment {
    variables = {
      OTOMOTO_URL           = var.otomoto_url
      S3_BUCKET             = var.s3_bucket_name
      AWS_REGION            = var.aws_region
      PYTHONUNBUFFERED      = "1"
    }
  }

  tags = {
    Name = "otomoto-scraper-lambda"
  }

  # Dependency = czekaj aż ECR lifecycle policy będzie gotowa
  depends_on = [
    aws_ecr_lifecycle_policy.scraper,
    aws_iam_role_policy_attachment.lambda_basic,
    aws_iam_role_policy.lambda_s3
  ]
}

# CloudWatch Log Group = logi z wykonania Lambda
resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${var.lambda_function_name}"
  retention_in_days = 7  # Przechowuj logi 7 dni (Free Tier: 5 GB)

  tags = {
    Name = "otomoto-scraper-lambda-logs"
  }
}

################################################################################
# EVENTBRIDGE RULE - Scheduled trigger (cron dla Lambda)
################################################################################
# EventBridge (dawniej CloudWatch Events) = scheduler dla AWS
# Możesz uruchamiać Lambda według harmonogramu (jak cron)
resource "aws_cloudwatch_event_rule" "scraper_schedule" {
  name                = "${var.project_name}-schedule"
  description         = "Trigger scraper Lambda on schedule"
  schedule_expression = var.schedule_expression  # np. "rate(6 hours)"

  # Możesz wyłączyć schedule nie usuwając zasobu
  is_enabled = var.schedule_enabled

  tags = {
    Name = "otomoto-scraper-schedule"
  }
}

# Target = co EventBridge ma uruchomić (naszą Lambda)
resource "aws_cloudwatch_event_target" "lambda" {
  rule      = aws_cloudwatch_event_rule.scraper_schedule.name
  target_id = "ScraperLambda"
  arn       = aws_lambda_function.scraper.arn
}

# Permission = pozwól EventBridge wywoływać Lambda
resource "aws_lambda_permission" "eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scraper.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.scraper_schedule.arn
}

################################################################################
# S3 BUCKET - Object storage (opcjonalne, jeśli nie masz bucketa)
################################################################################
# S3 = storage dla plików (jak Dropbox, ale dla aplikacji)
# Zakomentowane jeśli już masz bucket "otomoto-scraper-2025"
# resource "aws_s3_bucket" "scraper_output" {
#   bucket = var.s3_bucket_name
#
#   tags = {
#     Name = "otomoto-scraper-output"
#   }
# }
#
# resource "aws_s3_bucket_versioning" "scraper_output" {
#   bucket = aws_s3_bucket.scraper_output.id
#
#   versioning_configuration {
#     status = "Enabled"  # Wersjonowanie plików (historia zmian)
#   }
# }
#
# resource "aws_s3_bucket_lifecycle_configuration" "scraper_output" {
#   bucket = aws_s3_bucket.scraper_output.id
#
#   # Automatyczne usuwanie starych plików
#   rule {
#     id     = "delete-old-files"
#     status = "Enabled"
#
#     expiration {
#       days = 30  # Usuń pliki starsze niż 30 dni
#     }
#   }
# }
