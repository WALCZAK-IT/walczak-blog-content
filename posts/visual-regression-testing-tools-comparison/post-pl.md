---
title: "Porównanie narzędzi do visual regression testing"
slug: "porownanie-narzedzi-do-visual-regression-testing"
publicationDate: "2024-03-11"
tags:
  - "visual regression testing"
  - "testing"
  - "Playwright"
  - "Cypress"
  - "WebdriverIO"
  - "CI/CD"
coverImage: ""
brief: "Testy regresji wizualnej wykrywają niezamierzone zmiany w interfejsie użytkownika, porównując zrzuty ekranu z zatwierdzonymi wzorcami. W tym artykule porównujemy narzędzia do tworzenia testów, chmurowe platformy przeglądarkowe, usługi do przeglądania zrzutów oraz proces CI, który łączy te elementy."
---

## Wprowadzenie

Testy regresji wizualnej wykrywają zmiany, których często nie zauważą zwykłe testy funkcjonalne: przesunięty przycisk, nagłówek zawinięty do drugiej linii albo zmienione odstępy w modalu po aktualizacji CSS. Test renderuje stronę, wykonuje zrzut ekranu i porównuje go z zatwierdzonym wzorcem. Istotna różnica staje się wtedy zmianą do przeanalizowania przez programistę lub projektanta.

Wybór stosu do testów regresji wizualnej nie sprowadza się tylko do wyboru biblioteki testowej. Są to trzy osobne decyzje:

1. **Jak pisać i uruchamiać testy** — na przykład z użyciem WebdriverIO, Cypress lub Playwright.
2. **Gdzie uruchamiać przeglądarki i urządzenia** — lokalnie, w CI albo na platformie chmurowej, takiej jak LambdaTest lub BrowserStack.
3. **Gdzie przechowywać i przeglądać zrzuty ekranu** — lokalnie albo w usłudze takiej jak Percy, Happo lub Chromatic.

W tym artykule porównujemy wszystkie te warstwy i opisujemy proces CI, który pozwala bezpiecznie zatwierdzać zmiany zrzutów ekranu. Porównanie odzwierciedla narzędzia i ceny dostępne w czasie zbierania informacji, w marcu 2024 roku. Integracje, obsługa przeglądarek i plany cenowe często się zmieniają, dlatego przed podjęciem ostatecznej decyzji należy sprawdzić aktualną dokumentację.

## Co sprawia, że narzędzie do regresji wizualnej jest użyteczne?

Samo porównanie zrzutów ekranu to tylko jeden z elementów całego procesu. W praktyce narzędzie powinno ułatwiać tworzenie deterministycznych zrzutów, dostrajanie akceptowalnych różnic, analizowanie diffu i zatwierdzanie nowego wzorca z poziomu pull requesta.

Najważniejsze pytania to:

- Czy narzędzie potrafi wykonać zrzut całej strony i zaczekać, aż aplikacja osiągnie stabilny stan?
- Czy zespół może skonfigurować tolerancję dla antyaliasingu, animacji i niewielkich różnic w renderowaniu?
- Czy testy mogą działać równolegle dla wielu przeglądarek i rozmiarów ekranu?
- Czy wzorzec i diff można łatwo przejrzeć w CI?
- Czy serwer aplikacji może zostać uruchomiony jako część polecenia testowego?
- Czy narzędzie pasuje do używanych przez zespół testów end-to-end, testów komponentów, testów urządzeń i języków programowania?

## Narzędzia do tworzenia testów

W tym porównaniu uwzględniamy trzy narzędzia do tworzenia testów: [WebdriverIO](https://webdriver.io/), [Cypress](https://www.cypress.io/) i [Playwright](https://playwright.dev/). Wszystkie mogą być używane do testów przeglądarkowych, ale różnią się tym, jak wiele funkcji testów wizualnych jest wbudowanych, a jak wiele zależy od wtyczek.

### Zrzuty ekranu i porównywanie diffów

| Możliwość | WebdriverIO | Cypress | Playwright |
| --- | --- | --- | --- |
| Porównywanie zrzutów ekranu | Dostępne przez rozszerzenie, na przykład `@wdio/visual-service` | Dostępne przez wtyczki, na przykład [`cypress-visual-regression`](https://github.com/kirill-konshin/cypress-visual-regression) | Wbudowane w Playwright Test za pomocą `toHaveScreenshot` |
| Konfiguracja tolerancji różnic | Zależy od usługi lub wtyczki do testów wizualnych | Zależy od wtyczki | Tak, na przykład `maxDiffPixels`, `maxDiffPixelRatio` i `threshold` |
| Porównywanie wielu zrzutów w jednym uruchomieniu | Zależy od runnera lub wtyczki | Zależy od wtyczki | Tak, choć porównywanie dowolnych zestawów obrazów może wymagać własnych narzędzi pomocniczych |
| Zarządzanie wzorcami | Lokalnie; przegląd w chmurze przez wtyczki lub usługi | Lokalnie; przegląd w chmurze przez wtyczki lub usługi | Lokalnie; przegląd w chmurze przez wtyczki lub usługi, takie jak [Playshot](https://github.com/sudharsan-selvaraj/playshot) |
| Interaktywny podgląd diffu | Zależy od reportera lub wtyczki | Zależy od wtyczki | Dostępny w raporcie HTML i obsługiwanych procesach przeglądu |
| Zrzuty całej strony | Tak | Tak, zależnie od wtyczki i konfiguracji | Tak |

Wbudowane asercje Playwright pozwalają łatwo napisać niewielki test wizualny:

```typescript
import { test, expect } from '@playwright/test';

test('strona główna ma oczekiwany wygląd', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveScreenshot('homepage.png', {
    fullPage: true,
    maxDiffPixelRatio: 0.01,
  });
});
```

Tolerancję należy skalibrować, a nie ustawiać wyłącznie po to, aby test przestał się nie udawać. Zbyt wysoki próg może ukryć prawdziwą regresję układu, natomiast próg równy zero może sprawić, że zestaw testów będzie niestabilny z powodu niegroźnych różnic w renderowaniu.

### Uruchamianie aplikacji i synchronizacja

| Możliwość | WebdriverIO | Cypress | Playwright |
| --- | --- | --- | --- |
| Uruchamianie serwera aplikacji | Zwykle konfigurowane i uruchamiane osobno | Zwykle konfigurowane i uruchamiane osobno | Obsługiwane przez konfigurację `webServer` |
| Oczekiwanie na załadowanie strony | Ustawienia frameworka i jawna logika testów | Komendy Cypress i jawne oczekiwanie; stałych opóźnień należy w miarę możliwości unikać | Wbudowane stany ładowania strony, takie jak `load`, `domcontentloaded` i `networkidle` |
| Testy end-to-end | Tak | Tak | Tak |
| Testy komponentów | Dostępne przez integracje WebdriverIO | Obsługiwane po skonfigurowaniu testów komponentów | Dostępne, ale w czasie tego porównania eksperymentalne |

Testy wizualne powinny czekać na znaczący stan aplikacji, a nie tylko na upływ określonego czasu. Oczekiwanie na znaną odpowiedź sieciową, widoczny komponent albo zakończenie wskaźnika ładowania jest zwykle stabilniejsze niż wymuszanie stałego opóźnienia. Warto również kontrolować fonty, animacje, zegar, dane losowe i treści zewnętrzne w momencie wykonywania zrzutu.

### Przeglądarki, urządzenia i wykonywanie testów

| Możliwość | WebdriverIO | Cypress | Playwright |
| --- | --- | --- | --- |
| Obsługiwane przeglądarki | Przeglądarki zgodne z WebDriver; Safari zazwyczaj wymaga lokalnego Maca | Przeglądarki oparte na Chromium, Edge, Electron i Firefox | Chromium, Firefox i WebKit, w tym emulacja urządzeń |
| Wykonywanie równoległe | Zależy od runnera i platformy wykonawczej | Ograniczone w porównaniu z pozostałymi narzędziami; równoległość w chmurze jest dostępna | Wbudowane workery równoległe i projekty |
| Testy na fizycznych urządzeniach | Tak, przez zgodne protokoły WebDriver i Appium | Brak natywnej obsługi fizycznych urządzeń | Obsługiwana jest emulacja przeglądarek i urządzeń; testy na fizycznych urządzeniach mogą wymagać innej platformy |
| Frameworki testowe | Mocha, Jasmine i Cucumber.js | Własny runner testów Cypress | Playwright Test |
| Języki | JavaScript/TypeScript oraz biblioteki klienckie WebDriver dla kilku języków | JavaScript/TypeScript | JavaScript/TypeScript, Python, Java i .NET |
| Protokół i architektura | Oparte na WebDriver | Komendy są wykonywane przez przeglądarkę i jej architekturę automatyzacji | Bezpośrednio korzysta z protokołów automatyzacji przeglądarek |

WebdriverIO dobrze pasuje do projektu, który już korzysta z WebDriver, Appium albo wielu integracji zewnętrznych. Cypress oferuje skoncentrowane na doświadczeniu programisty narzędzia i dużą społeczność, ale porównywanie wizualne i obsługa fizycznych urządzeń w większym stopniu zależą od zewnętrznych integracji. Playwright zapewnia najbardziej kompletny wbudowany proces testów przeglądarkowych i zrzutów ekranu z całej tej trójki, a także wygodne projekty przeglądarek i workery równoległe.

### Doświadczenie programisty i ekosystem

Oryginalne notatki oceniały narzędzia jakościowo w następujący sposób:

| Aspekt | WebdriverIO | Cypress | Playwright |
| --- | ---: | ---: | ---: |
| Intuicyjność w tym zastosowaniu | ++ | + | +++ |
| Społeczność i ekosystem | ++ | +++ | ++++ |
| Liczba zależności w podstawowej konfiguracji | +++ | ++ | + |
| Wydajność w ocenianej konfiguracji | ++ | ++ | +++ |
| Wsparcie i dokumentacja | Tak | Tak, z różnicami zależnymi od wtyczek | Tak |

Oceny te są oczywiście subiektywne. Najlepiej traktować je jako punkt wyjścia do przygotowania proof of concept, a nie uniwersalny ranking. Zespół, który ma już duży zestaw testów Cypress, może uzyskać lepsze rezultaty, rozszerzając istniejące rozwiązanie, zamiast migrować do narzędzia z lepszymi wbudowanymi asercjami zrzutów ekranu.

Dodatkowe obserwacje z przeprowadzonej oceny:

- WebdriverIO nie zapewnia domyślnie integracji z Jest, ale pomocne mogą być niezależne szablony, takie jak [jest-webdriverio-standalone-boilerplate](https://github.com/erwinheitzman/jest-webdriverio-standalone-boilerplate).
- Porównywanie wizualne w Cypress zależy od wtyczek, a ich działanie może różnić się między trybem interaktywnym a uruchomieniem z wiersza poleceń. Często rekomendowana dawniej wtyczka [`cypress-plugin-snapshots`](https://github.com/meinaart/cypress-plugin-snapshots) nie była dobrym wyborem dla Cypress 13; podczas oceny lepiej działała [`cypress-visual-regression`](https://github.com/kirill-konshin/cypress-visual-regression).
- Playwright można połączyć ze Storybookiem. Przykłady można znaleźć w artykułach [Visual testing Storybook with Playwright](https://jamesiv.es/blog/frontend/testing/2024/03/11/visual-testing-storybook-with-playwright) i [Playwright VRT](https://pow.rs/blog/playwright-vrt/).

## Chmurowe platformy do automatyzacji przeglądarek

Chmurowe platformy przeglądarkowe są przydatne, gdy zespół potrzebuje przeglądarek lub fizycznych urządzeń, których nie ma na runnerach CI. Mogą również zapewnić spójne środowiska i uprościć wykonywanie testów równolegle.

W tym porównaniu uwzględniono platformy [LambdaTest](https://www.lambdatest.com) i [BrowserStack](https://www.browserstack.com/).

| Możliwość | LambdaTest | BrowserStack |
| --- | --- | --- |
| Emulacja przeglądarek i urządzeń | Tak | Tak |
| Fizyczne urządzenia | Tak | Tak |
| Integracja z WebdriverIO, Cypress i Playwright | Tak | Tak |
| Integracja z GitLab CI | Tak | Tak |
| Ceny | Plany płatne; w ocenianym procesie możliwa była konfiguracja za 0 USD dzięki integracji z Percy | Plany płatne |

Wybór platformy zależy mniej od samej listy funkcji, a bardziej od dokładnego zestawu przeglądarek i urządzeń, dostępności geograficznej, limitów równoległości oraz liczby minut CI wymaganych przez projekt. Przed wyborem dostawcy warto uruchomić reprezentatywne zrzuty na przeglądarkach istotnych dla użytkowników i sprawdzić, czy wynik jest wystarczająco stabilny do porównywania z wzorcem.

## Usługi do przechowywania i przeglądania zrzutów

Usługa do przeglądania zmian w zrzutach zamienia różnice wizualne w proces zespołowy. Zamiast pobierać artefakty CI i ręcznie analizować pliki, recenzent może otworzyć pull request, porównać wzorzec z obrazem testowym i zaakceptować albo odrzucić zmianę.

Wzięto pod uwagę usługi [Percy](https://percy.io), [Pixeleye](https://pixeleye.io), [Wopee](https://wopee.io/), [Happo](https://happo.io/) i [Chromatic](https://chromatic.com).

| Cecha | Percy | Pixeleye | Wopee | Happo | Chromatic |
| --- | --- | --- | --- | --- | --- |
| Plan odnotowany w czasie badań | Bezpłatnie do 5000 zrzutów ekranu | Bezpłatnie do 7500 zrzutów ekranu | Plany płatne od 79 USD za 10 000 zrzutów | Bezpłatnie do 5000 zrzutów ekranu | Plany płatne od 149 USD za 35 000 zrzutów |
| Obsługa Storybooka | Dostępne integracje | Należy sprawdzić aktualną integrację | Należy sprawdzić aktualną integrację | Należy sprawdzić aktualną integrację | Silna integracja; Storybook obsługuje testy wizualne przez Chromatic |

Powyższe liczby są historycznymi notatkami, a nie aktualnym porównaniem cen. Plany, limity zrzutów, okresy przechowywania i definicje zrzutu mogą się zmieniać. Zwykle ważniejsze są następujące kryteria:

- czy usługa integruje się z wybranym runnerem testów i dostawcą CI;
- jak obsługuje branche, pull requesty i własność wzorców;
- czy recenzenci mogą zobaczyć nakładkę, porównanie obok siebie i szczegóły na poziomie pikseli;
- jak obsługuje dynamiczne treści i różnice między przeglądarkami;
- czy model cenowy pasuje do liczby stron, rozmiarów ekranu i commitów objętych testami.

W projekcie intensywnie korzystającym ze Storybooka Chromatic jest naturalnym kandydatem, ponieważ jest z nim ściśle zintegrowany. W przypadku ogólnego zestawu testów end-to-end lepiej może sprawdzić się Percy, Happo albo inna usługa niezależna od konkretnego narzędzia. W małym projekcie może wystarczyć lokalny raport HTML, bez potrzeby centralnego przeglądania.

## Praktyczny proces CI

Wybór narzędzia przynosi korzyści dopiero wtedy, gdy wynik testów jest częścią procesu obsługi pull requestów. Stabilny pipeline może składać się z następujących kroków:

1. **Zbuduj deterministyczną aplikację.** Użyj stałych danych testowych i fontów, kontroluj czas oraz ustawienia regionalne, a treści zewnętrzne zastąp wersjami mockowanymi lub lokalnymi.
2. **Uruchom aplikację.** Jeśli to możliwe, użyj konfiguracji serwera dostarczanej przez runner testów. W przeciwnym razie uruchom serwer jawnie i zaczekaj na sprawdzenie jego stanu.
3. **Uruchom zestaw testów wizualnych.** Dla każdego właściwego pull requesta wykonuj ten sam zestaw tras, komponentów, rozmiarów ekranu i przeglądarek.
4. **Porównaj ze wzorcem.** Przechowuj zrzuty testowe i diffy jako artefakty CI albo wysyłaj je do usługi do przeglądania.
5. **Opublikuj check w pull requeście.** Check powinien prowadzić bezpośrednio do raportu i wyraźnie odróżniać awarię testu od zmiany wizualnej oczekującej na akceptację.
6. **Przejrzyj zmianę.** Recenzent potwierdza, że różnica jest zamierzona. Jeśli nie jest, należy poprawić kod zamiast aktualizować wzorzec.
7. **Zatwierdź nowy wzorzec.** Dopiero po akceptacji zmienione zrzuty powinny stać się wzorcami dla kolejnych uruchomień.

W GitLabie link do raportu można udostępnić jako artefakt joba, a sam job uczynić wymaganym przez reguły merge requestów. Usługa do hostowania zrzutów może dodatkowo dodać status check i bezpośredni link do zmienionych obrazów. Najważniejsza zasada jest taka, że aktualizacja wzorca musi być jawną i możliwą do przejrzenia czynnością — nie powinna następować automatycznie tylko dlatego, że test zakończył się niepowodzeniem.

## Rekomendacje

Nie istnieje jedno najlepsze narzędzie, ale porównanie prowadzi do kilku rozsądnych domyślnych wyborów:

- **Zacznij od Playwright**, jeśli tworzysz nowy zestaw testów regresji wizualnej dla aplikacji przeglądarkowej. Asercje zrzutów, projekty przeglądarek, zrzuty całych stron, workery równoległe i raportowanie HTML są dostępne bez składania rozwiązania z wielu wtyczek.
- **Rozszerz Cypress**, jeśli projekt już z powodzeniem korzysta z Cypress, a istniejące testy komponentów lub end-to-end są wartościowe. Starannie wybierz wtyczkę wizualną i sprawdź, czy działa z używaną wersją Cypress oraz w trybie CI.
- **Wybierz WebdriverIO**, jeśli zgodność z WebDriver/Appium, istniejąca infrastruktura Selenium albo szeroki ekosystem runnerów są ważniejsze niż wbudowane asercje zrzutów ekranu.
- **Dodaj platformę chmurową**, jeśli wymagany zestaw przeglądarek i fizycznych urządzeń nie może być niezawodnie odtworzony na runnerach CI.
- **Dodaj hostowaną usługę do przeglądania**, jeśli kilka osób musi akceptować zmiany wizualne albo lokalne artefakty zrzutów stają się trudne w zarządzaniu. W przeciwnym razie wystarczający może być raport HTML i artefakty CI.

## Powiązane tematy

Testy regresji wizualnej nie zastępują natywnych testów interfejsu ani testów obciążeniowych. W przypadku aplikacji na platformy Apple [XCUITest](https://developer.apple.com/documentation/xctest) obejmuje inną warstwę testowania. Eksperymenty z testami obciążeniowymi front-endu opisano w artykule [Front-end load testing with Playwright and Artillery](https://medium.com/@tolandominic/front-end-load-testing-with-playwright-and-artillery-4fa1ac615fda) oraz w dokumentacji [Artillery](https://www.artillery.io/).

## Podsumowanie

Testy regresji wizualnej są najbardziej skuteczne, gdy traktuje się je jako proces przeglądu, a nie zbiór plików ze zrzutami ekranu. Wybierz runner testów, który potrafi tworzyć stabilne zrzuty, uruchamiaj go w powtarzalnym środowisku przeglądarkowym i zadbaj o to, aby diff można było łatwo zaakceptować w pull requeście. W nowym projekcie dobrym punktem wyjścia jest Playwright; istniejące projekty Cypress lub WebdriverIO powinny najpierw sprawdzić, czy można rozszerzyć obecny stos. W każdym przypadku deterministyczne testy i jawny proces akceptacji wzorców są ważniejsze niż nazwa usługi przechowującej obrazy.
