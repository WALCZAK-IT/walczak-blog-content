---
title: "Geolocation of Website Users"
slug: "geolocation-of-website-users"
publicationDate: "2023-10-31"
tags:
  - "geolocation"
  - "GeoIP"
  - "web development"
  - "APIs"
  - "Google Cloud"
coverImage: "media/Internet-icon.png"
brief: "This article compares browser-based Geolocation API with server-side IP geolocation and evaluates services that help locate website users."
---

The ability to precisely locate browser users is a key functionality of many applications and online services. Choosing the right geolocation method is not always straightforward. In this article, we will examine the strengths and weaknesses of the browser’s Geolocation API versus server-side IP-based geolocation, and also compare the effectiveness of various services supporting the latter option.


## Survey Research

In the following article, we will present the effectiveness of individual geolocation methods based on conducted survey research. The survey was conducted among 19 users in Poland, of which 37% were in the capital at that time. 32% of the surveyed individuals were using smartphones with internet via cellular network - we asked them to turn off WiFi. Meanwhile, the remaining 68% were using computers connected to the network through WiFi or wired connection.

## Browser Geolocation API

Geolocation API is an API available for JavaScript in browsers, utilizing GPS data, Wi-Fi network information, and cellular signals to provide precise location data. However, to use this API, it is necessary to ask the browser user for additional permissions. The effectiveness in the case of users who agreed to grant these additional permissions is as follows:

![geolocation-api.png](media/geolocation-api.png)

Returned the city where I am

Not my city but close, up to 50 km

A farther city but from the same province

Different province, but at least the country matches

Even the country doesn’t match

As various sources indicate, only a few users agree to share their location data through Geolocation API. Online privacy is much more crucial for users visiting a website than minor improvements such as determining their city by sharing precise location information. In the same moment they could click the dialog allowing permission, they might as well select their city in the UI.

## Server-side IP-based Geolocation

An alternative to the Geolocation API is technology based on the user's IP address. This method is more universal because it doesn’t require additional permissions. IP-based geolocation utilizes a database of IP addresses and their locations to determine the approximate position of a user. However, the location based on IP is less precise, and its effectiveness can be diminished by the use of mobile internet connections and technologies such as VPN or proxy. Below, we present the statistics of geolocation effectiveness through various services maintaining databases of IP ranges and their associated countries and cities.

### Geoapify

Paid service available at: [www.geoapify.com](https://www.geoapify.com/)

with a free package for websites with less traffic and limited commercialization.

![geoapify.png](media/geoapify.png)

Returned the city where I am

Not my city but close, up to 50 km

A farther city but from the same province

Different province, but at least the country matches

Even the country doesn’t match

### IPGeolocation

Paid service available at: [ipgeolocation.io](https://ipgeolocation.io/)

with a free package available for non-commercial websites, even those with higher traffic.

![ipgeolocation.png](media/ipgeolocation.png)

Returned the city where I am

Not my city but close, up to 50 km

A farther city but from the same province

Different province, but at least the country matches

Even the country doesn’t match

### IP-API

Service available at: [ip-api.com](https://ip-api.com/)

A substantial free package available for websites, even those with high traffic. There is an option to purchase additional bandwidth capacity.

![ip-api.png](media/ip-api.png)

Returned the city where I am

Not my city but close, up to 50 km

A farther city but from the same province

Different province, but at least the country matches

Even the country doesn’t match

### Metadata of a HTTP request in GCP AppEngine

Every developer deploying their service in AppEngine on Google Cloud Platform gets access to various types of metadata from the client making the HTTP request. Among them is also geolocation based on IP, processed by Google’s infrastructure. If you are not working with GCP, you can deploy the following service, [appengine-ip-to-location](https://github.com/renaudcerrato/appengine-ip-to-location), to make this feature available to yourself as a microservice API.

![gcp-ip.png](media/gcp-ip.png)

Returned the city where I am

Not my city but close, up to 50 km

A farther city but from the same province

Different province, but at least the country matches

Even the country doesn’t match

## Summary

Determining location by IP (excluding one faulty service of this type) did not show drastically lesser effectiveness than the browser's Geolocation API. For this reason, it is certainly an option worth considering as it doesn’t require additional interactions from users. However, in both approaches, there can be cases where they are off by tens of kilometers. Therefore, regardless of the mechanism, in the UI design of the application, it is always necessary to provide a clear presentation of geolocation results.
