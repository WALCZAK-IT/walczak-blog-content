---
title: "PostgreSQL na Kubernetes: porównanie operatorów i testy wydajności"
slug: "postgresql-na-kubernetes-porownanie-operatorow"
publicationDate: "2022-09-15"
tags:
  - "PostgreSQL"
  - "Kubernetes"
  - "CloudNativePG"
  - "Cloud SQL"
  - "operators"
  - "pgbench"
coverImage: ""
brief: "Porównuję operatory PostgreSQL dla Kubernetes z Google Cloud SQL, zwracając uwagę na replikację, backupy, rozszerzenia i wygodę utrzymania. Na końcu zestawiam wydajność CloudNativePG i Cloud SQL w teście pgbench."
---

Uruchomienie PostgreSQL na Kubernetes daje dużą kontrolę nad konfiguracją, przechowywaniem danych i sposobem wdrażania. Jednocześnie oznacza, że część odpowiedzialności za wysoką dostępność, backupy i aktualizacje pozostaje po stronie zespołu. Operator Kubernetes może tę pracę znacznie uprościć, ale poszczególne projekty różnią się zakresem funkcji, jakością dokumentacji i dojrzałością.

W tym artykule porównuję kilka operatorów PostgreSQL oraz Google Cloud SQL jako zarządzaną alternatywę. Najpierw sprawdzam funkcje ważne w codziennej pracy, a następnie porównuję wydajność wybranego rozwiązania — CloudNativePG — z Cloud SQL w prostym teście `pgbench`.

## Zakres porównania

Porównuję następujące rozwiązania:

- **KubeDB**,
- **Percona Operator for PostgreSQL**,
- [**CloudNativePG**](https://cloudnative-pg.io/),
- **Zalando Postgres Operator**,
- [**Kubegres**](https://www.kubegres.io/).
- **Google Cloud SQL**,

Oceniam przede wszystkim koszt licencji, dojrzałość projektu, obsługę replik i backupów, możliwość zmiany konfiguracji oraz dostępność rozszerzeń PostgreSQL. Symbole w dalszej części artykułu oznaczają: ✅ dobre lub pełne wsparcie, ⚠️ wsparcie częściowe albo wymagające dodatkowej weryfikacji, ❌ brak funkcji lub istotny problem.

## Najważniejsze różnice

### Koszt i model utrzymania

- **KubeDB** — ⚠️ podstawowe funkcje są dostępne w wersji open source, natomiast bardziej zaawansowane możliwości wymagają wersji płatnej.
- **Percona Operator**, **CloudNativePG**, **Zalando Operator** i **Kubegres** — ✅ podstawowy zakres funkcji jest dostępny jako open source.
- **Google Cloud SQL** — ⚠️ płacimy za zarządzaną usługę i przy porównywalnej liczbie vCPU oraz pamięci koszt jest mniej więcej dwukrotnie wyższy niż w przypadku samodzielnych maszyn wirtualnych. W analizowanej konfiguracji nie ma odpowiednika hot standby dostępnego bez dodatkowej instancji, więc HA z repliką odczytową wymagało co najmniej trzech instancji: primary, standby i read replica.

W przypadku operatorów trzeba doliczyć koszt utrzymania klastra, storage'u, backupów oraz pracy zespołu. Z kolei Cloud SQL ogranicza zakres obowiązków operacyjnych, ale zmniejsza kontrolę nad środowiskiem i może być droższy przy większej liczbie instancji.

### Dojrzałość i zaufanie do projektu

To kryterium jest częściowo subiektywne. Uwzględniam zarówno własny research, jak i aktywność projektu oraz opinie użytkowników dostępne w czasie analizy.

- **KubeDB** — ❌ w poprzednim researchu znaleźliśmy rozbieżności między materiałami marketingowymi a faktycznymi możliwościami operatora. Wątpliwości budziła również niewielka skala zespołu utrzymującego projekt. Podobne uwagi pojawiały się w [opiniach zewnętrznych](https://blog.flant.com/comparing-kubernetes-operators-for-postgresql/#comment-5415639120).
- **Percona Operator** — ✅ Percona ma dobre [opinie jako dostawca konsultingu i usług związanych z bazami danych](https://www.gartner.com/reviews/market/data-and-analytics-others/vendor/percona/reviews?marketSeoName=data-and-analytics-others&vendorSeoName=percona).
- **CloudNativePG** — ⚠️ projekt rozwijany przez [EDB](https://www.enterprisedb.com/), firmę z wieloletnim doświadczeniem w PostgreSQL. W czasie analizy repozytorium było jeszcze młode, ale aktywnie rozwijane.
- **Google Cloud SQL** — ✅ zarządzana usługa używana przez wiele firm, z odpowiedzialnością za infrastrukturę przeniesioną na Google.
- **Zalando Operator** — ⚠️ często opisywany jako [production ready](https://www.reddit.com/r/kubernetes/comments/wmz684/is_anyone_using_postgres_on_kubernetes/), choć część konfiguracji nadal odzwierciedla potrzeby Zalando i może wymagać dostosowania.
- **Kubegres** — ❌ w 2022 roku brakowało nowych wydań, a aktywność projektu sugerowała [bardzo mały zespół](https://github.com/reactive-tech/kubegres/issues/126).

### Repliki odczytowe

- **Percona Operator** — ⚠️ dokumentacja sugerowała użycie PgBouncera i trudno było znaleźć kompletny przykład połączenia aplikacji z repliką odczytową; dostępna była jedynie [wzmianka na blogu](https://www.percona.com/blog/2018/10/02/scaling-postgresql-using-connection-poolers-and-load-balancers-for-an-enterprise-grade-environment/#comment-10971387).
- **CloudNativePG** — ✅ operator tworzy osobne [serwisy Kubernetes dla primary i replik](https://cloudnative-pg.io/documentation/1.17/applications/). Nie trzeba w tym celu dodawać PgBouncera — pooling może pozostać po stronie aplikacji.
- **Google Cloud SQL** — ⚠️ dokumentacja [replik read-only](https://cloud.google.com/sql/docs/postgres/replication#read-replicas) potwierdza taką możliwość, ale nie pokazuje szczegółowo sposobu integracji. Samo [połączenie z Kubernetes do Cloud SQL](https://cloud.google.com/sql/docs/postgres/connect-kubernetes-engine) wymaga dodatkowej konfiguracji.

### Replikacja, backupy i zmiana rozmiaru

- **Szybkie dodawanie replik — CloudNativePG:** ✅ nowa replika może odtworzyć dane z backupu WAL, a następnie pobrać najnowsze zmiany ze streamingu.
- **Backup z Point-in-Time Recovery — CloudNativePG:** ✅ mechanizm oparty na [Barman](https://docs.pgbarman.org/release/3.0.1/).
- **Rozszerzanie dysku — CloudNativePG:** ✅ wspierane zgodnie z [dokumentacją](https://cloudnative-pg.io/documentation/1.17/storage/#volume-expansion).

### Rozszerzenia i własna konfiguracja PostgreSQL

- `pg_trgm` i `unaccent`:
  - **CloudNativePG** — ✅ udało się wykonać `CREATE EXTENSION` dla obu rozszerzeń.
  - **Google Cloud SQL** — ✅ oba rozszerzenia znajdują się na liście [wspieranych rozszerzeń](https://cloud.google.com/sql/docs/postgres/extensions#postgresql-extensions-supported-by-cloud-sql).
- Własne słowniki do full-text search:
  - **CloudNativePG** — ⚠️ nie znalazłem gotowej instrukcji, ale prawdopodobnym rozwiązaniem jest własny obraz Dockera bazujący na `ghcr.io/cloudnative-pg/postgresql`.
  - **Google Cloud SQL** — ❌ według [opisu zgłoszenia](https://issuetracker.google.com/issues/65624669) nie ma możliwości wgrania własnych słowników.

## Werdykt z porównania funkcji

Na podstawie funkcji, dokumentacji i zachowania podczas testów wybrałbym **CloudNativePG**. Najważniejsze argumenty to:

- pełny zakres podstawowych funkcji dostępny jako open source, z możliwością skorzystania ze wsparcia komercyjnego,
- najlepsza dokumentacja spośród porównywanych operatorów,
- stabilne zachowanie w testowanym scenariuszu,
- możliwość przygotowania własnego obrazu PostgreSQL, na przykład z dodatkowymi słownikami,
- możliwość używania osobnych serwisów Kubernetes dla primary i replik odczytowych.

Cloud SQL pozostaje rozsądnym wyborem, jeśli najważniejsze jest ograniczenie obowiązków związanych z utrzymaniem bazy. W zamian trzeba zaakceptować wyższy koszt, mniejszą kontrolę nad systemem oraz ograniczenia usługi zarządzanej.

## Test wydajności: CloudNativePG kontra Cloud SQL

### Konfiguracja

#### Cloud SQL

W teście wykorzystano instancję Cloud SQL o następujących parametrach:

- region: `europe-central2` (Warszawa),
- silnik: PostgreSQL 14.4,
- maszyna: 4 vCPU i 26 GB pamięci,
- miejsce na dane: 100 GB, z włączonym automatycznym zwiększaniem rozmiaru,
- przepustowość sieci: 1000 z 2000 MB/s,
- przepustowość dysku: odczyt 48 z 240 MB/s, zapis 48 z 240 MB/s,
- IOPS: odczyt 3000 z 15 000, zapis 3000 z 15 000,
- połączenia: publiczny adres IP, bez prywatnego adresu IP,
- dozwolone sieci: `0.0.0.0/0`, czyli dowolny adres IPv4 — ustawienie akceptowalne wyłącznie w izolowanym teście, nie w środowisku produkcyjnym,
- backup: automatyczny,
- dostępność: wiele stref (High Availability),
- odzyskiwanie do określonego momentu (PITR): włączone,
- maksymalna liczba połączeń: 500.

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
  username: YWRtaW4=
  password: c2VydGcyMzQ1
kind: Secret
metadata:
  name: demo-user-secret
type: kubernetes.io/basic-auth
```

W obu wolumenach użyto klasy `premium-rwo`, czyli klasy szybkich dysków CSI w GCP. Manifest zawiera również przykładowy sekret z danymi użytkownika; wartości pokazane w artykule są testowe i nie powinny być używane w prawdziwym środowisku.

### Metodyka

Do uruchomienia `pgbench` utworzono osobny pod w tym samym klastrze Kubernetes:

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

Następnie dwukrotnie wykonano inicjalizację danych poleceniem:

```bash
pgbench -i --host={host} --scale=100 --user=demo demo
```

Do porównania wykorzystano wyniki drugiego uruchomienia, aby ograniczyć wpływ rozgrzewania środowiska i cache'y. Jest to prosty test obciążenia inicjalizacyjnego, a nie pełny benchmark produkcyjnej bazy — nie mierzy na przykład opóźnień zapytań aplikacji przy równoległym ruchu.

### Rezultaty

| Etap | Cloud SQL | Cloud SQL* | CloudNativePG |
| --- | :---: | :---: | :---: |
| Całość | 69,53 s | 41,13 s | 36,46 s |
| Usuwanie tabel | 0,30 s | 0,30 s | 0,31 s |
| Tworzenie tabel | 0,01 s | 0,01 s | 0,01 s |
| Generowanie danych po stronie klienta | 24,49 s | 15,50 s | 14,81 s |
| `VACUUM` | 36,11 s | 20,30 s | 16,60 s |
| Klucze główne | 8,62 s | 5,03 s | 4,73 s |

\* W drugim pomiarze Cloud SQL zmieniono konfigurację na jednostrefową: usunięto standby w innej strefie, pozostawiając replikę w tej samej strefie.

### Wnioski z testu

W tej konkretnej konfiguracji CloudNativePG zakończył inicjalizację szybciej niż Cloud SQL. Różnica była widoczna również po zmianie Cloud SQL na wariant jednostrefowy, choć wtedy wynik Cloud SQL wyraźnie się poprawił. Z perspektywy aplikacji działającej w klastrze Kubernetes PostgreSQL uruchomiony przez CloudNativePG okazał się więc co najmniej tak wydajny jak zarządzana usługa.

Nie oznacza to, że Kubernetes zawsze zapewni lepszą wydajność. Na wynik wpływają między innymi typ dysku, topologia stref, konfiguracja replikacji, parametry PostgreSQL i odległość klienta od bazy. Test pokazuje przede wszystkim, że koszt wygody oferowanej przez Cloud SQL nie musi oznaczać wyższej wydajności.

W praktyce decyzję warto podjąć w tej kolejności: najpierw określić wymagania dotyczące dostępności i odpowiedzialności operacyjnej, następnie wybrać model utrzymania, a dopiero na końcu porównywać wyniki benchmarków dla własnego obciążenia.
