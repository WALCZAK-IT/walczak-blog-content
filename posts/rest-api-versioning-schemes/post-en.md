---
title: "REST API versioning schemes"
slug: "rest-api-versioning-schemes"
publicationDate: "2024-10-05"
tags:
  - "REST"
  - "API design"
  - "versioning"
  - "GraphQL"
coverImage: "media/rest-versioning.drawio.png"
brief: "Versioning is crucial for maintaining a stable and evolving REST API. As your API matures, changes become inevitable, whether due to bug fixes, new features, or performance enhancements. This article explores several common REST API versioning strategies, discussing their pros and cons."
---

Versioning is crucial for maintaining a stable and evolving REST API. As your API matures, changes become inevitable, whether due to bug fixes, new features, or performance enhancements. Proper versioning allows you to introduce these changes without breaking existing client integrations. This article explores several common REST API versioning strategies, discussing their pros and cons.


## Postponing version changes

Before exploring different versioning schemes, it's crucial to recognize that regardless of the method chosen, postponing the introduction of new versions by adding features while preserving backward compatibility is often beneficial. Maintaining compatibility helps minimize disruptions for existing clients and reduces the overhead associated with managing multiple versions.

Adding new fields to responses is generally straightforward, as clients can simply ignore fields they do not recognize. However, challenges arise when significant refactoring of the data model is required to support new features.

### Example Scenario

Consider a system initially operating in a single country, with a product catalog endpoint like:

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

As the system expands internationally, additional information such as currency codes and VAT rates must be included. The most elegant solution might seem to involve changing the `price` field to an object:

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

However, this change would break existing clients expecting `price` to be a numeric value, not an object.

### Balancing Backward Compatibility and Model Elegance

One workaround is to add a new field, such as `newPrice`, while retaining the original `price` field for backward compatibility:

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

However, introducing a field like `newPrice` may compromise the semantics and elegance of the data model. A better approach is to choose a semantically meaningful name for the new field, such as `grossPrice`, indicating that the value includes VAT:

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

By carefully selecting new field names, you can extend the API without sacrificing clarity or requiring a new version. In your documentation you would of course mark the `price` field as deprecated and for removal in the next API / resource version.

## Lifecycle of a Versioned API or Resource

Every version of an API or resource follows a lifecycle that typically includes:

1. **Introduction**: The new version is released, and clients are encouraged to adopt it.
2. **Deprecation Notice**: Clients are informed that an existing version will be deprecated, usually through documentation, changelogs, and direct communication (e.g., emails).
3. **Deprecation Period**: A grace period during which both the old and new versions are available, allowing clients time to migrate.
4. **Retirement**: The old version is retired and becomes unavailable.

Effective API lifecycle management hinges on clear communication with clients and partners. Keeping stakeholders informed through comprehensive documentation and timely notifications ensures a smooth transition between versions.

## Global API versioning using path prefixes

**Example**: `/v2/users` ​​​​`/v2/orders`

This method involves prefixing the entire API path with a version number. Its a pattern known from old SOAP APIs and promotes infrequent, revolutionary changes that affect the entire API.

### Characteristics

- **Simplicity**: Easy to understand and implement.
- **Isolation**: Different versions can coexist without interference.
- **Revolutionary Changes**: Encourages large, infrequent updates rather than gradual improvements.

### Pros

- **Clear Separation**: Different versions are entirely separate, reducing the risk of accidental cross-version interactions.
- **Easy to communicate**: Its easier to communicate one revolutionary change every couple of years that smaller changes every month.

### Cons

- **Maintenance Overhead**: Supporting multiple versions increases complexity and in this scheme one has to give clients a long time to adjust.
- **Discourages Incremental Updates**: Smaller, resource-specific changes are harder to implement without affecting the entire API.

### Other variations of this scheme

Other variations of this scheme use subdomains for API versioning like `api-v1.myapp.com` `v2.myapp.com` or custom headers like `X-API-Version: 2`

## Per-Resource Versioning

Below we will present various schemes of resource based versioning. All of them have some shared characteristics.

### Characteristics

- **Granular Control**: Each resource can be versioned separately.
- **Flexibility**: Enables incremental updates and gradual migration.

### Pros

- **Targeted Updates**: Changes to one resource don't necessitate changes to others.
- **Reduced Impact**: Minimizes the scope of changes for clients.

### Cons

- **Hard To Communicate**: Due to the continuous introduction of small changes over time, it can be difficult to keep track of all modifications, update documentation accordingly, and inform integrators.
- **Inconsistent API**: Different resources may have different leatest version numbers, leading to confusion.

### Path based resource versioning

**Example**: `/users-v1`, `/orders-v3`

In this approach, version numbers are appended to individual resource paths, allowing each resource to evolve independently.

### Query Parameter Versioning

**Example**: `/users?version=2`

Version information is included as a query parameter in the API request.

**Pros**

- **Easier exploration:** latest version as default if `version` is ommited may ease browsing the API for new comers

### Cons

- **Will break naively written clients**: if passing the version number is optional then client that not use it will break when a new version becomes the default for the given resource.

### Versioning Using Content-Type and Accept Headers

**Example**:

- Request Header: `Accept: application/vnd.example.resource+json; version=2`
- Response Header: `Content-Type: application/vnd.example.resource+json; version=2`

This method embeds version information within the media type specified in the `Content-Type` and `Accept` headers.

### Pros:

- **RESTful Compliance**: Aligns with the principles of content negotiation in HTTP and HEOS.
- **Transparent URIs**: Keeps the URI clean and consistent.

### Cons

- **Complexity**: Parsing custom media types and parameters adds complexity.

## Versioning in GraphQL

GraphQL approaches versioning differently compared to REST APIs. Instead of versioning the entire API or individual resources, GraphQL emphasizes evolving the schema while maintaining backward compatibility.

### Key Concepts

- **Evolving Schema**: The schema can be evolved by deprecating old fields and introducing new ones without affecting existing queries. However as noted in the beginning of the article this can force you to use not optimal semantic names of fields.
- **Field Deprecation**: GraphQL provides a built-in `@deprecated` directive to mark fields as deprecated, along with optional reason messages.
- **Single Endpoint**: GraphQL operates through a single endpoint, relying on the client to request specific data shapes.

### Pros

- **Tracking Deprecated Field Usage**: Since each client specifies exactly which fields it needs, you can monitor which deprecated fields are still in use.
- **Reduced Breaking Changes**: By deprecating fields and providing alternatives, breaking changes are minimized.

### Cons

- **Hard To Communicate**: Due to the continuous introduction of small changes over time, it can be difficult to keep track of all modifications, update documentation accordingly, and inform integrators.
- **Complex Implementation**: A GraphQL API is usually a complex beast to code and make it performant on the server side.
- **Clients Lack Deprecation Warnings**: Most GraphQL clients do not automatically read introspection metadata to alert developers about using deprecated fields. Despite potential support in the technology, developers still need to monitor documentation and announcements to stay informed about deprecations.

## Summary

Effective API versioning is crucial for maintaining a robust and user-friendly API. The choice of versioning strategy depends on various factors, including the nature of the API, client needs, and the desired balance between flexibility and simplicity.

- **Postponing Version Changes**: Strive to maintain backward compatibility by carefully extending the API, delaying the need for new versions.
- **Global API Versioning** is straightforward but may lead to significant overhead.
- **Per-Resource Versioning** offers flexibility but can result in an inconsistent API experience.

When designing an API, consider the trade-offs of each method and choose the one that best aligns with your goals and the expectations of your API consumers. Clear communication and thoughtful planning are key to a smooth API evolution.
