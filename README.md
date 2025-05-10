# Qdrant Vector Database

Konfiguracja Qdrant z obsługą API key i HTTPS dla środowisk lokalnych i produkcyjnych.

## Opis

Repozytorium zawiera gotową konfigurację Qdrant - wydajnej bazy danych wektorowych, z następującymi funkcjonalnościami:

- Środowisko lokalne z bezpośrednim dostępem do Qdrant
- Środowisko produkcyjne z Caddy jako reverse proxy (HTTPS, Basic Auth)
- Uwierzytelnianie za pomocą klucza API
- Skrypty do zarządzania (start, stop, restart)
- Automatyczne uzyskiwanie certyfikatów SSL w środowisku produkcyjnym

## Wymagania

- Docker i Docker Compose
- Bash

## Szybki start

1. Skopiuj `.env.example` do `.env` i dostosuj zmienne:
   ```bash
   cp .env.example .env
   ```

2. Uruchom Qdrant lokalnie:
   ```bash
   ./start.sh
   ```

3. Dostęp do dashboardu:
   ```
   http://localhost:8081/dashboard
   ```
   
4. Użyj klucza API z pliku `.env` do uwierzytelniania zapytań.

## Struktura projektu

- `config/` - Pliki konfiguracyjne (Caddyfile)
- `scripts/` - Skrypty do zarządzania i konfiguracji
- `docs/` - Dokumentacja
- `docker-compose.local.yml` - Konfiguracja dla środowiska lokalnego
- `docker-compose.prod.yml` - Konfiguracja dla środowiska produkcyjnego

## Wdrożenie produkcyjne

Aby wdrożyć na produkcji:

1. Ustaw zmienną `DOMAIN` w pliku `.env`
2. Uruchom skrypt konfiguracji domeny:
   ```bash
   sudo ./scripts/setup-domain.sh
   ```

Szczegółowe instrukcje znajdują się w `docs/DEPLOYMENT.md`.

## Dokumentacja

- `docs/Troubleshooting.md` - Rozwiązywanie problemów
- `docs/Tutorial korzystania z API Qdrant.md` - Przykłady użycia API
