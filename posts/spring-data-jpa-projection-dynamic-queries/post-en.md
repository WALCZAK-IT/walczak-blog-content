---
title: "Spring Data JPA - data projection in dynamic queries"
slug: "spring-data-jpa-projection-dynamic-queries"
publicationDate: "2019-06-22"
tags:
  - "Spring Data JPA"
  - "Java"
  - "projections"
  - "dynamic queries"
  - "Hibernate"
coverImage: "media/spring-data.png"
brief: "This article compares JPA entity graphs and Spring Data projections for dynamically selecting only the fields required by an application query."
---

**Problem:** we want queries to our entities to eagerly fetch only the fields that we need in the given context (for example to show in a specific UI data table).  
 **Requirement:** our solution must be able to accept dynamic filter compositions.  
 **Possible solutions:**

- Named Entity Graphs from the JPA standard
- Projections mechanism from Spring Data

Lets research them!


## JPA Named Entity Graphs

This mechanism comes directly from the JPA specifications and is supported by Spring Data repositories. To use it we must first specify a graph on our entity. In that graph we define the fields to be eagerly fetched.

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

As you can see using entity graphs is trivial in this simple example. However, there is a crucial problem for more complex data models if you choose **Hibernate** as your JPA implementation. There is a [bug](https://hibernate.atlassian.net/browse/HHH-9298)hanging around since 2014 which makes using named entity graphs impossible in @Embedded and @MappedSuperclass classes. If you're using another implementation that does not suffer from this limitation then you can read more about entity graphs in the [Java EE documentation](https://javaee.github.io/tutorial/persistence-entitygraphs003.html) and the [Springs Data documentation](https://docs.spring.io/spring-data/jpa/docs/current/reference/html/#jpa.entity-graph).

## Spring Data Projections

This is a feature from outside of the JPA specs and is supported only by Spring Data repositories for JPA. It uses interfaces to define the scope of data which you want to be fetched eagerly.

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

As you can see this solutions returns only an interfaces with the projected fields and not an entity in which you could choose to get other properties using lazy fetching. This can be seen as a downside but in fact its a safer approach if performance is crucial to your app. Spring Data projections also have some interesting additional features that named entity graphs cannot provide. Your can read more about them in the [Spring Data JPA Reference Manual](https://docs.spring.io/spring-data/jpa/docs/current/reference/html/#projections).

## Usage in dynamic queries

Both mechanisms described in this article require some effort to make them work with dynamic queries constructed by the [Specifications mechanism from Spring Data](https://docs.spring.io/spring-data/jpa/docs/current/reference/html/#specifications). Normaly we add the specifications mechanism to our repositories by extending the JpaSpecificationExecutor\<T\> interface which gives a closed set of methods that accept Specification\<T\> as their argument (optionally with the Pageable and Sort argument). Out of the box Spring Data JPA conventions do not let us to use Specification\<T\> in our own methods. Because of this we cannot add our own dynamic query methods which would return a projection interface or have an @EntityGraph annotation. To solve this problem we must extend the internals of Spring Data - fortunately there are working third party libraries that do just that.

For Named Entity Graphs you have the [spring-data-jpa-entity-graph](https://github.com/Cosium/spring-data-jpa-entity-graph) library. However keep in mind that in the case of Hibernate it still will not solve the [bug](https://hibernate.atlassian.net/browse/HHH-9298) we mentioned earlier.

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

For Spring Data Projections there is a small library called [specification-with-projection](https://github.com/pramoth/specification-with-projection). There is also a [feature request](https://jira.spring.io/browse/DATAJPA-1033) since 2016 to add this to the main library.

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

This article is a result of our cooperation with [**Nextbuy**](https://www.nextbuy24.com/)- a SaaS company which develops a procurement and online auction platform to connect buyers and suppliers. We provide various consulting and software development services to them and they have kindly allowed us to publish part of the resulting research / design documents. You can checkout their amazing platform at [www.nextbuy24.com](https://www.nextbuy24.com/)

---

[![](media/walczak-it-logo5.png)](https://walczak.it/contact)
