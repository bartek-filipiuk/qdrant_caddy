# Projekt: Bezpieczny interfejs Qdrant Web UI za pomocą Caddy + Docker

## 🎯 Cel projektu
Zbudowanie lekkiego i bezpiecznego środowiska do pracy z wektorową bazą danych Qdrant, dostępnego przez przeglądarkę (Web UI) oraz przez REST API, z uruchomieniem wszystkiego lokalnie lub na serwerze (np. VPS) poprzez Dockera. Dostęp ma być zabezpieczony przez Basic Auth i API Key.

## 🧱 Architektura systemu
```lua
+-------------+        +------------+        +-------------+
|  Użytkownik | <--->  |  Caddy     | <----> |  Qdrant     |
| (przeglądarka/API)   | (reverse proxy)     | (baza wektorów + UI)
+-------------+        +------------+        +-------------+
```
- **Qdrant:** baza danych wektorowych, Web UI i REST API.
- **Caddy:** reverse proxy, który:
    - Zabezpiecza dostęp do Qdrant (Basic Auth),
    - Wymaga API Key w nagłówku `X-API-KEY`,
    - Obsługuje HTTPS automatycznie (na serwerze z domeną),
- **Docker:** całość działa jako dwa kontenery.

## ⚙️ Wymagania techniczne
- Docker + Docker Compose
- Działa zarówno lokalnie (`http://localhost:8080`) jak i na domenie (`https://twojadomena.pl`) z certyfikatem SSL
- Zgodne z najnowszymi wersjami:
    - Qdrant: `qdrant/qdrant:latest`
    - Caddy: `caddy:alpine` (minimalna i aktualna)

## 🔐 Zabezpieczenia

### Basic Auth
- Użytkownik podaje login i hasło przy dostępie do Web UI i REST API.
- Hasło zapisane jako bcrypt hash.

### API Key
- Wymagany nagłówek `X-API-KEY: tajny_klucz`
- Brak tego nagłówka → zwracane 403 Forbidden

## 📁 Caddyfile (przykład)
```caddyfile
:8080 {
  basicauth {
    admin JDJhJDEyJHRiR3B1cG9qZ1lFZGxyMG0uVlp2dXdzQ1JzL1dZUVZDMU9KMjZ5SkZCQjEyd3g1MXNZ
  }

  @invalid_api_key not header X-API-KEY tajny_klucz_123
  respond @invalid_api_key 403

  reverse_proxy qdrant:6333
}
```

## 🔒 Hash hasła (`haslo123`) generujemy komendą:
```bash
caddy hash-password --plaintext haslo123
```

## 📦 docker-compose.yml (przykład)
```yaml
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:latest
    expose:
      - "6333"
    volumes:
      - qdrant_storage:/qdrant/storage

  caddy:
    image: caddy:alpine
    ports:
      - "8080:8080"    # lokalne testowanie
      - "80:80"        # opcjonalnie dla certyfikatu na serwerze
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
    depends_on:
      - qdrant

volumes:
  qdrant_storage:
```

## 🔧 Testowanie lokalne
Uruchom:
```bash
docker-compose up -d
```
- Wejdź na `http://localhost:8080/dashboard`
- **Login:** `admin`
- **Hasło:** `haslo123`
- Dodaj header: `X-API-KEY: tajny_klucz_123` w zapytaniach API

## 🌐 Działanie na własnej domenie (VPS + DNS)
- Skieruj domenę (np. `vector.example.com`) na IP serwera (rekord A).
- Zmień `Caddyfile`:
  ```caddyfile
  vector.example.com {
    # reszta jak wyżej
  }
  ```
- Upewnij się, że porty 80 i 443 są otwarte.
- Caddy automatycznie pobierze certyfikat SSL.

## 🧾 Handoff: Plan działania dla innego agenta AI
🔹 **1. Przygotowanie projektu**
 - Stwórz katalog projektu
 - Wygeneruj hash hasła przez `caddy hash-password`
 - Zapisz go w `Caddyfile` jako bcrypt dla `admin`

🔹 **2. Pliki projektu**
 - `docker-compose.yml` z Qdrant i Caddy
 - `Caddyfile` z Basic Auth i walidacją API Key

🔹 **3. Uruchomienie i testy**
 - Uruchom `docker-compose up -d`
 - Sprawdź dostępność Web UI przez przeglądarkę
 - Sprawdź REST API z `curl`/Postman z poprawnym API Key

🔹 **4. Deployment na serwerze (jeśli wymagane)**
 - Skonfiguruj domenę (rekord A)
 - Podmień domenę w `Caddyfile`
 - Sprawdź HTTPS i poprawność certyfikatu
```