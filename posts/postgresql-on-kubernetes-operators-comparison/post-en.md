---
title: "PostgreSQL on Kubernetes: operator comparison and performance tests"
slug: "postgresql-on-kubernetes-operators-comparison"
publicationDate: "2022-09-15"
tags:
  - "PostgreSQL"
  - "Kubernetes"
  - "CloudNativePG"
  - "Cloud SQL"
  - "operators"
  - "pgbench"
coverImage: ""
brief: "I compare PostgreSQL operators for Kubernetes with Google Cloud SQL, focusing on replication, backups, extensions, and operational effort. Finally, I compare CloudNativePG and Cloud SQL performance in a pgbench test."
---

## Introduction

Running PostgreSQL on Kubernetes provides extensive control over configuration, data storage, and deployment. At the same time, it means that part of the responsibility for high availability, backups, and upgrades remains with the team. A Kubernetes operator can simplify this work considerably, but individual projects differ in functionality, documentation quality, and maturity.

In this article, I compare several PostgreSQL operators with Google Cloud SQL as a managed alternative. First, I review features that matter in day-to-day operations. Then I compare the performance of the selected solution — CloudNativePG — with Cloud SQL in a simple `pgbench` test.

The comparison and tests described below were conducted in September 2022. Projects and cloud services change constantly, so these conclusions should be treated as the result of the documentation and configuration available at that time, rather than as a timeless ranking.

## Scope of the comparison

The following solutions are compared:

- **KubeDB**,
- **Percona Operator for PostgreSQL**,
- [**CloudNativePG**](https://cloudnative-pg.io/),
- **Google Cloud SQL**,
- **Zalando Postgres Operator**,
- [**Kubegres**](https://www.kubegres.io/).

The main criteria are licensing cost, project maturity, replication and backup support, configuration flexibility, and PostgreSQL extension availability. The symbols used below mean: ✅ good or complete support, ⚠️ partial support or functionality requiring additional verification, and ❌ missing functionality or a significant problem.

## Key differences

### Cost and operational model

- **KubeDB** — ⚠️ basic functionality is available in the open-source version, while more advanced features require the paid version.
- **Percona Operator**, **CloudNativePG**, **Zalando Operator**, and **Kubegres** — ✅ the basic feature set is available as open source.
- **Google Cloud SQL** — ⚠️ the managed service is billed for its resources, and with a comparable number of vCPUs and amount of memory it costs roughly twice as much as self-managed virtual machines. In the configuration analysed here, there was no hot standby equivalent available without an additional instance, so HA with a read replica required at least three instances: primary, standby, and read replica.

For operators, the cost of maintaining the cluster, storage, backups, and the team's work also has to be included. Cloud SQL reduces the operational workload, but provides less control over the environment and may be more expensive when multiple instances are required.

### Project maturity and trust

This criterion is partly subjective. It includes both my own research and the project's activity and user feedback available at the time of the analysis.

- **KubeDB** — ❌ in earlier research, we found discrepancies between the operator's marketing materials and its actual capabilities. The relatively small team maintaining the project was another concern. Similar comments appeared in [external reviews](https://blog.flant.com/comparing-kubernetes-operators-for-postgresql/#comment-5415639120).
- **Percona Operator** — ✅ Percona has good [reviews as a provider of database consulting and services](https://www.gartner.com/reviews/market/data-and-analytics-others/vendor/percona/reviews?marketSeoName=data-and-analytics-others&vendorSeoName=percona).
- **CloudNativePG** — ⚠️ the project was developed by [EDB](https://www.enterprisedb.com/), a company with many years of PostgreSQL experience. At the time of the analysis, the repository was still young but actively developed.
- **Google Cloud SQL** — ✅ a managed service used by many companies, with Google taking responsibility for the infrastructure.
- **Zalando Operator** — ⚠️ often described as [production ready](https://www.reddit.com/r/kubernetes/comments/wmz684/is_anyone_using_postgres_on_kubernetes/), although some of its configuration still reflects Zalando's needs and may require adaptation.
- **Kubegres** — ❌ in 2022, there had been no new releases for some time, and the project's activity suggested a [very small team](https://github.com/reactive-tech/kubegres/issues/126).

### Read replicas

- **Percona Operator** — ⚠️ the documentation suggested using PgBouncer, and it was difficult to find a complete example of connecting an application to a read replica; only [a mention in a blog post](https://www.percona.com/blog/2018/10/02/scaling-postgresql-using-connection-poolers-and-load-balancers-for-an-enterprise-grade-environment/#comment-10971387) was available.
- **CloudNativePG** — ✅ the operator creates separate [Kubernetes services for the primary and replicas](https://cloudnative-pg.io/documentation/1.17/applications/). PgBouncer is not required for this — pooling can remain on the application side.
- **Google Cloud SQL** — ⚠️ the documentation for [read replicas](https://cloud.google.com/sql/docs/postgres/replication#read-replicas) confirms that this is possible, but does not describe the integration in detail. [Connecting Kubernetes to Cloud SQL](https://cloud.google.com/sql/docs/postgres/connect-kubernetes-engine) itself requires additional configuration.

### Replication, backups, and resizing

- **Quickly adding replicas — CloudNativePG:** ✅ a new replica can restore data from a WAL backup and then fetch the latest changes through streaming replication.
- **Point-in-Time Recovery backup — CloudNativePG:** ✅ based on [Barman](https://docs.pgbarman.org/release/3.0.1/).
- **Disk expansion — CloudNativePG:** ✅ supported according to the [documentation](https://cloudnative-pg.io/documentation/1.17/storage/#volume-expansion).

### Extensions and custom PostgreSQL configuration

- `pg_trgm` and `unaccent`:
  - **CloudNativePG** — ✅ I was able to run `CREATE EXTENSION` for both extensions.
  - **Google Cloud SQL** — ✅ both extensions are included in the list of [supported extensions](https://cloud.google.com/sql/docs/postgres/extensions#postgresql-extensions-supported-by-cloud-sql).
- Custom full-text search dictionaries:
  - **CloudNativePG** — ⚠️ I could not find ready-made instructions, but a probable solution is to create a custom Docker image based on `ghcr.io/cloudnative-pg/postgresql`.
  - **Google Cloud SQL** — ❌ according to the [issue description](https://issuetracker.google.com/issues/65624669), uploading custom dictionaries is not possible.

## Verdict based on the feature comparison

Based on the features, documentation, and behaviour during testing, I would choose **CloudNativePG**. The main reasons are:

- the complete basic feature set is available as open source, with the option of commercial support,
- the best documentation among the compared operators,
- stable behaviour in the tested scenario,
- the ability to prepare a custom PostgreSQL image, for example with additional dictionaries,
- the ability to use separate Kubernetes services for the primary and read replicas.

Cloud SQL remains a sensible choice when reducing database maintenance responsibilities is the top priority. In exchange, you have to accept a higher cost, less control over the system, and the limitations of a managed service.

## Performance test: CloudNativePG versus Cloud SQL

### Configuration

#### Cloud SQL

The test used a Cloud SQL instance with the following parameters:

- region: `europe-central2` (Warsaw),
- engine: PostgreSQL 14.4,
- machine: 4 vCPUs and 26 GB of memory,
- data storage: 100 GB, with automatic storage increase enabled,
- network throughput: 1000 out of 2000 MB/s,
- disk throughput: read 48 out of 240 MB/s, write 48 out of 240 MB/s,
- IOPS: read 3000 out of 15,000, write 3000 out of 15,000,
- connections: public IP address, without a private IP address,
- authorized networks: `0.0.0.0/0`, meaning any IPv4 address — acceptable only in an isolated test, not in production,
- backups: automatic,
- availability: multiple zones (High Availability),
- point-in-time recovery (PITR): enabled,
- maximum number of connections: 500.

#### CloudNativePG

```yaml
# helm chart installed using https://github.com/cloudnative-pg/charts
# Example of PostgreSQL cluster
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-example
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:14.5-4
  instances: 2
  # superuserSecret:
  #   name: superuser-secret
  bootstrap:
    initdb:
      database: demo
      owner: demo
      secret:
        name: demo-user-secret
  # Example of rolling update strategy:
  # - unsupervised: automated update of the primary once all
  #                 replicas have been upgraded (default)
  # - supervised: requires manual supervision to perform
  #               the switchover of the primary
  primaryUpdateStrategy: unsupervised
  postgresql:
    parameters:
      max_connections: "310"
      shared_buffers: "7GB"
      maintenance_work_mem: "1GB"
  resources:
    requests:
      memory: "26Gi"
      cpu: 4
    limits:
      memory: "26Gi"
      cpu: 4
  storage:
    size: 100Gi
    # GCP class for fast CSI SSD disks
    storageClass: premium-rwo
  walStorage:
    size: 100Gi
    # GCP class for fast CSI SSD disks
    storageClass: premium-rwo
---
apiVersion: v1
data:
  username: ZGVtbw==
  password: c29tZS1zZWNyZXQ=
kind: Secret
metadata:
  name: demo-user-secret
type: kubernetes.io/basic-auth
```

Both volumes use the `premium-rwo` class, which is the class for fast CSI disks in GCP. The manifest also contains an example secret with user credentials; the values shown in the article are for testing and must not be used in a real environment.

### Methodology

A separate pod was created in the same Kubernetes cluster to run `pgbench`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: manipulator
spec:
  containers:
    - name: manipulator
      image: postgres:14.5
      env:
        - name: PGDATA
          value: /work/data
        - name: POSTGRES_PASSWORD
          value: manipulator-secret
      resources:
        requests:
          cpu: "1"
          memory: "3Gi"
```

The data was then initialized twice using the following command:

```bash
pgbench -i --host={host} --scale=100 --user=demo demo
```

The second run was used for comparison to reduce the impact of warming up the environment and caches. This is a simple initialization workload test, not a complete production database benchmark — for example, it does not measure application query latency under concurrent traffic.

### Results

| Stage | Cloud SQL | Cloud SQL* | CloudNativePG |
| --- | :---: | :---: | :---: |
| Total | 69.53 s | 41.13 s | 36.46 s |
| Drop tables | 0.30 s | 0.30 s | 0.31 s |
| Create tables | 0.01 s | 0.01 s | 0.01 s |
| Client-side data generation | 24.49 s | 15.50 s | 14.81 s |
| `VACUUM` | 36.11 s | 20.30 s | 16.60 s |
| Primary keys | 8.62 s | 5.03 s | 4.73 s |

\* In the second Cloud SQL measurement, the configuration was changed to a single-zone setup: the standby in another zone was removed, while a replica in the same zone was retained.

### Test conclusions

In this specific configuration, CloudNativePG completed the initialization faster than Cloud SQL. The difference was also visible after Cloud SQL was changed to a single-zone variant, although the Cloud SQL result improved significantly. From the perspective of an application running in the Kubernetes cluster, PostgreSQL running through CloudNativePG was therefore at least as fast as the managed service.

This does not mean that Kubernetes will always provide better performance. The result depends on factors such as disk type, zone topology, replication configuration, PostgreSQL parameters, and the distance between the client and the database. The test mainly shows that the convenience offered by Cloud SQL does not necessarily come with higher performance.

In practice, the decision should be made in this order: first define the availability requirements and operational responsibilities, then choose the operating model, and only afterwards compare benchmark results for your own workload.
