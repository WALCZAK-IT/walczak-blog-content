---
title: "Spring Data JPA - projekcja danych w zapytaniach dynamicznych"
slug: "spring-data-jpa-projekcja-danych-zapytaniach-dynamicznych"
publicationDate: "2019-06-22"
tags:
  - "Spring Data JPA"
  - "Java"
  - "projections"
  - "dynamic queries"
  - "Hibernate"
coverImage: "media/spring-data.png"
brief: "Porównuję grafy encji JPA i projekcje Spring Data jako sposoby dynamicznego pobierania wyłącznie pól potrzebnych w konkretnym zapytaniu aplikacji."
---

**Problem:** chcemy aby zapytania do naszych encji ściągały tylko te pola, które są nam potrzebne w danej sytuacji (np. do pokazania w specyficznej tabeli w UI).  
 **Wymaganie:** nasze rozwiązanie musi mieć możliwość przyjęcia dowolnej kompozycji filtrów.  
 **Możliwe rozwiązania:**

- Named Entity Graph ze standardu JPA.
- Projections - mechanizm z Spring Data

Zbadajmy je!

![spring-data.png](media/spring-data.png)

## JPA Named Entity Graphs

Ten mechanizm pochodzi bezpośrednio ze specyfikacji JPA i jest wspierany przez repozytoria Spring Data. Aby go wykorzystać musimy najpierw zdefiniować graf na naszej encji. W owym grafie określimy, które pola mają być pobierane w ramach zapytania poprzez tzw. eager fetching.

```java
@NamedEntityGraph(
    name="Person.justName",
    attributeNodes={
        @NamedAttributeNode("firstName"),
        @NamedAttributeNode("lastName")
    }
)
@Entity
public class Person {
 
    private UUID id;
    private String firstName;
    private String lastName;
    private String countryCode;
    
    // setters and getters
}
```

```java
public interface PersonRepository extends JpaRepository<Person, UUID> {
 
    @EntityGraph(value = "Person.justName", type = EntityGraphType.FETCH)
    List<Person> findByCountryCode(String countryCode);
}
```

Jak widać wykorzystanie Named Entity Graphs jest trywialne w tego typu prostym przykładzie. Istnieje jednak poważny problem w **Hibernate** (najpopularniejszej implementacji JPA), który uwidacznia się przy nieco bardziej złożonych modelach danych. W bibliotece jest [bug](https://hibernate.atlassian.net/browse/HHH-9298) wiszący od 2014, który uniemożliwia wykorzystanie Named Entity Graphs w klasach @Embedded oraz @MappedSuperclass. Jeżeli wykorzystujesz inną implementację, która nie ma tego typu ograniczeń, to możesz dowiedzieć się więcej o Named Entity Graphs z [dokumentacji JavaEE](https://javaee.github.io/tutorial/persistence-entitygraphs003.html) oraz [dokumentacji Spring Data](https://docs.spring.io/spring-data/jpa/docs/current/reference/html/#jpa.entity-graph).

## Spring Data Projections

Jest to funkcjonalność spoza specyfikacji JPA i jest wspierana wyłącznie w repozytoriach Spring Data dla JPA. Wykorzystuje interfejsy, aby zdefiniować zakres danych, który chcesz pobrać w zapytaniu poprzez tzw. eadger fetching.

```java
@Entity
public class Person {
 
    private UUID id;
    private String firstName;
    private String lastName;
    private String countryCode;
    
    // setters and getters
}
```

```java
public interface PersonNameOnly {
 
  String getFirstName();
  String getLastName();
}
```

```java
public interface PersonRepository extends JpaRepository<Person, UUID> {
 
    List<PersonNameOnly> findByCountryCode(String countryCode);
}
```

Jak widać to rozwiązanie zwraca tylko interfejs z polami projekcji, a nie encję, z której można by w dalszym przetwarzaniu pobrać pozostałe pola poprzez tzw. lazy fetching. Można to postrzegać jako minus tego mechanizmu, ale jest to też bezpieczniejsze podejście jeżeli wydajność jest kluczowa dla Twojej aplikacji. Projekcje z Spring Data mają też parę ciekawych opcji, których Named Entity Graphs nie zapewniają. Można o nich poczytać w [Spring Data JPA Reference Manual](https://docs.spring.io/spring-data/jpa/docs/current/reference/html/#projections).

## Wykorzystanie w zapytaniach dynamicznych

Oba mechanizmy opisane w niniejszym artykule wymagają nieco wysiłku aby zmusić je do współpracy z dynamicznymi zapytaniami tworzonymi przez [Spring Data Speifications](https://docs.spring.io/spring-data/jpa/docs/current/reference/html/#specifications). Normalnie dodajemy mechanizm specyfikacji do naszych repozytoriów poprzez rozszerzenie ich interfejsem JpaSpecificationExecutor\<T\>, który to zapewnia zamknięty zbiór metod akceptujących Specification\<T\> jako argument (opcjonalnie z argumentem Pageable oraz Sort). Konwencje Spring Data JPA domyślnie nie pozwolą nam użyć Specification\<T\> w naszych metodach. Z tego powodu nie możemy dodać własnych metod, które zwracałyby interfejsy projekcji lub miały nad sobą adnotacje @EntityGraph. Aby rozwiązać ten problem musimy rozszerzyć wewnętrzną funkcjonalność Spring Data - na szczęście mamy gotowe biblioteki, które to robią.

Dla Named Entity Graphs mamy bibliotekę [spring-data-jpa-entity-graph](https://github.com/Cosium/spring-data-jpa-entity-graph). Należy jednak mieć na uwadze, że w przypadku Hibernate nadal nie rozwiąże to wcześniej wspomnianego [buga](https://hibernate.atlassian.net/browse/HHH-9298).

```xml
<dependency>
    <groupId>com.cosium.spring.data</groupId>
    <artifactId>spring-data-jpa-entity-graph</artifactId>
    <version>${springDataEntityGraphVersion}</version>
</dependency>
```

```java
@Configuration
@EnableJpaRepositories(repositoryFactoryBeanClass = EntityGraphJpaRepositoryFactoryBean.class)
public class DataRepositoryConfiguration {
    //...
}
```

```java
public interface PersonRepository
    extends JpaRepository<Person, UUID>, EntityGraphJpaSpecificationExecutor<Person> { }
```

```java
Page<Persion> filteredPeople = personRepository.findAll(
    filterSpecifications, pageRequest,
    new EntityGraph("Person.justName")
);
```

Dla Spring Data Projections istnieje mała biblioteka zwana [specification-with-projection](https://github.com/pramoth/specification-with-projection). Jest też [zgłoszenie](https://jira.spring.io/browse/DATAJPA-1033) od 2016 aby dodać tą funkcjonalność do głównej biblioteki.

```xml
<dependency>
    <groupId>th.co.geniustree.springdata.jpa</groupId>
    <artifactId>specification-with-projections</artifactId>
    <version>${springDataSpecificationWithProjectionsVersion}</version>
</dependency>
```

```java
@Configuration
@EnableJpaRepositories(repositoryFactoryBeanClass = JpaSpecificationExecutorWithProjectionImpl.class)
public class DataRepositoryConfiguration {
    //...
}
```

```java
public interface PersonRepository
    extends JpaRepository<Person, UUID>, JpaSpecificationExecutorWithProjection<Person> { }
```

```java
Page<PersonNameOnly> filteredPeople = personRepository.findAll(
    filterSpecifications,
    PersonNameOnly.class
    pageRequest
);
```

---

[![](media/nextbuy_logo.png)](https://www.nextbuy24.com/)

Ten artykuł jest wynikiem naszej współpracy z [**Nextbuy**](https://www.nextbuy24.com/)- firmą dostarczającą w modelu SaaS platformę zakupową i przetargową, która łączy kupców i dostawców. Świadczymy dla nich usługi doradcze oraz wsparcie w pracach programistycznych. Jesteśmy wdzięczni, że zgodzili się upublicznić część dokumentów projektowo-rozwojowych powstałych, w wyniku tego. Możecie sprawdzić ich świetną platformę na [www.nextbuy24.com](https://www.nextbuy24.com/)

---

[![](media/walczak-it-logo5.png)](https://walczak.it/contact)

Czy potrzebujesz pomocy z którymś tematem poruszonym na naszym blogu? Jeżeli tak, [skontaktuj się z nami](https://walczak.it/pl/kontakt). Możemy pomóc poprzez doradztwo oraz usługi audytowe lub zorganizować [warsztaty szkoleniowe](https://walczak.it/pl/doradztwo-szkolenia) dla Twoich pracowników. Możemy także wspomóc proces [wytwarzania oprogramowania](https://walczak.it/pl/tworzenie-oprogramowania) w Twojej firmie poprzez outsourcing naszych programistów.
