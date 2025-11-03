# 🚀 Terraform + AWS Lambda Deployment Guide

> **Edukacyjny przewodnik po Infrastructure as Code z Terraform**

## 📚 Czym jest Terraform?

**Terraform** to narzędzie do zarządzania infrastrukturą jako kodem (Infrastructure as Code - IaC).

### Główne koncepcje:

1. **Declarative** (deklaratywny):
   - Opisujesz "JAK MA BYĆ" infrastruktura
   - Terraform sam wymyśla "JAK TO OSIĄGNĄĆ"
   - Przykład: `aws_lambda_function` → Terraform stworzy Lambda

2. **State** (stan):
   - Plik `terraform.tfstate` = aktualny stan infrastruktury
   - Terraform porównuje: co JEST vs co MA BYĆ
   - Zmienia tylko różnice (idempotentność)

3. **Resources** (zasoby):
   - `resource "aws_lambda_function" "scraper" { }` = jedna rzecz w AWS
   - Każdy resource ma typ + nazwę lokalną + konfigurację

4. **Variables** (zmienne):
   - Input = parametry wejściowe (`variables.tf`)
   - Output = wartości zwracane (`outputs.tf`)

5. **Providers** (dostawcy):
   - Plugin do komunikacji z cloud (AWS, Azure, GCP)
   - `terraform init` pobiera providers

---

## 🏗️ Architektura rozwiązania

```
┌─────────────────────────────────────────────────────────────┐
│                      GITHUB ACTIONS                          │
│  1. Build Docker image (Dockerfile.lambda)                   │
│  2. Push to AWS ECR (Elastic Container Registry)             │
│  3. Deploy via Terraform (opcjonalnie)                       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    AWS ECR REPOSITORY                        │
│  - Docker images storage (jak Docker Hub, ale AWS)          │
│  - Auto-scan for vulnerabilities                             │
│  - Lifecycle policy (keep last 5 images)                     │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                     AWS LAMBDA FUNCTION                      │
│  - Runs Docker container with scraper                        │
│  - Timeout: 15 minutes (max)                                 │
│  - Memory: 512 MB (configurable)                             │
│  - Triggered by: EventBridge / Manual / GitHub Actions       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                      EVENTBRIDGE RULE                        │
│  - Scheduler (cron/rate expression)                          │
│  - Example: "rate(12 hours)" = every 12 hours                │
│  - Can be enabled/disabled without deletion                  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                     S3 BUCKET                                │
│  - Storage for scraped data (all_offers.jsonl)               │
│  - Versioning enabled                                        │
│  - Lifecycle policy (delete after 30 days)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Wymagania wstępne

### 1. Zainstaluj Terraform

**Windows (Chocolatey):**
```powershell
choco install terraform
```

**Windows (Scoop):**
```powershell
scoop install terraform
```

**Linux/macOS:**
```bash
# https://developer.hashicorp.com/terraform/downloads
wget https://releases.hashicorp.com/terraform/1.6.5/terraform_1.6.5_linux_amd64.zip
unzip terraform_1.6.5_linux_amd64.zip
sudo mv terraform /usr/local/bin/
```

**Sprawdź instalację:**
```bash
terraform version
```

### 2. Skonfiguruj AWS CLI

```powershell
# Jeśli jeszcze nie masz AWS CLI:
pip install awscli

# Konfiguracja credentials:
aws configure --profile otomoto-proffile
# AWS Access Key ID: AKIATQBJF2TISO4BVCJP
# AWS Secret Access Key: (twój secret)
# Default region: eu-central-1
# Default output format: json
```

### 3. Ustaw AWS profile dla Terraform

**Windows PowerShell:**
```powershell
$env:AWS_PROFILE = "otomoto-proffile"
```

**Linux/macOS:**
```bash
export AWS_PROFILE=otomoto-proffile
```

---

## 🚀 Deployment krok po kroku

### Krok 1: Build i push Docker image do ECR

Najpierw musimy stworzyć ECR repository ręcznie (lub przez Terraform):

```powershell
# Przejdź do katalogu terraform
cd terraform

# Inicjalizacja Terraform (pobierz providers)
terraform init

# Podgląd zmian (co Terraform zamierza zrobić)
terraform plan

# Zastosuj zmiany (stwórz ECR repository)
# UWAGA: To utworzy tylko ECR, Lambda jeszcze nie zadziała (brak image)
terraform apply -target=aws_ecr_repository.scraper
# Wpisz: yes
```

Po utworzeniu ECR, pobierz URL:

```powershell
$ECR_URL = terraform output -raw ecr_repository_url
echo $ECR_URL
# Output: 123456789012.dkr.ecr.eu-central-1.amazonaws.com/otomoto-scraper
```

### Krok 2: Login do ECR i push image

```powershell
# Przejdź do głównego katalogu projektu
cd ..

# Login do ECR
aws ecr get-login-password --region eu-central-1 --profile otomoto-proffile | docker login --username AWS --password-stdin $ECR_URL

# Build Docker image dla Lambda
docker build -f Dockerfile.lambda -t otomoto-scraper:lambda .

# Tag image dla ECR
docker tag otomoto-scraper:lambda ${ECR_URL}:latest

# Push do ECR
docker push ${ECR_URL}:latest
```

### Krok 3: Deploy całej infrastruktury

```powershell
# Wróć do katalogu terraform
cd terraform

# Deploy wszystkiego (Lambda, EventBridge, IAM roles, logs)
terraform apply
# Przeczytaj plan, wpisz: yes
```

**Co się stało?**
- ✅ ECR repository (Docker registry)
- ✅ Lambda function (używa image z ECR)
- ✅ IAM role z uprawnieniami (CloudWatch Logs, S3)
- ✅ CloudWatch Log Group (logi z Lambda)
- ✅ EventBridge rule (scheduler - domyślnie wyłączony)
- ✅ Lambda permission (pozwól EventBridge wywoływać Lambda)

### Krok 4: Test ręcznego uruchomienia

```powershell
# Wyświetl wszystkie outputy
terraform output

# Uruchom Lambda ręcznie
aws lambda invoke `
  --function-name otomoto-scraper `
  --region eu-central-1 `
  --profile otomoto-proffile `
  response.json

# Sprawdź response
cat response.json

# Zobacz logi w CloudWatch
$LOG_GROUP = terraform output -raw cloudwatch_log_group
aws logs tail $LOG_GROUP --follow --profile otomoto-proffile
```

### Krok 5: Włącz automatyczne uruchamianie (opcjonalnie)

Edytuj `terraform.tfvars`:

```hcl
schedule_enabled = true           # Włącz scheduler
schedule_expression = "rate(6 hours)"  # Co 6 godzin
```

Zastosuj zmiany:

```powershell
terraform apply
# Wpisz: yes
```

Sprawdź status:

```powershell
terraform output eventbridge_enabled
# Output: true
```

---

## 🔧 Terraform - Najważniejsze komendy

### Podstawowe operacje

```bash
# 1. Inicjalizacja (pobierz providers)
terraform init

# 2. Walidacja składni
terraform validate

# 3. Formatowanie kodu (prettier dla Terraform)
terraform fmt

# 4. Podgląd zmian (dry-run)
terraform plan

# 5. Zastosuj zmiany
terraform apply

# 6. Zastosuj bez pytania o potwierdzenie
terraform apply -auto-approve

# 7. Zniszcz całą infrastrukturę
terraform destroy
```

### Praca ze zmiennymi

```bash
# Nadpisz zmienną przez CLI
terraform apply -var="schedule_enabled=true"

# Użyj innego pliku tfvars
terraform apply -var-file="production.tfvars"

# Environment variable
export TF_VAR_aws_region="us-east-1"
terraform apply
```

### State management

```bash
# Wyświetl aktualny state
terraform show

# Lista zasobów w state
terraform state list

# Szczegóły konkretnego zasobu
terraform state show aws_lambda_function.scraper

# Usuń zasób ze state (NIE usuwa z AWS!)
terraform state rm aws_lambda_function.scraper

# Import istniejącego zasobu AWS do state
terraform import aws_lambda_function.scraper otomoto-scraper
```

### Outputs

```bash
# Wyświetl wszystkie outputs
terraform output

# Konkretny output
terraform output lambda_function_arn

# Output jako raw string (bez cudzysłowów)
terraform output -raw ecr_repository_url

# Export jako JSON
terraform output -json > outputs.json
```

### Targeted apply (tylko konkretne zasoby)

```bash
# Stwórz tylko ECR
terraform apply -target=aws_ecr_repository.scraper

# Zniszcz tylko EventBridge rule
terraform destroy -target=aws_cloudwatch_event_rule.scraper_schedule

# Odśwież tylko Lambda
terraform apply -target=aws_lambda_function.scraper
```

---

## 🎓 Terraform Concepts - Edukacja

### 1. Resource Dependencies

Terraform automatycznie wykrywa zależności:

```hcl
resource "aws_iam_role" "lambda" {
  # ...
}

resource "aws_lambda_function" "scraper" {
  role = aws_iam_role.lambda.arn  # ← Terraform wie: stwórz role NAJPIERW
}
```

Ręczne zależności:

```hcl
resource "aws_lambda_function" "scraper" {
  # ...
  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic
  ]
}
```

### 2. Data Sources (odczyt istniejących zasobów)

```hcl
# Użyj ISTNIEJĄCEGO S3 bucket (nie twórz nowego)
data "aws_s3_bucket" "existing" {
  bucket = "otomoto-scraper-2025"
}

# Referencja: data.aws_s3_bucket.existing.arn
```

### 3. Locals (zmienne obliczane)

```hcl
locals {
  common_tags = {
    Project   = "otomoto-scraper"
    ManagedBy = "Terraform"
  }
  
  lambda_name = "${var.project_name}-${var.environment}"
}

resource "aws_lambda_function" "scraper" {
  function_name = local.lambda_name
  tags          = local.common_tags
}
```

### 4. Count i for_each (pętle)

```hcl
# Stwórz 3 Lambda (dev, staging, prod)
variable "environments" {
  default = ["dev", "staging", "prod"]
}

resource "aws_lambda_function" "scraper" {
  count = length(var.environments)
  
  function_name = "scraper-${var.environments[count.index]}"
  # ...
}
```

### 5. Modules (reusable components)

```hcl
# terraform/modules/lambda/main.tf
resource "aws_lambda_function" "this" {
  # ...
}

# terraform/main.tf
module "lambda_dev" {
  source = "./modules/lambda"
  
  function_name = "scraper-dev"
  memory_size   = 512
}

module "lambda_prod" {
  source = "./modules/lambda"
  
  function_name = "scraper-prod"
  memory_size   = 1024
}
```

### 6. Remote State (współdzielenie state)

```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "otomoto-scraper/terraform.tfstate"
    region         = "eu-central-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

**Dlaczego remote state?**
- 🤝 Współpraca w teamie (shared state)
- 🔒 State locking (DynamoDB) = nie nadpisuj się nawzajem
- 💾 Backup (S3 versioning)

### 7. Workspaces (multiple environments)

```bash
# Stwórz workspace dla dev
terraform workspace new dev

# Przełącz się na prod
terraform workspace select prod

# Lista workspaces
terraform workspace list

# W kodzie:
resource "aws_lambda_function" "scraper" {
  function_name = "scraper-${terraform.workspace}"
}
```

---

## 🐛 Troubleshooting

### Problem: "Error acquiring the state lock"

**Przyczyna:** Ktoś inny (lub wcześniejsze terraform apply) trzyma lock.

**Rozwiązanie:**
```bash
# TYLKO jeśli jesteś pewien że nikt nie używa:
terraform force-unlock <LOCK_ID>
```

### Problem: "Error: Provider configuration not present"

**Przyczyna:** Nie uruchomiłeś `terraform init`.

**Rozwiązanie:**
```bash
terraform init
```

### Problem: Lambda timeout po 15 minutach

**Przyczyna:** Lambda ma max timeout 15 min.

**Rozwiązanie:**
- Opcja A: Optymalizuj scraper (przetwarzaj mniej stron)
- Opcja B: Użyj ECS Fargate (bez limitu czasu)
- Opcja C: Podziel na mniejsze kawałki (Lambda wywołuje kolejną Lambda)

### Problem: "ImageNotFoundException" przy deploy Lambda

**Przyczyna:** Image nie istnieje w ECR (nie zrobiłeś `docker push`).

**Rozwiązanie:**
```bash
# Push image do ECR (patrz: Krok 2)
aws ecr get-login-password | docker login ...
docker push <ECR_URL>:latest
```

### Problem: Lambda nie ma dostępu do S3

**Przyczyna:** IAM role nie ma uprawnień.

**Sprawdź:**
```bash
# Zobacz IAM policy Lambda
aws iam get-role-policy \
  --role-name otomoto-scraper-lambda-role \
  --policy-name otomoto-scraper-lambda-s3-policy
```

### Problem: Chcę zmienić tylko schedule bez przebudowy Lambda

**Rozwiązanie:**
```bash
# Edytuj terraform.tfvars
schedule_expression = "rate(4 hours)"

# Apply tylko EventBridge
terraform apply -target=aws_cloudwatch_event_rule.scraper_schedule
```

---

## 💰 Koszty AWS Free Tier

### Lambda
- ✅ **1M invocations/miesiąc** - FREE
- ✅ **400,000 GB-seconds compute** - FREE
- ⚠️ Po przekroczeniu: $0.20 per 1M requests + $0.0000166667 per GB-second

**Przykład:** 512 MB RAM, 5 minut (300s), 100x/miesiąc
- Compute: (512/1024) * 300 * 100 = 15,000 GB-s ✅ FREE
- Requests: 100 ✅ FREE

### CloudWatch Logs
- ✅ **5 GB ingestion** - FREE
- ✅ **5 GB storage** - FREE
- Retention: 7 dni (ustawione w Terraform)

### ECR (Docker Registry)
- ✅ **500 MB storage** - FREE przez 12 miesięcy
- Lifecycle policy: keep last 5 images (oszczędność miejsca)

### EventBridge
- ✅ **Wszystkie invocations** - FREE (nie płacisz za scheduler)

### S3
- ✅ **5 GB storage** - FREE przez 12 miesięcy
- ✅ **20,000 GET + 2,000 PUT** - FREE
- Lifecycle: delete after 30 days (oszczędność)

**Szacunkowy koszt miesięczny:** $0 (w ramach Free Tier) 🎉

---

## 📖 Dalsze kroki edukacyjne

### 1. Terraform Advanced
- [ ] Refactor do modułów (modules/)
- [ ] Remote state (S3 + DynamoDB)
- [ ] Workspaces (dev/staging/prod)
- [ ] Terraform Cloud (collaboration)

### 2. AWS Advanced
- [ ] Lambda Layers (shared dependencies)
- [ ] API Gateway (HTTP endpoint dla Lambda)
- [ ] Step Functions (orchestration)
- [ ] CloudFormation comparison

### 3. CI/CD Integration
- [ ] GitHub Actions deploy via Terraform
- [ ] Automated drift detection
- [ ] PR preview environments
- [ ] Terraform plan w Pull Requests

### 4. Monitoring & Observability
- [ ] CloudWatch Dashboards
- [ ] SNS alerts (email on failure)
- [ ] X-Ray tracing
- [ ] Cost anomaly detection

---

## 🔗 Przydatne linki

- [Terraform Documentation](https://developer.hashicorp.com/terraform/docs)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Lambda Docs](https://docs.aws.amazon.com/lambda/)
- [EventBridge Schedule Expressions](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-create-rule-schedule.html)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)

---

## 📝 Notatki

### Terraform State (terraform.tfstate)
- ⚠️ **NIE commituj do git!** (zawiera sensitive data)
- 📁 Dodaj do `.gitignore`: `*.tfstate*`
- 🔒 W produkcji: użyj S3 backend + encryption

### Secrets Management
- ❌ NIE hardcode credentials w `.tf` files
- ✅ Użyj AWS Secrets Manager / Parameter Store
- ✅ Lub environment variables: `TF_VAR_*`

### Terraform Plan przed Apply
- ✅ ZAWSZE uruchom `terraform plan` przed `apply`
- 🔍 Przeczytaj co Terraform zamierza zmienić
- ⚠️ Czerwony `-` = usunięcie, zielony `+` = dodanie

---

**Autor:** GitHub Copilot + Terraform Community  
**Ostatnia aktualizacja:** 2025-11-03  
**Terraform version:** >= 1.0  
**AWS Provider version:** ~> 5.0
