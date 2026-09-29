---
layout: post
title: "05. Step1 - Stage 4 join in_ordering_pagination_wrapup"
date: 2026-04-06 13:40:44 +0000
categories: [database]
tags: [database, booking-system, indexes]
permalink: /database/05-step1-stage-4-join-in-ordering-pagination-wrapup-ff28754b/
source_note: "study plan/Arc1 - Booking System/Part2 - Indexes/05. Step1 - Stage 4 join in_ordering_pagination_wrapup.md"
---

[Database]({{ '/database/' | relative_url }}) / Study archive
# Stage 4 — Join + Ordering + Pagination Wrap-up

## Query
```sql
EXPLAIN ANALYZE
SELECT c.id, c.name, o.id, o.created_at, o.status
FROM customers c
JOIN orders2 o ON o.customer_id = c.id
WHERE c.grade = 'VIP'
ORDER BY o.created_at DESC
LIMIT 100;
```

---

## 1. Prediction before running
### My answers
1. `(grade, id)` on `customers` is more likely to be useful immediately because it reduces rows first.
2. The main risk is sorting too many joined rows.
3. `LIMIT 100` will help only after a lot of work is already done if PostgreSQL must first join many rows.

### Refined understanding
- The customer-side filter is real and selective enough to matter.
- The main danger in this query is **join first, sort later**.
- `LIMIT` is only truly powerful if the planner can use it **before** doing most of the heavy work.

---

## 2. Plan before adding new indexes
### Main shape
- `Seq Scan` on `customers`
- filter `grade = 'VIP'`
- build `Hash`
- `Parallel Seq Scan` on `orders2`
- `Hash Join`
- `Sort` by `o.created_at DESC`
- `Gather Merge`
- `Limit`

### What I observed
- PostgreSQL reduced `customers` first
- then scanned all of `orders2`
- then joined them by hash join
- then used `top-N heapsort`
- then merged worker results and returned 100 rows

### What I learned
This is still a broad plan:
- orders are scanned broadly
- joined rows are produced broadly
- `LIMIT 100` helps the sorting stage, but only after a lot of join work

---

## 3. Why `(grade, id)` can make sense
### My question
Why include `id` in `(grade, id)` if `id` is already the PK?

### Answer
Because a composite index is one ordered structure:
- first by `grade`
- then by `id`

That means:
- `grade` reduces rows
- `id` is immediately available in the same structure for joining

### Practical note
For some queries, just `(grade)` may also help.  
But `(grade, id)` is reasonable when rows filtered by grade are then joined by `id`.

---

## 4. Composite index vs separate single-column indexes
### My question
Do several single-column indexes work almost the same as one composite index?

### Answer
No, not usually.

### Why
Two single indexes:
- help separate predicates separately

One composite index:
- stores the combined ordering/access path

Example:
```sql
WHERE status = 'CONFIRMED'
  AND created_at >= '2025-01-01'
ORDER BY created_at DESC
```

- separate indexes on `status` and `created_at` are not the same as
- one composite index on `(status, created_at DESC)`

### Main lesson
Composite indexes are about **combined access pattern**, not just indexed columns.

---

## 5. About `IS NOT NULL` in composite indexes
### My question
Can `IS NOT NULL` be part of a composite index?

Example:
```sql
SELECT *
FROM tableA
WHERE product_code IS NOT NULL
  AND status = 'ON_SALE'
  AND created_at >= ...
```

### My index idea
```sql
(product_code, status, created_at)
```

### Refined answer
Yes, it can be part of a composite index, but whether it should be the **leading** column depends on selectivity.

If most rows already have `product_code IS NOT NULL`, then leading with `product_code` is usually weak.

More natural candidates may be:
```sql
(status, created_at)
```
or
```sql
(status, created_at, product_code)
```

### Main lesson
For predicates like `IS NOT NULL`, ask:
- how many rows does it really eliminate?

If not many, it is usually weak as the leading column.

---

## 6. Plan after adding `idx_customers_grade_id`
### Index
```sql
CREATE INDEX idx_customers_grade_id
    ON customers (grade, id);
```

### What changed
- `customers` access improved from `Seq Scan` to:
  - `Bitmap Index Scan`
  - `Bitmap Heap Scan`

### What did not change
- PostgreSQL still used `Hash Join`
- `orders2` was still scanned broadly
- sorting pattern stayed essentially the same

### What I learned
Improving the customer filter side helped a bit, but the whole query still had the same broad shape:
- scan all orders
- hash join
- sort top-N after join

The result count on the customer side did not change because the index improved **access path**, not **logical filtering outcome**.

---

## 7. Plan after adding `idx_orders2_created_customer`
### Index
```sql
CREATE INDEX idx_orders2_created_customer
    ON orders2 (created_at DESC, customer_id);
```

### New plan shape
- `Index Scan` on `orders2` using `idx_orders2_created_customer`
- `Nested Loop`
- `Memoize`
- `Index Scan` on `customers_pkey`
- `Filter: grade = 'VIP'`
- `Limit`

### What changed
This was a structural plan change:
- no hash join
- no broad orders scan
- no explicit sort
- no gather merge

### Why it became much faster
PostgreSQL could now:
1. read orders already in `created_at DESC` order
2. check each order's customer by PK
3. apply the VIP filter during lookup
4. stop as soon as 100 qualifying rows were found

### Main lesson
This is an **order-driven early-stop plan**.  
It wins because `ORDER BY ... LIMIT` becomes useful very early, not after broad join work.

---

## 8. What `Memoize` means
### My question
What are these new keywords:
- `Memoize`
- `Cache Mode`
- `Hits`
- `Misses`
- `Evictions`
- `Overflows`

### Answer
`Memoize` means PostgreSQL caches repeated lookup results during nested-loop execution.

### In this plan
- outer rows come from `orders2`
- many rows may repeat the same `customer_id`
- instead of re-looking up the same customer every time, PostgreSQL caches the result

### Meaning of fields
- `Cache Key`: value used for cache lookup (`o.customer_id`)
- `Hits`: reused cached result
- `Misses`: had to do actual lookup
- `Evictions`: removed cached entries to free space
- `Overflows`: cache storage overflow event
- `Memory Usage`: memory used by memoization

### Main lesson
`Memoize` was helpful, but it was **not** the main reason for the huge speedup.  
The main reason was the ordered index scan on `orders2` plus early stop from `LIMIT`.

---

## 9. Main comparison of Stage 4 strategies
### Strategy A — filter customers first
- find VIP customers
- hash them
- scan all orders
- join
- sort joined rows
- limit

### Strategy B — read latest orders first
- scan orders in `created_at DESC` order
- lookup customer by PK
- filter VIP on the fly
- stop once 100 rows are found

### What I learned
For this query, **Strategy B clearly wins**.

### Why
Because the output requirement is strongly order-driven:
```sql
ORDER BY o.created_at DESC
LIMIT 100
```

An index aligned to that output order can avoid:
- broad order scan
- hash join
- large post-join sorting

---

## 10. Final understanding
A good summary of Stage 4 is:

> For joined pagination queries, an index aligned with the final output order can outperform a filter-first strategy. In this case, `(created_at DESC, customer_id)` on `orders2` allowed PostgreSQL to scan the newest orders first, check customer eligibility by PK lookup, and stop early after finding 100 VIP-customer rows. This removed the need for broad order scanning, hash join, and post-join sorting.
