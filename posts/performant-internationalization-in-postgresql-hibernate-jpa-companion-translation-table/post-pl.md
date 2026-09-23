---
title: "Wydajna internacjonalizacja w PostgreSQL + Hibernate / JPA - tabela towarzysząca z tłumaczeniami"
slug: "wydajna-internacjonalizacja-w-postgresql-hibernate-jpa-tabela-towarzyszaca-z-tlumaczeniami"
publicationDate: "2021-04-03"
tags:
  - "PostgreSQL"
  - "Hibernate"
  - "JPA"
  - "internationalization"
  - "database design"
  - "Java"
  - "performance"
coverImage: "media/multilingual-data.png"
brief: "Artykuł pokazuje implementację wielojęzycznego wyszukiwania tekstowego na poziomie pól z użyciem tabeli towarzyszącej, indeksów GIN i GiST, PostgreSQL, Hibernate oraz Spring Data JPA."
---

Kontynuując nasze rozważania, jak optymalnie zaimplementować wyszukiwanie tekstowe na poziomie pojedynczych pól w systemie opiszemy koncepcję tabeli towarzyszącej z tłumaczeniami, którą będziemy tworzyć dla każdej klasy. Zastosujemy tutaj indeksy typu GIN / GiST opisane na początku niniejszej serii artykułów oraz spróbujemy zaimplementować opisywaną koncepcję w technologii Spring Data JPA, Hibernate oraz Postgres.


## Spis treści

Ten wpis na jest częścią serii artykułów o internacjonalizacji danych ze wsparciem dla wyszukiwania tekstowego:

1. [Indeksy dostepne w Postgres oraz antywzorce](https://walczak.it/pl/blog/internacjonalizacja-danych-z-wyszukiwaniem-tekstowym-indeksy-w-postgres-oraz-antywzorce)
2. Wydajna internacjonalizacja w PostgreSQL + Hibernate / JPA:
  1. Tabela towarzysząca z tłumaczeniami - obecnie czytasz
  2. [Kolumna HStore z tłumaczeniami](https://walczak.it/pl/blog/wydajna-internacjonalizacja-w-postgresql-hibernate-jpa-kolumna-hstore-z-tlumaczeniami)

Chcesz otrzymać notyfikację, gdy pozostałe artykuły zostaną opublikowane? Polub nas na [Facebook](https://www.facebook.com/walczak.it/) lub śledź na [4programmers.net](https://4programmers.net/Profile/33337/Microblog).

## Model relacyjny

Z perspektywy SQL koncepcja tabeli towarzyszącej z tłumaczeniami polega na tym, że dla każdej tabeli reprezentującej jakiś byt w systemie, który ma pola wymagające tłumaczeń, będziemy tworzyć towarzyszącą tabelę zawierającą owe tłumaczenia. Jeden wiersz tabeli towarzyszącej będzie zawierał tłumaczenia wszystkich pól dla danego wiersza tabeli źródłowej i danego języka. Zobrazujmy to na przykładzie kartoteki produktów sprzedawanych w sklepie.

![concept-a-tables-1.png](media/concept-a-tables-1.png)

Produkt w kartotece po za identyfikatorem, który stanowi klucz główny, posiada pola które:

- nie wymagają tłumaczenia: Code, Price,
- są przetłumaczalne: Name, Description.

Tabela towarzysząca z tłumaczeniami pól produktu ma klucz główny kompozytowy składający się z:

- odwołania do identyfikatora produktu,
- kodu języka, do którego przetłumaczyliśmy w danym wierszu pola.

Pozostałe kolumny trzymają tłumaczenia tożsame z kolumnami z tabeli produktów. Zakładamy, że w tabeli Product posługujemy się językiem natywnym dla załogi obsługującej system, natomiast w ProductTranslation trzymamy tłumaczenia pól na pozostałe języki.

## Model obiektowy z JPA

Spróbujemy teraz skonstruować obiektowy model danych w Javie oraz JPA, który powinien wygenerować model relacyjny analogiczny do modelu przedstawionego w poprzednim rozdziale.

```java
@Entity
public class Product {
 
    @Id
    private UUID id = UUID.randomUUID();
     
    @Embedded
    private ProductDetails details;
     
    @ElementCollection(fetch = FetchType.LAZY)
    private Map<String, TranslatableProductDetails> translatedDetailsByLanguage = new HashMap<>();
 
    protected Product() { }
     
    public Product(ProductDetails details) {
        this.details = details;
    }
    
    // getters and setters
}
```

```java
@Embeddable
public class ProductDetails extends TranslatableProductDetails {
     
    private String code;
    private BigDecimal price;
 
    // getters and setters
}
```

```java
@Embeddable
@MappedSuperclass
public class TranslatableProductDetails {
     
    private String name;
    private String description;
 
    // getters and setters
}
```

## Usługa w Spring wyszukująca po tekście

Przetestujemy teraz wykorzystanie modelu w praktyce poprzez zaimplementowanie usługi Springowej umożliwiającej poprzez REST API:

- dodać oraz pobrać tłumaczenia danego produktu;
- wyszukać produkty po nazwie wg. danego języka.

Obsługę zapytań SQL, na której będzie bazować owa usługa, zaimplementujemy natomiast z pomocą Spring Data JPA.

```java
@RestController
@RequestMapping("products")
@Transactional
public class ProductService {
     
    private final ProductRepostiory repostiory;
 
    public ProductService(ProductRepostiory repostiory) {
        this.repostiory = repostiory;
    }
     
    @PostMapping
    public @ResponseBody Product add(@RequestBody ProductDetails details) {
        return repostiory.save(new Product(details));
    }
     
    @PutMapping("{id}/translations/{language}")
    public @ResponseBody void setTranslation(
        @PathVariable("id") UUID id,
        @PathVariable("language") String language,
        @RequestBody TranslatableProductDetails details) {
        Product product = repostiory.getOne(id);
        product.getTranslatedDetailsByLocale().put(language, details);
    }
     
    @GetMapping("{id}")
    public @ResponseBody Product get(@PathVariable("id") UUID id) {
        return repostiory.findById(id)
            .orElseThrow(IdNotFoundException::new);
    }
     
    @GetMapping
    public @ResponseBody List<Product> find(
        @RequestParam("name") String name) {
        return repostiory.findByNameLocalized(
            name, LocaleContextHolder.getLocale().getLanguage(),
            PageRequest.of(0, 100)
        );
    }
}
```

```java
public interface ProductRepostiory extends JpaRepository<Product, UUID> {
     
    @Query(
        "select p from Product p left join p.translatedDetailsByLanguage td "
            + "where index(td) = ?2 and ("
            + "lower(p.details.name) like concat('%', lower(?1), '%') "
            + "or lower(td.name) like concat('%', lower(?1), '%')"
            + ")"
    )
    public List<Product> findByNameLocalized(String name, String language, Pageable pageable);
}
```

## Indeksy w Postgres oraz testy wydajności

Biblioteka Hibernate na podstawie modelu z adnotacjami JPA wygeneruje nam tabele SQL, jednak nie zapewni optymalizacji. Samodzielnie musimy zadbać o dodanie do Postgres indeksów typu GIN, o których wspomnieliśmy w pierwszym artykule z serii.

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
 
CREATE INDEX product_details_name_idx ON product
USING GIN (lower(details_name) gin_trgm_ops);
 
CREATE INDEX product_translated_name_idx ON product_translateddetailsbylanguage
USING GIN (lower(translateddetailsbylanguage_value_name) gin_trgm_ops);
```

Napiszemy też skrypt w Scala pod [Gatling](https://gatling.io) aby zapełnić naszą bazę danych po REST API.

```scala
class ConceptAPopulateSimulation extends In18jpaSimulation {
 
  val scn = scenario("Concept A - Populate")
    .repeat(100000)(
        feed(createFeeder())
        .exec(
          http("add-product")
            .post("/products")
            .body(StringBody(
              """
              | {
              |   "code": "${code}",
              |   "name": "${name}",
              |   "description": "${description}",
              |   "price": ${price}
              | }
              """.stripMargin))
            .check(status.is(200))
            .check(jsonPath("$.id").saveAs("id"))
        )
        .exec(
          http("add-translation")
            .put("/products/${id}/translations/pl")
            .body(StringBody(
              """
                 | {
                 |    "name": "${nameTranslation}",
                 |    "description": "${descriptionTranslation}"
                 | }
              """.stripMargin))
            .check(status.is(200))
        )
    )
 
  setUp(
      scn.inject(
          atOnceUsers(1)
        )
      .protocols(createHttpProtocol())
  )
}
```

Wykonajmy zapytanie do naszej usługi żeby sprawdzić jak działa wyszukiwanie.

```json
GET /products?name=abcd
Accept: application/json
Accept-Language: pl-PL

HTTP/1.1 200
Content-Type: application/json
[
    {
        "id": "21d84002-da10-450c-90f8-448fe92d4583",
        "details": {
            "name": "CqaBCdrrdmD",
            "description": "us2a6LvnDXs4bDimkCNd77bKxUOBADaLQa6lIC9LGzKBrTFqOGVa",
            "code": "Z",
            "price": 0.19
        },
        "translatedDetails": {
            "name": "ZXMzRdraH2",
            "description": "O0x9VV6X53iss8ttiOunsHfKOvsbASihGTfVRWMMXn50K45WwFCk3619G3p"
        }
    },
    {
        "id": "65e1b7c6-0c5e-4e36-8bbc-6cf160b0514b",
        "details": {
            "name": "XWgIWaBcDkrbs",
            "description": "",
            "code": "PWSMXoei3",
            "price": 0.87
        },
        "translatedDetails": {
            "name": "vZX6uQcr1NW4k4p",
            "description": "W6rZILJv9gqTXGCeZGwQU50ElZwtaGbrtWA65f8Hrkuen85V3KU1AVFknyw2DYISVvjZZY"
        }
    }
]
```

Wynik poprawny ale wyszukiwanie pośród 100'000 produktów zajęło nam całkiem sporo czasu: **~350 ms**. Sprawdźmy zatem czy indeksy były wykorzystywane przez bazę danych. Wykorzystując opcje `spring.jpa.show-sql=true` możemy w naszej Spring Bootowej aplikacji podejrzeć jakie zapytania wysyła Hibernate do Postgresa, a następnie wrzucić je w EXPLAIN.

```sql
explain select
    product0_.id as id1_0_, product0_.details_code as details_2_0_,
    product0_.details_price as details_3_0_,
    product0_.details_description as details_4_0_,
    product0_.details_name as details_5_0_
from Product product0_ left outer join Product_translatedDetailsByLanguage translated1_ on product0_.id=translated1_.Product_id
where translated1_.translatedDetailsByLanguage_KEY='pl'
and (
    lower(product0_.details_name) ilike ('%'||lower('aaa')||'%')
    or lower(translated1_.translatedDetailsByLanguage_value_name) like ('%'||lower('aaa')||'%')
)
```

```sql
Hash Join  (cost=6108.18..17175.56 rows=10447 width=85)
  Hash Cond: (product0_.id = translated1_.product_id)
  Join Filter: ((lower((product0_.details_name)::text) ~~* '%aaa%'::text) OR (lower((translated1_.translateddetailsbylanguage_value_name)::text) ~~ '%aaa%'::text))
  ->  Seq Scan on product product0_  (cost=0.00..3341.14 rows=100000 width=85)
  ->  Hash  (cost=3531.59..3531.59 rows=100000 width=26)
        ->  Seq Scan on product_translateddetailsbylanguage translated1_  (cost=0.00..3531.59 rows=100000 width=26)
              Filter: ((translateddetailsbylanguage_key)::text = 'pl'::text)
```

Jak widać na obu tabelach są wykonywane pełne skanowania ich całej zawartości (Seq Scan), więc indeksy nie zostały użyte. Na [StackOverflow](https://stackoverflow.com/questions/49117971/postgresql-gin-indexes-on-fields-from-many-tables-and-or-conditions) oraz [Postgres Mailing List](https://www.postgresql.org/message-id/530F4FC5.9040100%40free.fr) można przeczytać że optymalizator zapytań nie radzi sobie z warunkiem OR po dwóch złączonych tabelach przy tego typu indeksach. Zasugerowane zostało zastosowanie unii. Faktycznie rozbicie zapytania na dwie części skutkuje wykorzystaniem indeksu.

```sql
explain select
    product0_.id as id1_0_, product0_.details_code as details_2_0_,
    product0_.details_price as details_3_0_,
    product0_.details_description as details_4_0_,
    product0_.details_name as details_5_0_
from Product product0_
where lower(product0_.details_name) like ('%'||lower('aaa')||'%')
```

```sql
Bitmap Heap Scan on product product0_  (cost=61.36..2148.41 rows=5337 width=85)
  Recheck Cond: (lower((details_name)::text) ~~ '%aaa%'::text)
  ->  Bitmap Index Scan on product_details_name_idx  (cost=0.00..60.02 rows=5337 width=0)
        Index Cond: (lower((details_name)::text) ~~ '%aaa%'::text)
```

```sql
explain select *
from Product_translatedDetailsByLanguage translated1_
where translated1_.translatedDetailsByLanguage_KEY='pl'
and lower(translated1_.translatedDetailsByLanguage_value_name) like ('%'||lower('aaa')||'%')
```

```sql
Bitmap Heap Scan on product_translateddetailsbylanguage translated1_  (cost=61.31..2020.58 rows=5330 width=79)
  Recheck Cond: (lower((translateddetailsbylanguage_value_name)::text) ~~ '%aaa%'::text)
  Filter: ((translateddetailsbylanguage_key)::text = 'pl'::text)
  ->  Bitmap Index Scan on product_translated_name_idx  (cost=0.00..59.97 rows=5330 width=0)
        Index Cond: (lower((translateddetailsbylanguage_value_name)::text) ~~ '%aaa%'::text)
```

Z punktu widzenia samego Postgresa wystarczyło by jedynie zrobić unię i odsiać duplikaty. Gorzej tu jednak będzie z wykorzystaniem tego poprzez JPA / Hibernate, które nie wspiera unii. Niestety aby dokończyć tę implementację musielibyśmy:

- albo tworzyć zapytania w czystym SQL - rozwiązanie mało wygodne, zwłaszcza jeżeli w dalszym rozwoju usług chcielibyśmy tworzyć zapytania dynamicznie poprzez [JPA Criteria API](https://www.baeldung.com/rest-search-language-spring-jpa-criteria) albo [Spring Data Specifications](https://www.baeldung.com/rest-api-search-language-spring-data-specifications),
- albo zrobić oddzielne zapytanie dla każdego kryterium i połączyć wyniki w Javie.

Jako, że oba rozwiązania nie są w pełni satysfakcjonujące zakończymy tutaj nasze eksperymenty z koncepcją towarzyszącej tabeli z tłumaczeniami.

## Wnioski

Wzorzec tabeli towarzyszącej z tłumaczeniami jest wydajnym rozwiązaniem problemu omawianego w niniejszej serii artykułów, jednak może być problematyczy w integracji na styku bazy danych i ORM. Jak pokazał powyższy eksperyment połączenie ograniczeń plannera Postgres z ograniczeniami Hibernate / JPA zmusiłby nas do zastosowania nie do końca optymalnego obejścia problemu. Dlatego też warto na tym etapie rozważań przejść do kolejnej konepcji, która mimo typu danych dla specyficznego dla Postgres, może okazać się prostsza w integracji z Hibernate / JPA.

## Czytaj dalej

Kody źródłowe zastosowane w tym artykule można znaleźć na naszym [repozytorium bitbucket](https://bitbucket.org/walczak_it/in18-jpa-data/src/master/).

Kolejny artykuł z serii: [Kolumna HStore z tłumaczeniami](https://walczak.it/pl/blog/wydajna-internacjonalizacja-w-postgresql-hibernate-jpa-kolumna-hstore-z-tlumaczeniami)

---

[![](media/nextbuy_logo.png)](https://www.nextbuy24.com/)

Ten artykuł jest wynikiem naszej współpracy z [**Nextbuy**](https://www.nextbuy24.com/)- firmą dostarczającą w modelu SaaS platformę zakupową i przetargową, która łączy kupców i dostawców. Świadczymy dla nich usługi doradcze oraz wsparcie w pracach programistycznych. Jesteśmy wdzięczni, że zgodzili się upublicznić część dokumentów projektowo-rozwojowych powstałych, w wyniku tego. Możecie sprawdzić ich świetną platformę na [www.nextbuy24.com](https://www.nextbuy24.com/)

---

[![](media/walczak-it-logo4.png)](https://walczak.it/contact)
