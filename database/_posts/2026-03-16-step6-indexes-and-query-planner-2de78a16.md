---
layout: post
title: "Step6 - Indexes And Query Planner"
date: 2026-03-16 12:18:46 +0000
categories: [database]
tags: [database, booking-system, concurrency, indexes, queries]
permalink: /database/step6-indexes-and-query-planner-2de78a16/
source_note: "study plan/Arc1 - Booking System/Part1 - Transaction. MVCC. Lock/Step6 - Indexes And Query Planner.md"
---

[Database]({{ '/database/' | relative_url }}) / Study archive
# Prep

## 1. Structure
```code
index-lab/
├─ docker-compose.yml
└─ init/
   ├─ 01_schema.sql
   └─ 02_seed.sql
```

---
## 2. docker-compose.yml
```yaml
version: "3.8"

services:
  pg-index-lab:
    image: postgres:16
    container_name: pg-index-lab
    restart: unless-stopped
    environment:
      POSTGRES_DB: indexlab
      POSTGRES_USER: labuser
      POSTGRES_PASSWORD: labpass
    ports:
      - "5432:5432"
    volumes:
      - pg_index_lab_data:/var/lib/postgresql/data
      - ./init:/docker-entrypoint-initdb.d

volumes:
  pg_index_lab_data:
```


## 3. 01_init.sql

Check out where indexes are given.
```sql
CREATE TABLE orders (
    id BIGINT PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    status VARCHAR(20) NOT NULL,
    delete_yn CHAR(1) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    amount NUMERIC(10,2) NOT NULL
);

CREATE INDEX idx_orders_customer_created
    ON orders (customer_id, created_at DESC);

CREATE INDEX idx_orders_status
    ON orders (status);

CREATE INDEX idx_orders_delete_yn
    ON orders (delete_yn);

CREATE INDEX idx_orders_created_at
    ON orders (created_at DESC);
```

## 4. 02_seed.sql

This will insert 500,000 random orders. 

```sql
INSERT INTO orders (
    id,
    customer_id,
    status,
    delete_yn,
    created_at,
    amount
)
SELECT
    gs AS id,
    (random() * 50000)::BIGINT + 1 AS customer_id,
    CASE
        WHEN random() < 0.70 THEN 'CREATED'
        WHEN random() < 0.90 THEN 'CONFIRMED'
        WHEN random() < 0.98 THEN 'SHIPPED'
        ELSE 'CANCELLED'
    END AS status,
    CASE
        WHEN random() < 0.95 THEN 'N'
        ELSE 'Y'
    END AS delete_yn,
    TIMESTAMP '2024-01-01'
        + ((random() * 730)::INT || ' days')::INTERVAL
        + ((random() * 86400)::INT || ' seconds')::INTERVAL AS created_at,
    ROUND((random() * 100000)::NUMERIC, 2) AS amount
FROM generate_series(1, 500000) gs;

ANALYZE orders;
```
