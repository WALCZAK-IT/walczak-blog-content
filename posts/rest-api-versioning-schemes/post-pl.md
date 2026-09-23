---
title: "Schematy wersjonowania REST API"
slug: "schematy-wersjonowania-rest-api"
publicationDate: "2024-10-05"
tags:
  - "REST"
  - "API design"
  - "versioning"
  - "GraphQL"
coverImage: "media/rest-versioning.drawio.png"
brief: "Artykuł omawia popularne strategie wersjonowania REST API, pokazując jak wprowadzać zmiany bez przerywania działania istniejących integracji klientów."
---

Wersjonowanie jest kluczowe dla utrzymania stabilnego i rozwijającego się RESTowego API. W miarę dojrzewania każdego API zmiany stają się nieuniknione, czy to z powodu poprawek błędów, nowych funkcji, czy ulepszeń wydajności. Odpowiednie wersjonowanie pozwala wprowadzać te zmiany bez przerywania działania istniejących integracji klientów. W tym artykule omawiamy kilka popularnych strategii wersjonowania REST API, analizując ich wady i zalety.


## Odkładanie zmian wersji

Przed eksploracją różnych schematów wersjonowania, ważne jest, aby zdać sobie sprawę, że niezależnie od wybranej metody, często korzystne jest odłożenie wprowadzenia nowych wersji poprzez dodawanie funkcji przy jednoczesnym zachowaniu wstecznej kompatybilności. Utrzymanie kompatybilności pomaga zminimalizować zakłócenia dla istniejących klientów i zmniejsza obciążenie związane z zarządzaniem wieloma wersjami.

Dodawanie nowych pól do odpowiedzi HTTP jest zazwyczaj proste, ponieważ klienci mogą po prostu ignorować pola, których nie rozpoznają. Jednak wyzwania pojawiają się, gdy wymagane jest znaczące refaktoryzowanie modelu danych w celu obsługi nowych funkcji.

### Przykład

Rozważmy system początkowo działający w jednym kraju, z endpointem katalogu produktów takim jak:

```json
GET /products/213123
```

```json
{
  "id": 213123,
  "name": "Bubbly Soda",
  "price": 10.99
}
```

Gdy przyjdzie nam rozbudować system o obsługę transakcji międzynarodowo wtedy będziemy musieli np. dodać kody walut oraz stawkę VAT. Najbardziej eleganckim rozwiązaniem wydaje się zmiana pola `price` na obiekt:

```json
{
  "id": 213123,
  "name": "Bubbly Soda",
  "price": {
    "value": 10.99,
    "currencyCode": "EUR",
    "vatRate": 0.23
  }
}
```

Jednak taka zmiana złamałaby działanie istniejących klientów oczekujących, że `price` będzie wartością numeryczną, a nie obiektem.

### Równoważenie wstecznej kompatybilności i elegancji modelu

Rozwiązaniem tego problemu byłoby dodanie nowego pola, takiego jak `newPrice`, przy jednoczesnym zachowaniu oryginalnego pola `price` dla wstecznej kompatybilności:

```json
{
  "id": 213123,
  "name": "Bubbly Soda",
  "price": 10.99,
  "newPrice": {
    "value": 10.99,
    "currencyCode": "EUR",
    "vatRate": 0.23
  }
}
```

Jednak wprowadzenie pola takiego jak `newPrice` jest mało eleganckie i nie semantycznie opisuje wartość tego pola. Lepszym podejściem, jeżeli jest taka możliwość, jest wybranie bardziej semantycznie opisowej nazwy dla nowego pola, takiej jak np. `grossPrice`, wskazującej, że wartość zawiera podatek VAT:

```json
{
  "id": 213123,
  "name": "Bubbly Soda",
  "price": 10.99,
  "grossPrice": {
    "value": 10.99,
    "currencyCode": "EUR",
    "vatRate": 0.23
  }
}
```

Poprzez staranne dobranie nazw nowych pól, możesz rozszerzyć API bez poświęcania czytelności lub konieczności wprowadzenia nowej wersji. W dokumentacji oczywiście oznaczyłbyś pole `price` jako przestarzałe i przeznaczone do usunięcia w następnej wersji API lub zasobu.

## Cykl życia wersjonowanego API lub zasobu

Każda wersja API lub zasobu podąża za cyklem życia, który zazwyczaj obejmuje:

1. **Wprowadzenie**: Nowa wersja jest wydana, a klienci są zachęcani do jej przyjęcia.
2. **Powiadomienie o przestarzałości**: Klienci są informowani, że istniejąca wersja zostanie wycofana, zazwyczaj poprzez dokumentację, change log i bezpośrednią komunikację (np. e-maile).
3. **Deprekacja**: Okres przejściowy, w którym zarówno stara, jak i nowa wersja są dostępne, pozwalając klientom na migrację.
4. **Wycofanie**: Stara wersja zostaje wycofana i staje się niedostępna.

Skuteczne zarządzanie cyklem życia API zależy od jasnej komunikacji z klientami i partnerami. Utrzymanie zainteresowanych stron poinformowanych poprzez kompleksową dokumentację i terminowe powiadomienia zapewnia płynne przejście między wersjami.

## Globalne wersjonowanie API przy użyciu prefiksów ścieżki

**Przykład**: `/v2/users`, `/v2/orders`

Ta metoda polega na poprzedzeniu całej ścieżki API numerem wersji. Jest to wzorzec znany ze starych SOAP API i promuje rzadkie, rewolucyjne zmiany wpływające na całe API.

### Charakterystyka

- **Prostota**: Łatwe do zrozumienia i wdrożenia.
- **Izolacja**: Różne wersje mogą współistnieć bez zakłóceń.
- **Rewolucyjne zmiany**: Zachęca do dużych, rzadkich aktualizacji zamiast stopniowych ulepszeń.

### Zalety

- **Wyraźne rozdzielenie**: Różne wersje są całkowicie oddzielone, co zmniejsza ryzyko przypadkowych interakcji między wersjami.
- **Łatwe do komunikacji**: Łatwiej jest komunikować jedną rewolucyjną zmianę co kilka lat niż mniejsze zmiany co miesiąc.

### Wady

- **Koszty utrzymania**: Wspieranie wielu wersji zwiększa złożoność i w tym schemacie trzeba dać partnerom dużo czasu na dostosowanie ich systemów.
- **Zniechęca do stopniowych aktualizacji**: Mniejsze, specyficzne dla zasobów zmiany są trudniejsze do wdrożenia bez wpływu na całe API.

### Inne warianty tego schematu

Inne warianty tego schematu wykorzystują subdomeny do wersjonowania API, takie jak `api-v1.myapp.com`, `v2.myapp.com`, lub niestandardowe nagłówki, takie jak `X-API-Version: 2`.

## Wersjonowanie per zasób

Poniżej przedstawimy różne schematy wersjonowania opartego na zasobach. Wszystkie mają pewne wspólne cechy.

### Charakterystyka

- **Granularna kontrola**: Każdy zasób może być wersjonowany oddzielnie.
- **Elastyczność**: Umożliwia stopniowe aktualizacje i stopniową migrację.

### Zalety

- **Ukierunkowane aktualizacje**: Zmiany w jednym zasobie nie wymagają zmian w innych.
- **Zmniejszony wpływ**: Minimalizuje zakres zmian dla klientów.

### Wady

- **Trudne do zakomunikowania**: Ze względu na ciągłe wprowadzanie małych zmian rozłożonych w czasie, może być trudno śledzić wszystkie modyfikacje, aktualizować odpowiednio dokumentację i informować integratorów.
- **Niespójne API**: Różne zasoby mogą mieć różne najnowsze numery wersji, co prowadzi do zamieszania.

### Wersjonowanie zasobów oparte na ścieżce

**Przykład**: `/users-v1`, `/orders-v3`

W tym podejściu numery wersji są dodawane do poszczególnych ścieżek zasobów, co pozwala każdemu zasobowi ewoluować niezależnie.

### Wersjonowanie za pomocą parametrów zapytania

**Przykład**: `/users?version=2`

Informacja o wersji jest zawarta jako parametr zapytania w żądaniu API.

#### Zalety

- **Łatwiejsza eksploracja**: Najnowsza wersja stosowana domyślnie, jeśli parametr `version` jest pominięty - ułatwia to przeglądanie API dla nowych użytkowników.

#### Wady

- **Zepsuje działanie naiwnie napisanych klientów**: Jeśli przekazywanie numeru wersji jest opcjonalne, to klienci, którzy go nie używają, przestaną działać, gdy nowa wersja stanie się domyślną dla danego zasobu.

## Wersjonowanie za pomocą nagłówków Content-Type i Accept

**Przykład**:

Nagłówek żądania:  
 `Accept: application/vnd.example.resource+json; version=2`

Nagłówek odpowiedzi:  
 `Content-Type: application/vnd.example.resource+json; version=2`

Ta metoda osadza informacje o wersji w typie mediów określonym w nagłówkach `Content-Type` i `Accept`.

### Zalety

- **Zgodność z REST**: Zgodna z zasadami negocjacji treści w HTTP i HATEOAS.
- **Przejrzyste URI**: Utrzymuje URI czyste i spójne.

### Wady

- **Złożoność**: Parsowanie niestandardowych typów mediów i parametrów dodaje złożoności.

## Wersjonowanie w GraphQL

GraphQL podchodzi do wersjonowania inaczej niż REST API. Zamiast wersjonować całe API lub poszczególne zasoby, GraphQL kładzie nacisk na ewolucję schematu przy jednoczesnym zachowaniu wstecznej kompatybilności.

### Kluczowe koncepcje

- **Ewolucja schematu**: Schemat może być rozwijany poprzez oznaczanie starych pól jako przestarzałe i wprowadzanie nowych bez wpływu na istniejące zapytania. Jednak, jak zauważono na początku artykułu, może to zmusić nas do użycia nieoptymalnych semantycznie nazw pól.
- **Oznaczanie pól jako przestarzałe**: GraphQL zapewnia wbudowaną dyrektywę `@deprecated` do oznaczania pól jako przestarzałych, wraz z opcjonalnymi komunikatami przyczyn.
- **Pojedynczy endpoint**: GraphQL działa poprzez pojedynczy endpoint, polegając na kliencie w kwestii kreowania zakresu danych jaki chce otrzymać.

### Zalety

- **Śledzenie użycia przestarzałych pól**: Ponieważ każdy klient określa dokładnie, których pól potrzebuje, możesz monitorować, które przestarzałe pola są nadal używane.
- **Zmniejszenie liczby zmian łamiących**: Poprzez oznaczanie pól jako przestarzałe i zapewnianie alternatyw, zmiany łamiące są zminimalizowane.

### Wady

- **Trudne do zakomunikowania**: Ze względu na ciągłe wprowadzanie małych zmian rozłożonych w czasie, może być trudno śledzić wszystkie modyfikacje, aktualizować odpowiednio dokumentację i informować o tym integratorów.
- **Złożona implementacja**: GraphQL API jest zazwyczaj skomplikowane do zakodowania po stronie serwera, zwłaszcza jeżeli zależny nam na optymalizacji wydajności.
- **Brak ostrzeżeń o przestarzałych polach w klientach**: Większość klientów GraphQL nie czyta automatycznie metadanych introspekcyjnych, aby ostrzegać deweloperów o używaniu przestarzałych pól. Pomimo potencjalnego wsparcia w technologii, deweloperzy nadal muszą monitorować dokumentację i ogłoszenia, aby reagować na deprykację pól.

## Podsumowanie

Skuteczne wersjonowanie API jest kluczowe dla utrzymania solidnego i przyjaznego dla użytkownika API. Wybór strategii wersjonowania zależy od różnych czynników, w tym charakteru API, potrzeb klientów i pożądanej równowagi między elastycznością a prostotą.

- **Odkładanie zmian wersji**: Staraj się utrzymać wsteczną kompatybilność poprzez ostrożne rozszerzanie API, opóźniając potrzebę nowych wersji.
- **Globalne wersjonowanie API** jest proste, ale może prowadzić do znacznych obciążeń.
- **Wersjonowanie per zasób** oferuje elastyczność, ale może skutkować niespójnym doświadczeniem API.

Projektując API, rozważ kompromisy każdej metody i wybierz tę, która najlepiej odpowiada Twoim celom i oczekiwaniom konsumentów API. Jasna komunikacja i przemyślane planowanie są kluczem do płynnej ewolucji API.
