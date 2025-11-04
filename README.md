# 🚗 Otomoto Scraper

> Web scraper do automatycznego pobierania ogłoszeń samochodów z serwisu [Otomoto.pl](https://www.otomoto.pl/)

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-orange.svg)](https://aws.amazon.com/lambda/)
[![Terraform](https://img.shields.io/badge/Terraform-IaC-purple.svg)](https://www.terraform.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 Spis treści

- [Opis projektu](#-opis-projektu)
- [Funkcjonalności](#-funkcjonalności)
- [Architektura](#-architektura)
- [Wymagania](#-wymagania)
- [Instalacja](#-instalacja)
- [Użycie](#-użycie)
- [Deployment na AWS](#-deployment-na-aws)
- [Konfiguracja](#-konfiguracja)
- [Struktura projektu](#-struktura-projektu)
- [Rozwój](#-rozwój)
- [Licencja](#-licencja)

---

## 🎯 Opis projektu

**Otomoto Scraper** to narzędzie do automatycznego pobierania i przetwarzania danych o samochodach z największego polskiego serwisu ogłoszeniowego Otomoto.pl. W celu poznania technologii jak:
# 🚗 Otomoto Scraper

Prosty web scraper do pobierania ogłoszeń samochodów z serwisu Otomoto.pl. Projekt powstał do nauki i poznania technologii takich jak GitHub Actions, AWS (Lambda/ECR/S3) oraz Terraform. Obecnie scraper pobiera dane na podstawie przekazanego adresu URL i zapisuje wynik do pliku JSONL.

## Wymagania

- Python 3.11–3.13 i pip
- Git
- Opcjonalnie: Docker Desktop (dla uruchomienia w kontenerze)
- Opcjonalnie: AWS CLI i Terraform (dla uruchomienia w chmurze)

## Instalacja (lokalnie)

```powershell
# Windows PowerShell
git clone https://github.com/Av3r/otomoto_scraper.git
cd otomoto_scraper
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Konfiguracja

- Ustaw adres do scrapowania w zmiennej środowiskowej lub pliku .env:

```env
OTOMOTO_URL=https://www.otomoto.pl/osobowe/audi/a4
```

- Wyniki są zapisywane do pliku: `data/all_offers.jsonl`

## Jak uruchomić

1) Python (lokalnie):

```powershell
# Windows PowerShell (po aktywacji venv)
python -m src.scraper.main
```

2) Docker Compose (lokalnie):

```powershell
# .env powinien zawierać OTOMOTO_URL
docker-compose up -d
```

3) Docker (bez compose):

```powershell
docker build -t otomoto-scraper .
docker run --rm -e OTOMOTO_URL="https://www.otomoto.pl/osobowe/bmw/seria-5" -v ${PWD}/data:/app/data otomoto-scraper
```

4) Makefile (jeśli masz Make):

```powershell
make install
make run
```

## Opcjonalnie: uruchomienie w AWS

Projekt posiada przygotowany deployment serverless (AWS Lambda jako obraz Docker) oraz automatyczne wdrażanie przez GitHub Actions. Infrastrukturę można utworzyć Terraformem (folder `terraform/`).

Scraper:
- 💾 Zapisuje wyniki w formacie JSONL
- ☁️ Może działać lokalnie, w Docker lub jako AWS Lambda (serverless)
- 📦 Infrastructure as Code (Terraform)
- � Automatyczny deployment przez GitHub Actions
- 📊 Ekstrahuje kluczowe informacje (cena, przebieg, silnik, lokalizacja)
- ✅ Waliduje dane za pomocą Pydantic
- 🔍 Przeszukuje ogłoszenia według zadanych kryteriów (marka, model, rocznik, etc.)


## Możliwe rozszerzenia w przyszłości


Use cases:
- Analiza rynku samochodów
- Monitorowanie cen konkretnych modeli
- Zbieranie danych do ML/Data Science
- Alerting przy nowych ofertach