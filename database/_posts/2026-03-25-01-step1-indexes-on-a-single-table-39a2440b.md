---
layout: post
title: "01. Step1 - Indexes on a single table"
date: 2026-03-25 12:35:00 +0000
categories: [database]
tags: [database, booking-system, indexes]
permalink: /database/01-step1-indexes-on-a-single-table-39a2440b/
source_note: "study plan/Arc1 - Booking System/Part2 - Indexes/01. Step1 - Indexes on a single table.md"
---

[Database]({{ '/database/' | relative_url }}) / Study archive
# **Index & Planner Lab**


## **Setup**


### **docker-compose.yml**

```
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

### **Folder structure**

```
index-lab/
├─ docker-compose.yml
└─ init/
   ├─ 01_orders_schema.sql
   ├─ 02_orders_seed.sql
   ├─ 03_join_schema.sql
   └─ 04_join_seed.sql
```

### **Run**

```
docker compose up -d
docker exec -it pg-index-lab psql -U labuser -d indexlab
```

---

## **Topic 1. What indexes really do**

  

Indexes improve **access path**. They are not magic acceleration.

  

### **Key points**

- good when query shape matches index structure
    
- good for equality, range, sorting, pagination when aligned well
    
- weak if DB still has to fetch many heap rows
    
- more indexes slow writes
    

  

### **Related Q&A**

  

**Q. Do indexes affect UPDATE / INSERT too?**

- Yes.
    
- INSERT: must also write index entries
    
- UPDATE: may use indexes to find rows and may also update index entries
    
- DELETE: must remove index entries too
    

---

## **Topic 2. Selectivity, cardinality, and weak indexes**

  

A low-cardinality column often makes a weak standalone index.

  

### **Key points**

- **cardinality** = number of distinct values
    
- **selectivity** = how much a predicate reduces rows
    
- low cardinality often leads to low selectivity
    
- rare values can still be useful
    

  

### **Related quiz**

  

**Why is a standalone index on delete_yn often weak?**

- My answer: because it has only 'Y' or 'N', so the advantage is small.
    
- Refined answer: because the predicate usually matches too many rows, so index access may be less attractive than a scan.
    

---

## **Topic 3. Composite indexes**

  

Composite index order should follow the **access pattern**, not the text order of SQL clauses.

  

### **Key points**

- (A, B) is usually good for A and A + B
    
- (A, B) is usually weak for B alone
    
- design by equality, range, and order pattern
    

  

### **Related quiz**

  

**Which is better for recent orders of one customer?**

- (customer_id, created_at)
    
- (created_at, customer_id)
    

  

My answer: (customer_id, created_at).

  

Refined answer: correct, because the query first narrows by customer_id, then wants rows ordered by created_at.

---

## **Topic 4.** 

## **ORDER BY ... LIMIT**

##  **and early stop**

  

A matching ordered index becomes much more valuable with LIMIT.

  

### **Key points**

- without LIMIT, DB may still need all matching rows
    
- with LIMIT, DB may stop early
    
- this is one of the strongest practical index wins
    

  

### **Related quiz**

  

**Why is ORDER BY ... LIMIT 100 often much faster with a matching index than plain ORDER BY?**

- My answer: because without LIMIT it brings all matching rows anyway.
    
- Refined answer: correct. The main gain is early stop.
    

---

## **Topic 5.** 

## **SELECT ***

##  **and heap fetches**

  

Even if the index finds the right rows, the DB may still need heap/table access for missing columns.

  

### **Key points**

- index locates rows
    
- heap/table fetch gets full row
    
- SELECT * often weakens index benefit
    
- narrower select list can be cheaper
    

  

### **Related quiz**

  

**Why does SELECT * often weaken index benefit?**

- My answer: because DB still has to go to the heap to fetch non-indexed columns.
    
- Refined answer: correct.
    

---

## **Topic 6. Aggregation and indexes**

  

Indexes do not usually compute SUM() directly.

  

### **Key points**

- index helps find qualifying rows faster
    
- grouping may be hash aggregate or sort aggregate
    
- for large analytics, row-store DBs are weaker than columnar systems
    
- at scale, summary tables/materialized views may be better
    

  

### **Related Q&A**

  

**How does aggregate work with index?**

- The index mainly helps row access, not the arithmetic itself.
    

---

## **Topic 7. Window functions and indexes**

  

Indexes can help if they align with PARTITION BY and ORDER BY.

  

### **Key points**

- index can reduce sorting cost
    
- index can feed rows in useful order
    
- window functions still require real computation over rows
    

  

### **Related correction**

  

Instead of:

```
SUM(amount) OVER (customer_id)
```

use:

```
SUM(amount) OVER (PARTITION BY customer_id)
```

---

## **Topic 8. Reading execution plans**

  

Important scan/access nodes:

- Seq Scan
    
- Parallel Seq Scan
    
- Index Scan
    
- Index Only Scan
    
- Bitmap Index Scan
    
- Bitmap Heap Scan
    

  

### **Key fields**

- cost=... → optimizer estimate, not milliseconds
    
- rows=... → estimated row count
    
- actual ... rows=... → actual row count
    
- loops=... → how many times node ran
    
- Index Cond → used inside access path
    
- Filter → applied after rows reached the node
    

  

### **Related quiz**

  

**What is the practical difference between Index Cond and Filter?**

- My answer: index cond means index lookup is used; filter means filtering happens afterward.
    
- Refined answer: correct.
    

---

## **Topic 9. Why the optimizer may ignore an index**

  

Having an index does not mean it will be used.

  

### **Possible reasons**

- too many rows match
    
- full scan is cheaper
    
- sort is cheap enough
    
- stats say another plan is cheaper
    
- query still needs many heap fetches
    
- predicate does not align with index structure
    

  

### **Related quiz**

  

**Why can prod choose full scan while dev uses an index for the same SQL?**

- My answer: row count grows, data gets skewed, optimizer guesses differently.
    
- Refined answer: also include stale statistics, parameter differences, schema/index differences, and lock/contention effects.
    

---

## **Topic 10. Stage 1 join practice — before the index**

  

Query:

```
SELECT o.id, o.created_at, o.status, o.amount
FROM customers c
JOIN orders2 o ON o.customer_id = c.id
WHERE c.id = 1001
ORDER BY o.created_at DESC
LIMIT 20;
```

### **What happened**

- customers.id was already fine because it is PK
    
- PostgreSQL still scanned all of orders2
    
- it used Parallel Seq Scan on orders2
    
- then joined by nested loop
    
- sort was small
    
- real cost was scanning orders2
    

  

### **Related Q&A**

  

**Which side is already selective?**

- My answer: c.id = 1001
    

  

**Why is customers.id already fine?**

- My answer: because it is the primary key
    

  

**What index is missing on orders2?**

- My answer: (customer_id, created_at DESC)
    

---

## **Topic 11. Stage 1 join practice — after the index**

  

Added:

```
CREATE INDEX idx_orders2_customer_created
    ON orders2 (customer_id, created_at DESC);
```

### **What changed**

- PostgreSQL started from customers
    
- then used the new index on orders2
    
- orders2 access became Bitmap Index Scan + Bitmap Heap Scan
    
- only a few heap blocks were touched
    
- sort was tiny
    
- execution time dropped sharply
    

  

### **Key lesson**

  

The real win was the access path change on orders2, not the join method itself.

  

### **My interpretation**

1. PostgreSQL starts from customers using PK index only scan
    
2. then uses bitmap index scan on orders2
    
3. then bitmap heap scan fetches rows
    
4. both tables use index-assisted paths
    
5. then sort and limit
    

  

### **Clarification**

  

There can still be a Sort even if the index includes created_at DESC, because a **bitmap path does not preserve order** like a plain Index Scan.

---

## **Topic 12. Join indexing**

  

For joins, think separately about:

- join keys
    
- filter keys
    
- sort keys
    

  

Do not assume SQL text order controls execution order.

  

### **Example idea**

  

On customers, (grade, id) is more natural than (id, grade) for:

```
WHERE c.grade = 'VIP'
```

because grade is the filter.

  

### **Related Q&A**

  

**Should I separate join key indexes from filter-key indexes?**

- Often yes.
    
- One composite index can sometimes serve both, but do not force it blindly.
    

  

**Can we not specify the join order because the DB compares row reduction possibilities?**

- Yes, generally the optimizer chooses join order based on estimated cost and selectivity.
    

---

## **Short review quiz**

1. Why did adding orders2(customer_id, created_at DESC) improve the Stage 1 join so much?
    
2. Why can a plan still sort even if the index has the same order as ORDER BY?
    
3. What is the practical difference between Index Cond and Filter?
    
4. Why is delete_yn often a weak standalone index?
    
5. Why does LIMIT often make an ordered composite index much more valuable?
