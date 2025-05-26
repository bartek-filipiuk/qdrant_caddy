# Tutorial: Korzystanie z API Qdrant za pomocą curl

## Wprowadzenie

Qdrant to otwartoźródłowa baza danych wektorowych i silnik wyszukiwania wektorowego napisany w języku Rust. Jest przeznaczony do wysokowydajnych aplikacji AI na dużą skalę, szczególnie do wyszukiwania podobieństwa wektorów. Qdrant można zainstalować lokalnie lub na serwerze, a jego API umożliwia przechowywanie, wyszukiwanie i zarządzanie wektorami z dodatkowymi danymi (payload). Od wersji 1.7 Qdrant oferuje również interfejs webowy do łatwiejszej interakcji. Ten tutorial przeprowadzi Cię przez proces konfiguracji Qdrant, autoryzacji w API, korzystania z kluczowych endpointów oraz używania interfejsu webowego.

## Krok 1: Konfiguracja i uruchomienie Qdrant w projekcie

W tym projekcie Qdrant jest zarządzany za pomocą Docker Compose wraz z serwerem Caddy, który pełni rolę reverse proxy i zapewnia HTTPS w środowisku produkcyjnym. Konfiguracja odbywa się poprzez plik `.env`.

1.  **Przygotowanie pliku konfiguracyjnego**:
    *   Skopiuj plik `.env.example` do nowego pliku o nazwie `.env` w głównym katalogu projektu:
        ```bash
        cp .env.example .env
        ```
    *   Otwórz plik `.env` i dostosuj zmienne środowiskowe do swoich potrzeb. Kluczowe zmienne to:
        *   `ENV`: Ustaw na `local` dla środowiska lokalnego lub `prod` dla produkcyjnego. Domyślnie jest `local`.
        *   `DOMAIN`: Twoja domena (używana w trybie `prod`), np. `qdrant.twojadomena.com`. Pamiętaj, aby skonfigurować odpowiednie rekordy DNS dla tej domeny, aby wskazywały na adres IP serwera, na którym uruchamiasz projekt.
        *   `ADMIN_USER`: Nazwa użytkownika do panelu administracyjnego Caddy.
        *   `ADMIN_PASSWORD`: Hasło dla `ADMIN_USER`. Skrypt `scripts/setup-domain.sh` może pomóc w wygenerowaniu hasha hasła (`ADMIN_PASSWORD_HASH`) dla Caddy, jeśli jest to wymagane.
        *   `QDRANT_API_KEY`: Klucz API do zabezpieczenia dostępu do Qdrant. Upewnij się, że jest to silny, unikalny klucz.
        *   `LOCAL_PORT`: Port, na którym Qdrant będzie dostępny lokalnie przez Caddy (używany w trybie `local`), np. `8081`.
        *   `ADMIN_EMAIL`: Adres email używany przez Caddy do uzyskiwania certyfikatów SSL/TLS od Let's Encrypt (w trybie `prod`).

2.  **Uruchomienie usług**:
    *   Upewnij się, że masz zainstalowany Docker i Docker Compose.
    *   W głównym katalogu projektu uruchom skrypt `start.sh`:
        ```bash
        ./start.sh
        ```
    *   Ten skrypt automatycznie odczyta konfigurację z pliku `.env` i uruchomi odpowiednie kontenery (`qdrant` i `caddy`) za pomocą `docker-compose`. W trybie `prod`, Caddy automatycznie spróbuje uzyskać certyfikat SSL dla Twojej domeny.

3.  **Dostęp do interfejsu webowego Qdrant**:
    *   Po pomyślnym uruchomieniu, interfejs webowy Qdrant będzie dostępny pod adresem:
        *   **Dla środowiska lokalnego (`ENV=local`)**: `http://localhost:LOCAL_PORT/dashboard` (gdzie `LOCAL_PORT` to wartość z pliku `.env`, np. `http://localhost:8081/dashboard`). Dostęp do API Qdrant będzie na `http://localhost:LOCAL_PORT/`.
        *   **Dla środowiska produkcyjnego (`ENV=prod`)**: `https://DOMAIN/dashboard` (gdzie `DOMAIN` to wartość z pliku `.env`, np. `https://qdrant.twojadomena.com/dashboard`). Dostęp do API Qdrant będzie na `https://DOMAIN/`.
    *   Interfejs webowy umożliwia zarządzanie kolekcjami, przeglądanie punktów i wykonywanie wyszukiwań w sposób interaktywny. Dostęp do API Qdrant (np. przez `curl` lub klientów programistycznych) będzie wymagał użycia `QDRANT_API_KEY` zdefiniowanego w pliku `.env` jako nagłówka `api-key`.

## Krok 2: Autoryzacja

Qdrant obsługuje autoryzację opartą na kluczach API, aby zabezpieczyć instancję. Domyślnie autoryzacja jest wyłączona, ale w środowisku produkcyjnym zaleca się jej włączenie.

- **Włączenie autoryzacji kluczem API**:
  - Klucz API można ustawić za pomocą pliku konfiguracyjnego lub zmiennych środowiskowych.
  - Przykład z użyciem zmiennej środowiskowej:
    ```bash
    docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage:z -e QDRANT__SERVICE__API_KEY=twój_tajny_klucz_api qdrant/qdrant
    ```
    - Zastąp `twój_tajny_klucz_api` bezpiecznym kluczem.

- **Dodawanie klucza API do żądań**:
  - W każdym żądaniu API należy uwzględnić klucz w nagłówku:
    ```bash
    -H 'api-key: twój_tajny_klucz_api'
    ```
  - Przykład:
    ```bash
    curl -X GET 'http://localhost:6333' -H 'api-key: twój_tajny_klucz_api'
    ```

- **Uwaga**: Jeśli autoryzacja jest wyłączona (domyślnie w lokalnych instalacjach), można pominąć nagłówek z kluczem API. W środowisku produkcyjnym zawsze włącz autoryzację i używaj HTTPS.

## Krok 3: Kluczowe endpointy API

Qdrant oferuje REST API do interakcji z bazą danych. Poniżej przedstawiono kluczowe endpointy, ich funkcjonalność oraz przykłady komend curl.

### 1. Tworzenie kolekcji
- **Endpoint**: `PUT /collections/{collection_name}`
- **Opis**: Tworzy nową kolekcję do przechowywania wektorów.
- **Przykład**:
  ```bash
  curl -X PUT 'https://quadro.run/collections/moja_kolekcja' \
    -u admin:haslo123 \
    -H 'Content-Type: application/json' \
    -H 'api-key: tajny_klucz_123' \
    -d '{
      "vectors": {
        "size": 128,
        "distance": "Cosine"
      },
      "optimizers_config": {
        "default_segment_number": 2
      },
      "on_disk_payload": true
    }'
  ```
- **Wyjaśnienie**:
  - `name`: Nazwa kolekcji.
  - `vectors.size`: Wymiary wektorów (np. 128).
  - `vectors.distance`: Metryka odległości (np. "Cosine" dla podobieństwa kosinusowego).

### 2. Dodawanie/aktualizacja punktów
- **Endpoint**: `PUT /collections/{collection_name}/points`
- **Opis**: Dodaje lub aktualizuje punkty (wektory z opcjonalnym payloadem) w kolekcji.
- **Przykład**:
  ```bash
  curl -X PUT 'https://quadro.run/collections/moja_kolekcja/points' \
    -u admin:haslo123 \
    -H 'Content-Type: application/json' \
    -H 'api-key: tajny_klucz_123' \
    -d '{
      "points": [
        {
          "id": 1,
          "vector": [0.1, 0.2, 0.3, 0.4],
          "payload": {"miasto": "Warszawa"}
        },
        {
          "id": 2,
          "vector": [0.4, 0.5, 0.6, 0.7],
          "payload": {"miasto": "Kraków"}
        }
      ]
    }'
  ```
- **Wyjaśnienie**:
  - `id`: Unikalny identyfikator punktu.
  - `vector`: Dane wektora (musi odpowiadać rozmiarowi kolekcji).
  - `payload`: Opcjonalne metadane (np. {"miasto": "Warszawa"}).

### 3. Wyszukiwanie punktów
- **Endpoint**: `POST /collections/{collection_name}/points/search`
- **Opis**: Wyszukuje punkty podobne do podanego wektora.
- **Przykład**:
  ```bash
  curl -X POST 'https://quadro.run/collections/moja_kolekcja/points/search' \
    -u admin:haslo123 \
    -H 'Content-Type: application/json' \
    -H 'api-key: tajny_klucz_123' \
    -d '{
      "vector": [0.2, 0.3, 0.4, 0.5],
      "limit": 10
    }'
  ```
- **Wyjaśnienie**:
  - `vector`: Wektor zapytania do wyszukiwania podobnych punktów.
  - `limit`: Liczba zwracanych wyników (np. 10).

### 4. Pobieranie informacji o kolekcji
- **Endpoint**: `GET /collections/{collection_name}`
- **Opis**: Zwraca informacje o kolekcji.
- **Przykład**:
  ```bash
  curl -X GET 'https://quadro.run/collections/moja_kolekcja' \
    -u admin:haslo123 \
    -H 'Content-Type: application/json' \
    -H 'api-key: tajny_klucz_123'
  ```

### 5. Usuwanie kolekcji
- **Endpoint**: `DELETE /collections/{collection_name}`
- **Opis**: Usuwa kolekcję i wszystkie jej punkty.
- **Przykład**:
  ```bash
  curl -X DELETE 'https://quadro.run/collections/moja_kolekcja' \
    -u admin:haslo123 \
    -H 'Content-Type: application/json' \
    -H 'api-key: tajny_klucz_123'
  ```

### 6. Lista migawek
- **Endpoint**: `GET /snapshots`
- **Opis**: Wyświetla wszystkie dostępne migawki dla kolekcji.
- **Przykład**:
  ```bash
  curl -X GET 'https://quadro.run/snapshots' \
    -u admin:haslo123 \
    -H 'Content-Type: application/json' \
    -H 'api-key: tajny_klucz_123'
  ```

### 7. Tworzenie klucza shard (dla trybu rozproszonego)
- **Endpoint**: `POST /distributed/shard-key`
- **Opis**: Tworzy klucz shard dla wdrożeń rozproszonych.
- **Przykład**:
  ```bash
  curl -X POST 'https://quadro.run/distributed/shard-key' \
    -H 'Content-Type: application/json' \
    -H 'api-key: twój_tajny_klucz_api' \
    -d '{
      "shard_key": "twój_klucz_shard"
    }'
  ```

## Krok 4: Korzystanie z interfejsu webowego

- Po uruchomieniu Qdrant, interfejs webowy jest dostępny pod adresem:
  ```
  http://localhost:6333/dashboard
  ```
- Dla wdrożeń w chmurze, dodaj `:6333/dashboard` do adresu URL klastra (np. `https://xyz-example.cloud.qdrant.io:6333/dashboard`).
- Interfejs webowy oferuje intuicyjne funkcje, takie jak:
  - Zarządzanie kolekcjami.
  - Przeglądanie i wyszukiwanie punktów.
  - Monitorowanie stanu klastra.

## Krok 5: Dodatkowe uwagi

- **Autoryzacja**:
  - Jeśli autoryzacja jest włączona, dodawaj klucz API do każdego żądania:
    ```bash
    -H 'api-key: twój_tajny_klucz_api'
    ```
- **Uwagi dla środowiska produkcyjnego**:
  - Zawsze włącz autoryzację kluczem API.
  - Używaj HTTPS (TLS) do zabezpieczenia komunikacji.
  - W przypadku wdrożeń rozproszonych, zapoznaj się z dokumentacją dotyczącą zarządzania kluczami shard.
- **Dokumentacja API**:
  - Pełna lista endpointów i szczegółowa dokumentacja są dostępne w [Qdrant API Reference](https://api.qdrant.tech/v-1-13-x/api-reference).
  - Możesz również przejrzeć specyfikację OpenAPI w [OpenAPI JSON](https://github.com/qdrant/qdrant/blob/master/docs/redoc/master/openapi.json).

## Przykład praktyczny: Kolekcja transkrypcji YouTube

Poniżej przedstawiamy kompletny przykład utworzenia kolekcji do przechowywania transkrypcji filmów z YouTube oraz dodania przykładowego punktu.

### 1. Utworzenie kolekcji dla transkrypcji YouTube

```bash
curl -X PUT 'https://quadro.run/collections/youtube_transcripts' \
  -u admin:xxx \
  -H 'Content-Type: application/json' \
  -H 'api-key: xxx' \
  -d '{
    "vectors": {
      "size": 1536,
      "distance": "Cosine"
    },
    "optimizers_config": {
      "default_segment_number": 2
    },
    "on_disk_payload": true
  }'
```

### 2. Dodanie przykładowego punktu z transkrypcją

```bash
curl -X PUT 'https://quadro.run/collections/youtube_transcripts/points' \
  -u admin:xxx \
  -H 'Content-Type: application/json' \
  -H 'api-key: xxx' \
  -d '{
    "points": [
      {
        "id": 1,
        "vector": [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20],
        "payload": {
          "video_id": "dQw4w9WgXcQ",
          "title": "Rick Astley - Never Gonna Give You Up",
          "channel": "Rick Astley",
          "publish_date": "2009-10-25",
          "transcript": "We are no strangers to love. You know the rules and so do I...",
          "timestamp": "00:00:15",
          "duration": "3:32",
          "language": "en",
          "category": "Music",
          "tags": ["80s", "pop", "rick roll"]
        }
      }
    ]
  }'
```

### 3. Wyszukiwanie podobnych transkrypcji

```bash
curl -X POST 'https://quadro.run/collections/youtube_transcripts/points/search' \
  -u admin:xxx \
  -H 'Content-Type: application/json' \
  -H 'api-key: xxx' \
  -d '{
    "vector": [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20],
    "limit": 5,
    "filter": {
      "must": [
        {
          "key": "language",
          "match": {
            "value": "en"
          }
        }
      ]
    }
  }'
```

### 4. Wyszukiwanie z filtrowaniem po metadanych

```bash
curl -X POST 'https://quadro.run/collections/youtube_transcripts/points/search' \
  -u admin:xxx \
  -H 'Content-Type: application/json' \
  -H 'api-key: xxx' \
  -d '{
    "vector": [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20],
    "limit": 10,
    "filter": {
      "must": [
        {
          "key": "category",
          "match": {
            "value": "Music"
          }
        },
        {
          "key": "tags",
          "match": {
            "value": "80s"
          }
        }
      ]
    }
  }'
```

## Podsumowanie

Ten tutorial przedstawił krok po kroku, jak używać API Qdrant za pomocą komend curl. Nauczyłeś się, jak skonfigurować Qdrant lokalnie, autoryzować się za pomocą kluczy API, korzystać z kluczowych endpointów do tworzenia kolekcji, dodawania punktów, wyszukiwania i innych operacji. Dodatkowo, możesz używać interfejsu webowego do interaktywnego zarządzania danymi.

W praktycznym przykładzie pokazaliśmy, jak utworzyć kolekcję do przechowywania transkrypcji filmów z YouTube, dodać przykładowy punkt i wykonać wyszukiwanie semantyczne z filtrowaniem.

Dla bardziej zaawansowanych przypadków użycia, takich jak wdrożenia rozproszone czy optymalizacja wydajności, zapoznaj się z oficjalną dokumentacją Qdrant.