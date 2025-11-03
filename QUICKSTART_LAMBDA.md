# 🚀 Quick Start - AWS Lambda Deployment

> **TL;DR:** Deploy scraper na AWS Lambda w 5 minut

## Wymagania

- ✅ AWS Account (Free Tier)
- ✅ AWS CLI skonfigurowane (`aws configure --profile otomoto-proffile`)
- ✅ Docker Desktop (działający)
- ✅ Terraform zainstalowany (`terraform version`)

## 5-minutowy deployment

### 1. Ustaw AWS profile

**PowerShell:**
```powershell
$env:AWS_PROFILE = "otomoto-proffile"
```

**Bash:**
```bash
export AWS_PROFILE=otomoto-proffile
```

### 2. Deploy infrastruktury (Terraform)

```bash
cd terraform

# Inicjalizacja
terraform init

# Podgląd zmian
terraform plan

# Deploy (tylko ECR na początku)
terraform apply -target=aws_ecr_repository.scraper
# Wpisz: yes

# Zapisz ECR URL
terraform output -raw ecr_repository_url
# Kopiuj URL (np: 123456789012.dkr.ecr.eu-central-1.amazonaws.com/otomoto-scraper)
```

### 3. Build i push Docker image

```bash
cd ..  # Wróć do głównego katalogu

# Pobierz ECR URL z Terraform
$ECR_URL = (cd terraform; terraform output -raw ecr_repository_url)

# Login do ECR
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin $ECR_URL

# Build
docker build -f Dockerfile.lambda -t otomoto-scraper:lambda .

# Tag
docker tag otomoto-scraper:lambda ${ECR_URL}:latest

# Push
docker push ${ECR_URL}:latest
```

### 4. Deploy reszty infrastruktury

```bash
cd terraform

# Deploy wszystkiego (Lambda, EventBridge, IAM, logs)
terraform apply
# Wpisz: yes

# Zobacz co zostało utworzone
terraform output
```

### 5. Test!

```bash
# Ręczne uruchomienie Lambda
aws lambda invoke \
  --function-name otomoto-scraper \
  --region eu-central-1 \
  response.json

# Zobacz response
cat response.json

# Zobacz logi
aws logs tail /aws/lambda/otomoto-scraper --follow
```

---

## GitHub Actions Auto-Deploy

### 1. Dodaj GitHub Secrets

Idź do: `https://github.com/<your-username>/otomoto_scraper/settings/secrets/actions`

Dodaj sekrety:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION` = `eu-central-1`
- `S3_BUCKET` = `otomoto-scraper-2025`

### 2. Deploy przez GitHub Actions

Każda zmiana w `src/` lub `Dockerfile.lambda` automatycznie:
1. Builduje nowy Docker image
2. Push do ECR
3. Update Lambda function

**Lub ręcznie:**
- Idź do: Actions → Deploy Lambda → Run workflow

---

## Włączenie automatycznego uruchamiania (scheduler)

### Edytuj `terraform/terraform.tfvars`:

```hcl
schedule_enabled = true
schedule_expression = "rate(6 hours)"  # Co 6 godzin
```

### Zastosuj:

```bash
cd terraform
terraform apply
```

### Opcje harmonogramu:

| Expression | Opis |
|------------|------|
| `rate(6 hours)` | Co 6 godzin |
| `rate(12 hours)` | Co 12 godzin |
| `rate(1 day)` | Raz dziennie |
| `cron(0 2 * * ? *)` | Codziennie o 2:00 UTC |
| `cron(0 */4 * * ? *)` | Co 4 godziny |

---

## Sprawdzanie rezultatów

### CloudWatch Logs (logi Lambda)

```bash
# Tail logs na żywo
aws logs tail /aws/lambda/otomoto-scraper --follow

# Ostatnie 50 linii
aws logs tail /aws/lambda/otomoto-scraper --since 1h
```

**Lub w konsoli AWS:**
```
https://eu-central-1.console.aws.amazon.com/cloudwatch/home?region=eu-central-1#logsV2:log-groups/log-group/$252Faws$252Flambda$252Fotomoto-scraper
```

### S3 Bucket (wyniki scrapera)

```bash
# Lista plików
aws s3 ls s3://otomoto-scraper-2025/

# Pobierz najnowszy
aws s3 cp s3://otomoto-scraper-2025/all_offers-latest.jsonl .

# Zobacz zawartość
cat all_offers-latest.jsonl | head -5
```

---

## Koszty (Free Tier)

| Usługa | Free Tier | Szacunkowe użycie | Koszt |
|--------|-----------|-------------------|-------|
| Lambda | 1M requests, 400k GB-seconds | 100x/miesiąc, 512MB, 5min | **$0** |
| CloudWatch Logs | 5 GB | <100 MB | **$0** |
| ECR | 500 MB | ~200 MB | **$0** |
| S3 | 5 GB, 20k GET, 2k PUT | <100 MB, <1000 requests | **$0** |
| EventBridge | Unlimited | Unlimited | **$0** |
| **TOTAL** | | | **$0** ✅ |

---

## Czyszczenie (destroy)

### Zniszcz całą infrastrukturę:

```bash
cd terraform
terraform destroy
# Wpisz: yes
```

**Uwaga:** To NIE usunie:
- S3 bucket (jeśli był utworzony ręcznie)
- CloudWatch Logs (retention policy = 7 dni, usunie się automatycznie)

---

## Troubleshooting

### Lambda timeout po 15 minutach

**Rozwiązanie:** Ogranicz liczbę stron w scraper:

```python
# src/scraper/main.py
offers = scrape_pages(base_url, max_pages=5)  # Zamiast 10
```

### Image not found w Lambda

**Rozwiązanie:** Push image do ECR ponownie:

```bash
docker push <ECR_URL>:latest
```

### Lambda nie ma dostępu do S3

**Sprawdź IAM policy:**

```bash
aws iam get-role-policy \
  --role-name otomoto-scraper-lambda-role \
  --policy-name otomoto-scraper-lambda-s3-policy
```

---

## Dalsze kroki

- [ ] Zobacz `terraform/README.md` dla szczegółowej edukacji Terraform
- [ ] Konfiguruj harmonogram w `terraform.tfvars`
- [ ] Monitoruj koszty w AWS Cost Explorer
- [ ] Dodaj SNS alerts (email on failure)

**Miłego scrapowania! 🚀**
