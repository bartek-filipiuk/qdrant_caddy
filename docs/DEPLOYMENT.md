# Qdrant - Instrukcja wdrożenia produkcyjnego

Ten dokument zawiera szczegółowe instrukcje dotyczące wdrożenia Qdrant w środowisku produkcyjnym z wykorzystaniem Caddy jako reverse proxy z obsługą HTTPS.

## Wymagania wstępne

- Serwer z systemem Linux
- Zainstalowany Docker i Docker Compose
- Domena internetowa wskazująca na adres IP serwera
- Otwarte porty 80 i 443 na serwerze (dla HTTP i HTTPS)

## 1. Przygotowanie środowiska

### 1.1. Konfiguracja pliku .env

Edytuj plik `.env` i ustaw następujące zmienne:

```bash
ENV=prod
DOMAIN=twoja-domena.pl
ADMIN_USER=admin
ADMIN_PASSWORD=silne_haslo
QDRANT_API_KEY=twoj_tajny_klucz_api
```

Pamiętaj, aby:
- Zastąpić `twoja-domena.pl` swoją rzeczywistą domeną
- Ustawić silne hasło dla użytkownika administratora
- Wygenerować bezpieczny klucz API dla Qdrant

### 1.2. Sprawdzenie konfiguracji DNS

Upewnij się, że Twoja domena wskazuje na adres IP serwera. Możesz to sprawdzić za pomocą polecenia:

```bash
host twoja-domena.pl
```

Wynik powinien zawierać adres IP Twojego serwera.

## 2. Wdrożenie

### 2.1. Uruchomienie skryptu konfiguracji domeny

Przejdź do katalogu ze skryptami i uruchom skrypt konfiguracji domeny:

```bash
cd /ścieżka/do/qdrant/scripts
sudo ./setup-domain.sh
```

Skrypt wykona następujące czynności:
- Sprawdzi, czy zmienna DOMAIN jest ustawiona
- Sprawdzi, czy skrypt jest uruchomiony z uprawnieniami roota
- Sprawdzi, czy porty 80 i 443 są dostępne
- Sprawdzi konfigurację DNS
- Wygeneruje hash hasła dla Caddy
- Zaktualizuje plik .env z wygenerowanym hashem
- Uruchomi środowisko produkcyjne

### 2.2. Weryfikacja wdrożenia

Po zakończeniu działania skryptu, Qdrant powinien być dostępny pod adresem:

```
https://twoja-domena.pl/dashboard
```

Caddy automatycznie uzyska certyfikat SSL z Let's Encrypt, co może zająć kilka minut.

## 3. Testowanie API

Aby sprawdzić, czy API Qdrant działa poprawnie, wykonaj następujące zapytanie:

```bash
curl -s -X GET -u admin:silne_haslo -H "api-key: twoj_tajny_klucz_api" https://twoja-domena.pl/collections
```

Powinieneś otrzymać odpowiedź JSON z listą kolekcji.

## 4. Rozwiązywanie problemów

### 4.1. Sprawdzanie logów

Jeśli napotkasz problemy, sprawdź logi kontenerów:

```bash
# Logi Caddy
docker logs qdrant-caddy-1

# Logi Qdrant
docker logs qdrant-qdrant-1
```

### 4.2. Problemy z certyfikatem SSL

Jeśli Caddy nie może uzyskać certyfikatu SSL, upewnij się, że:
- Domena poprawnie wskazuje na adres IP serwera
- Porty 80 i 443 są otwarte i dostępne
- Nie ma innych usług korzystających z tych portów

### 4.3. Problemy z uwierzytelnianiem

Jeśli masz problemy z logowaniem:
- Sprawdź, czy używasz poprawnego hasła i klucza API
- Upewnij się, że zmienne ADMIN_PASSWORD i QDRANT_API_KEY w pliku .env są poprawne
- Sprawdź, czy hash hasła został poprawnie wygenerowany

## 5. Kopie zapasowe

### 5.1. Tworzenie kopii zapasowej

Aby utworzyć kopię zapasową danych Qdrant, użyj skryptu:

```bash
cd /ścieżka/do/qdrant/scripts
./backup.sh
```

Kopia zapasowa zostanie zapisana w katalogu `backups`.

### 5.2. Przywracanie z kopii zapasowej

Aby przywrócić dane z kopii zapasowej, użyj skryptu:

```bash
cd /ścieżka/do/qdrant/scripts
./restore.sh nazwa_pliku_kopii
```

## 6. Aktualizacja

Aby zaktualizować Qdrant do najnowszej wersji:

1. Zatrzymaj kontenery:
   ```bash
   cd /ścieżka/do/qdrant
   ./stop.sh
   ```

2. Edytuj plik `docker-compose.prod.yml` i zmień wersję obrazu Qdrant (opcjonalnie)

3. Uruchom ponownie środowisko:
   ```bash
   ENV=prod ./restart.sh
   ```

## 7. Bezpieczeństwo

- Regularnie zmieniaj hasło administratora i klucz API
- Monitoruj logi pod kątem nieautoryzowanych prób dostępu
- Rozważ dodatkowe zabezpieczenia na poziomie sieci (firewall, VPN)
- Wykonuj regularne kopie zapasowe danych

## 8. Zasoby dodatkowe

- [Dokumentacja Qdrant](https://qdrant.tech/documentation/)
- [Dokumentacja Caddy](https://caddyserver.com/docs/)
- [Let's Encrypt](https://letsencrypt.org/docs/)
