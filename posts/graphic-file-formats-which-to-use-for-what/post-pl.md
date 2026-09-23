---
title: "Formaty plików graficznych - które służą do czego"
slug: "formaty-plikow-graficznych-ktore-sluza-do-czego"
publicationDate: "2024-01-07"
tags:
  - "graphics"
  - "file formats"
  - "RAW"
  - "SVG"
  - "JPG"
  - "PNG"
  - "AVIF"
  - "PDF"
coverImage: "media/formats-question.png"
brief: "Praktyczna ściąga dotycząca wyboru formatów plików graficznych do publikacji w Internecie, druku, fotografii i grafiki wektorowej, z uwzględnieniem kolorów, kompresji i czcionek."
---

Często zdarza się, że pracownicy agencji marketingowych lub początkujący graficy nie posiadają technicznej wiedzy o działaniu poszczególnych formatów plików graficznych i ich odpowiednim zastosowaniu. To staje się wyraźne, gdy przekazują do publikacji w Internecie grafikę wektorową w formacie JPG lub gdy dostarczają do druku plik PDF z paletą kolorów RGB i załączonymi niestandardowymi czcionkami. Celem tego artykułu jest zapewnienie szybkiej ściągi dla takich osób, aby prace przekazywane przez nich nie traciły na jakości w wyniku konwersji do niewłaściwych formatów oraz żeby nie okazywało się w drukarni że wydruki wyszły inne niż podgląd dokumentu na monitorze.


## Współpraca z fotografami

### RAW - negatyw zdjęcia

Format plików RAW, często określany mianem "cyfrowego negatywu", zawiera kompletny zestaw informacji zarejestrowanych przez sensor aparatu w momencie uchwycenia zdjęcia, nie podlegając automatycznej obróbce czy kompresji. To doskonały wybór dla fotografa, który zamierza precyzyjnie przetworzyć obraz za pomocą specjalistycznego oprogramowania, takiego jak Darktable czy Adobe Lightroom, aby później wykorzystać go w pracach graficznych. Mimo to, RAW nie jest formatem zalecanym do przekazywania agencjom czy grafikom. Po dokładnym dostosowaniu parametrów zdjęcia, fotograf powinien wyeksportować je do formatu, który nadal umożliwia wysokiej jakości obróbkę cyfrową, lecz nie jest tak specjalistyczny i ściśle związany z fotografią jak RAW. Idealnym wyborem do przekazania zdjęć jest TIFF, opisany poniżej.

### TIFF - zdjęcia przygotowane do dalszej obróbki

Tagged Image File Format (TIFF) jest idealnym wyborem do przechowywania zdjęć w dużym, bezstratnym formacie, który może być później cyfrowo poprawiany lub konwertowany do różnych innych formatów. Jego przewaga wynika z faktu, że umożliwia bezstratną kompresję — dąży do redukcji rozmiaru pliku (z dziesiątek do setek MB), nie obniżając przy tym jakości. To stanowi zasadniczy kontrast do formatu JPG, gdzie każde kolejne zapisanie pliku prowadzi do nieuchronnej utraty ostrości i granularności obrazu ze względu na kompresję stratną. Wielokrotne edytowanie i zapisywanie pliku JPG pogarsza jakość z każdym krokiem, a utrata detali staje się szczególnie widoczna przy powiększeniu zdjęcia lub w jego wydrukach.

Grafik może bezpośrednio zaimportować plik w formacie TIFF do projektu przygotowywanego do druku. Może się jednak okazać, że potrzebna będzie konwersja z palety kolorów RGB, używanej przez monitory, na paletę CMYK, stosowaną przez drukarnie. W przypadku publikacji elektronicznej, takiej jak strona internetowa lub same pliki, konieczna będzie konwersja do formatu JPG. Kompresja stratna jest w tym przypadku akceptowalna jedynie jako ostatni krok, który zmniejsza rozmiar zdjęcia z kilkudziesięciu MB do kilku MB.

## Współpraca z grafikami

### Formaty edytowalne

Każdy grafik, tworząc nowy projekt przeznaczony do druku lub infografikę do publikacji online, zapisze swoją pracę w formacie odpowiadającym używanemu programowi graficznemu. Dla Adobe InDesign będzie to plik INDD, natomiast dla Adobe Illustrator – AI. Pliki te charakteryzują się następującymi cechami:

- Warto je przechowywać, ponieważ umożliwiają one łatwą edycję i dalszy rozwój projektu.
- Nie nadają się do bezpośredniej publikacji online, ponieważ mało kto dysponuje oprogramowaniem umożliwiającym ich otwarcie.
- Często nie są odpowiednie dla drukarni – drukarnia może nie posiadać wymaganego programu, a plik może zawierać odnośniki do zewnętrznych plików, takich jak zdjęcia czy niestandardowe czcionki, które mogą nie wydrukować się poprawnie po przesłaniu pliku.

Z tych powodów, graficy zwykle konwertują projekty do bardziej uniwersalnych formatów przed ich publikacją lub wysłaniem do drukarni.

### PDF - idealny do drukarni i publikacji dokumentów w siecii

Portable Document Format to wszechstronny format przydatny zarówno do druku, jak i publikacji dokumentów cyfrowych. Nie jest natomiast odpowiedni do osadzania grafiki na stronach WWW lub w mailach - jest otwierany zazwyczaj jako osobny plik. Nie nie nadaje się też do rozległej edycji – poza drobnymi poprawkami, graficy napotkają znaczące trudności w dalszym rozwijaniu projektu opierając się wyłącznie na pliku PDF. Ten format jest zazwyczaj stosowany na końcowym etapie procesu, głównie do celów publikacyjnych. Warto jednak pamiętać, że metoda przygotowania pliku PDF do druku różni się od tej stosowanej przy przygotowaniu do publikacji online.

W kontekście materiałów przeznaczonych do druku, kluczowe jest, aby pliki PDF były oparte na palecie kolorów CMYK oraz aby wszystkie niestandardowe czcionki zostały zamienione na krzywe. Również zdjęcia powinny być dostosowane do palety CMYK i osadzone w wysokiej rozdzielczości. Dzięki temu można zagwarantować, że wydruk będzie wiernie odzwierciedlał projekt.

Dla publikacji cyfrowych zalecana jest paleta kolorów RGB, dostosowana do ekranów i urządzeń cyfrowych. Wskazane jest również stosowanie wyższego stopnia kompresji obrazów, by rozmiar PDF-a nie przekraczał kilkunastu megabajtów. Dla porównania, plik PDF przeznaczony do druku może osiągać rozmiar nawet setek megabajtów.

### SVG - Grafika wektorowa w sieci

Scalable Vector Graphics (SVG) to format plików graficznych, który służy do przechowywania grafiki wektorowej. W odróżnieniu od formatów rastrowych, takich jak JPG czy PNG, SVG pozwala na dowolne skalowanie grafiki bez utraty jakości. Dzięki temu jest to doskonały wybór dla projektów, które wymagają ostrości krawędzi niezależnie od rozmiaru wyświetlanego obrazu.

SVG jest szczególnie popularny do publikacji w sieci. Znajduje zastosowanie w przypadku:

- **Logotypów** – dzięki niewielkiemu rozmiarowi plików i możliwości skalowania bez utraty jakości.
- **Infografik i wykresów** – zapewnia ostre krawędzie i czytelność przy dowolnym powiększeniu.
- **Animacji** – SVG wspiera proste animacje, które można tworzyć za pomocą CSS i JavaScript.
- **Ikon i elementów interfejsu użytkownika (UI)** – dzięki kompatybilności z przeglądarkami i możliwości łatwej edycji.

SVG nie jest natomiast powszechnie stosowany w projektach przeznaczonych do druku. Bardzo późno do tego standardu dodano obsługę CMYK i profili ICC, a co za tym idzie są słabo wspierane.

### JPG - publikowanie zdjęć

Format Joint Photographic Experts Group jest idealnym wyborem do publikacji zdjęć w sieci, ponieważ jest on powszechnie obsługiwany przez przeglądarki internetowe oraz aplikacje do przeglądania plików. Dzięki zastosowaniu kompresji stratnej, JPG może znacząco zmniejszyć rozmiar zdjęcia, co jest szczególnie przydatne przy ograniczonej przepustowości internetu. Kompresja ta została specjalnie opracowana z myślą o zdjęciach. Jednak dla publikacji różnego rodzaju infografik, logotypów i innych grafik, gdzie ważna jest ostrość krawędzi i przezroczystość, bardziej odpowiedni może okazać się format PNG.

### PNG - publikowanie obrazów wektorowych

Portable Network Graphics jest dobrym wyborem do publikacji infografik, logotypów, wykresów i innych grafik przygotowanych na podstawie tzw. projektów wektorowych. Dla tego rodzaju projektów, PNG oferuje kompresję, która umożliwia zmniejszenie rozmiaru pliku przy zachowaniu ostrych krawędzi obrazu - co jest istotne, ponieważ kompresja JPG często prowadzi do ich zaburzenia w przypadku tego typu grafik. Różnice między grafiką rastrową a wektorową demonstruje poniższy obraz:

![raster-vs-vector2.jpg](media/raster-vs-vector2.jpg)

Powyżej zastosowaliśmy format JPG dla obu grafik - dlatego właśnie po prawej widać trochę szumu wokół krawędzi wykresów i figur. Gdybyś podzielili ten obrazek na dwa i dla prawej strony zastosowali **PNG**, wtedy krawędzie grafik byłby ostre. PNG nie jest jednak nieskończenie skalowalny z zachowaniem ostrości krawędzi tak jak SVG. Jest jednak formatem prostszym niż SVG i z tego względu stwarza mniej problemów z kompatybilnością na starszych urządzeniach.

### Aktualizacja: AVIF - następca JPG i PNG

Format AVIF (AV1 Image File Format) to nowoczesny standard graficzny oparty na otwartym kodeku wideo AV1. Zapewnia on znacznie wyższą wydajność kompresji niż starsze formaty, takie jak JPG, PNG, a nawet WebP, oferując lepszą jakość obrazu przy zauważalnie mniejszym rozmiarze pliku. AVIF jest niezwykle wszechstronny – obsługuje zarówno kompresję stratną, jak i bezstratną, przezroczystość (kanał alfa), animacje, a także szeroką paletę barw i tryb HDR.

Podczas zapisu do formatu **AVIF** należy dokonać wyboru między kompresją stratną a bezstratną, kierując się tą samą logiką, co w przypadku dylematu: **JPG** (kompresja stratna) czy **PNG** (kompresja bezstratna).

Na dzień dzisiejszy (2026 rok) wsparcie dla formatu AVIF jest powszechne i ugruntowane. Jest on natywnie i w pełni obsługiwany przez wszystkie główne przeglądarki internetowe, w tym Google Chrome, Mozilla Firefox, Apple Safari oraz Microsoft Edge (zarówno w wersjach desktopowych, jak i mobilnych). Dzięki temu AVIF stał się nowym, domyślnym standardem optymalizacji grafik i zdjęć w nowoczesnym projektowaniu stron WWW.
