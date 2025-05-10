# Tutorial: Korzystanie z API Qdrant za pomocą curl

## Wprowadzenie

Qdrant to otwartoźródłowa baza danych wektorowych i silnik wyszukiwania wektorowego napisany w języku Rust. Jest przeznaczony do wysokowydajnych aplikacji AI na dużą skalę, szczególnie do wyszukiwania podobieństwa wektorów. Qdrant można zainstalować lokalnie lub na serwerze, a jego API umożliwia przechowywanie, wyszukiwanie i zarządzanie wektorami z dodatkowymi danymi (payload). Od wersji 1.7 Qdrant oferuje również interfejs webowy do łatwiejszej interakcji. Ten tutorial przeprowadzi Cię przez proces konfiguracji Qdrant, autoryzacji w API, korzystania z kluczowych endpointów oraz używania interfejsu webowego.

## Krok 1: Konfiguracja Qdrant

Qdrant można uruchomić lokalnie za pomocą Dockera lub jako plik binarny. W tym tutorialu użyjemy Dockera dla prostoty.

1. **Pobierz obraz Qdrant**:
   ```bash
   docker pull qdrant/qdrant
   ```

2. **Uruchom kontener Qdrant**:
   ```bash
   docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage:z qdrant/qdrant
   ```
   - Komenda uruchamia Qdrant na porcie 6333.
   - Flaga `-v` montuje lokalny katalog (`qdrant_storage`) do przechowywania danych.

3. **Dostęp do interfejsu webowego**:
   - Po uruchomieniu Qdrant, interfejs webowy jest dostępny pod adresem:
     ```
     http://localhost:6333/dashboard
     ```
   - Interfejs webowy umożliwia zarządzanie kolekcjami, przeglądanie punktów i wykonywanie wyszukiwań w sposób interaktywny.

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
- **Endpoint**: `POST /collections`
- **Opis**: Tworzy nową kolekcję do przechowywania wektorów.
- **Przykład**:
  ```bash
  curl -X PUT 'http://localhost:8080/collections/moja_kolekcja' \
    -u admin:haslo123 \
    -H 'Content-Type: application/json' \
    -H 'X-API-KEY: tajny_klucz_123' \
    -d '{
      "vectors": {
        "size": 128,
        "distance": "Cosine"
      }
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
  curl -X PUT 'http://localhost:8080/collections/moja_kolekcja/points' \
    -u admin:haslo123 \
    -H 'Content-Type: application/json' \
    -H 'X-API-KEY: tajny_klucz_123' \
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
  curl -X POST 'http://localhost:8080/collections/moja_kolekcja/points/search' \
    -u admin:haslo123 \
    -H 'Content-Type: application/json' \
    -H 'X-API-KEY: tajny_klucz_123' \
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
  curl -X GET 'http://localhost:8080/collections/moja_kolekcja' \
    -u admin:haslo123 \
    -H 'Content-Type: application/json' \
    -H 'X-API-KEY: tajny_klucz_123'
  ```

### 5. Usuwanie kolekcji
- **Endpoint**: `DELETE /collections/{collection_name}`
- **Opis**: Usuwa kolekcję i wszystkie jej punkty.
- **Przykład**:
  ```bash
  curl -X DELETE 'http://localhost:8080/collections/moja_kolekcja' \
    -u admin:haslo123 \
    -H 'Content-Type: application/json' \
    -H 'X-API-KEY: tajny_klucz_123'
  ```

### 6. Lista migawek
- **Endpoint**: `GET /snapshots`
- **Opis**: Wyświetla wszystkie dostępne migawki dla kolekcji.
- **Przykład**:
  ```bash
  curl -X GET 'http://localhost:8080/snapshots' \
    -u admin:haslo123 \
    -H 'Content-Type: application/json' \
    -H 'X-API-KEY: tajny_klucz_123'
  ```

### 7. Tworzenie klucza shard (dla trybu rozproszonego)
- **Endpoint**: `POST /distributed/shard-key`
- **Opis**: Tworzy klucz shard dla wdrożeń rozproszonych.
- **Przykład**:
  ```bash
  curl -X POST 'http://localhost:6333/distributed/shard-key' \
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

## Podsumowanie

Ten tutorial przedstawił krok po kroku, jak używać API Qdrant za pomocą komend curl. Nauczyłeś się, jak skonfigurować Qdrant lokalnie, autoryzować się za pomocą kluczy API, korzystać z kluczowych endpointów do tworzenia kolekcji, dodawania punktów, wyszukiwania i innych operacji. Dodatkowo, możesz używać interfejsu webowego do interaktywnego zarządzania danymi.

Dla bardziej zaawansowanych przypadków użycia, takich jak wdrożenia rozproszone czy optymalizacja wydajności, zapoznaj się z oficjalną dokumentacją Qdrant.