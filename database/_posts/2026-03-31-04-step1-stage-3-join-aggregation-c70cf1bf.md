---
layout: post
title: "04. Step1 - Stage 3 join_aggregation"
date: 2026-03-31 12:51:41 +0000
categories: [database]
tags: [database, booking-system, indexes]
permalink: /database/04-step1-stage-3-join-aggregation-c70cf1bf/
source_note: "study plan/Arc1 - Booking System/Part2 - Indexes/04. Step1 - Stage 3 join_aggregation.md"
---

[Database]({{ '/database/' | relative_url }}) / Study archive
# Stage 3 — Join + Aggregation Wrap-up

## Query
```sql
EXPLAIN ANALYZE
SELECT p.category_id, SUM(oi.quantity * oi.unit_price) AS sales
FROM orders2 o
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id
WHERE o.status = 'CONFIRMED'
  AND o.created_at >= '2025-01-01'
GROUP BY p.category_id
ORDER BY p.category_id;
```

---

## Plan
before adding indexes
```
                                                                          QUERY PLAN                                                                              

---------------------------------------------------------------------------------------------------------------------------------------------------------------------

 Finalize GroupAggregate  (cost=31242.48..31255.79 rows=51 width=40) (actual time=161.073..163.756 rows=51 loops=1)

   Group Key: p.category_id

   ->  Gather Merge  (cost=31242.48..31254.39 rows=102 width=40) (actual time=161.067..163.702 rows=153 loops=1)

         Workers Planned: 2

         Workers Launched: 2

         ->  Sort  (cost=30242.46..30242.59 rows=51 width=40) (actual time=144.954..144.957 rows=51 loops=3)

               Sort Key: p.category_id

               Sort Method: quicksort  Memory: 30kB

               Worker 0:  Sort Method: quicksort  Memory: 30kB

               Worker 1:  Sort Method: quicksort  Memory: 30kB

               ->  Partial HashAggregate  (cost=30240.38..30241.01 rows=51 width=40) (actual time=144.907..144.918 rows=51 loops=3)

                     Group Key: p.category_id

                     Batches: 1  Memory Usage: 48kB

                     Worker 0:  Batches: 1  Memory Usage: 48kB

                     Worker 1:  Batches: 1  Memory Usage: 48kB

                     ->  Hash Join  (cost=8638.31..29281.26 rows=95912 width=20) (actual time=31.084..126.418 rows=76770 loops=3)

                           Hash Cond: (oi.product_id = p.id)

                           ->  Parallel Hash Join  (cost=8329.31..28719.95 rows=96075 width=20) (actual time=26.992..110.347 rows=76773 loops=3)

                                 Hash Cond: (oi.order_id = o.id)

                                 ->  Parallel Seq Scan on order_items oi  (cost=0.00..18750.00 rows=625000 width=28) (actual time=0.037..31.859 rows=500000 loops=3)

                                 ->  Parallel Hash  (cost=7929.00..7929.00 rows=32025 width=8) (actual time=26.382..26.382 rows=25568 loops=3)

                                       Buckets: 131072  Batches: 1  Memory Usage: 4096kB

                                       ->  Parallel Seq Scan on orders2 o  (cost=0.00..7929.00 rows=32025 width=8) (actual time=0.022..20.274 rows=25568 loops=3)

                                             Filter: ((created_at >= '2025-01-01 00:00:00'::timestamp without time zone) AND ((status)::text = 'CONFIRMED'::text))

                                             Rows Removed by Filter: 141098

                           ->  Hash  (cost=184.00..184.00 rows=10000 width=16) (actual time=4.044..4.044 rows=10000 loops=3)

                                 Buckets: 16384  Batches: 1  Memory Usage: 597kB

                                 ->  Seq Scan on products p  (cost=0.00..184.00 rows=10000 width=16) (actual time=0.019..1.530 rows=10000 loops=3)

 Planning Time: 0.700 ms

 Execution Time: 163.884 ms

(30 rows)

```

After adding indexes
```
QUERY PLAN                                                                                        

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

 Finalize GroupAggregate  (cost=30678.10..30691.40 rows=51 width=40) (actual time=171.082..173.642 rows=51 loops=1)

   Group Key: p.category_id

   ->  Gather Merge  (cost=30678.10..30690.00 rows=102 width=40) (actual time=171.074..173.585 rows=153 loops=1)

         Workers Planned: 2

         Workers Launched: 2

         ->  Sort  (cost=29678.07..29678.20 rows=51 width=40) (actual time=152.983..152.987 rows=51 loops=3)

               Sort Key: p.category_id

               Sort Method: quicksort  Memory: 30kB

               Worker 0:  Sort Method: quicksort  Memory: 30kB

               Worker 1:  Sort Method: quicksort  Memory: 30kB

               ->  Partial HashAggregate  (cost=29675.99..29676.63 rows=51 width=40) (actual time=152.945..152.960 rows=51 loops=3)

                     Group Key: p.category_id

                     Batches: 1  Memory Usage: 48kB

                     Worker 0:  Batches: 1  Memory Usage: 48kB

                     Worker 1:  Batches: 1  Memory Usage: 48kB

                     ->  Hash Join  (cost=8073.93..28716.87 rows=95912 width=20) (actual time=41.577..135.090 rows=76770 loops=3)

                           Hash Cond: (oi.product_id = p.id)

                           ->  Parallel Hash Join  (cost=7764.93..28155.56 rows=96075 width=20) (actual time=38.039..119.880 rows=76773 loops=3)

                                 Hash Cond: (oi.order_id = o.id)

                                 ->  Parallel Seq Scan on order_items oi  (cost=0.00..18750.00 rows=625000 width=28) (actual time=0.032..31.106 rows=500000 loops=3)

                                 ->  Parallel Hash  (cost=7364.61..7364.61 rows=32025 width=8) (actual time=37.644..37.645 rows=25568 loops=3)

                                       Buckets: 131072  Batches: 1  Memory Usage: 4064kB

                                       ->  Parallel Bitmap Heap Scan on orders2 o  (cost=2080.24..7364.61 rows=32025 width=8) (actual time=6.450..30.346 rows=25568 loops=3)

                                             Recheck Cond: (((status)::text = 'CONFIRMED'::text) AND (created_at >= '2025-01-01 00:00:00'::timestamp without time zone))

                                             Heap Blocks: exact=2190

                                             ->  Bitmap Index Scan on idx_orders2_status_created  (cost=0.00..2061.02 rows=76860 width=0) (actual time=18.155..18.155 rows=76705 loops=1)

                                                   Index Cond: (((status)::text = 'CONFIRMED'::text) AND (created_at >= '2025-01-01 00:00:00'::timestamp without time zone))

                           ->  Hash  (cost=184.00..184.00 rows=10000 width=16) (actual time=3.461..3.461 rows=10000 loops=3)

                                 Buckets: 16384  Batches: 1  Memory Usage: 597kB

                                 ->  Seq Scan on products p  (cost=0.00..184.00 rows=10000 width=16) (actual time=0.016..1.404 rows=10000 loops=3)

 Planning Time: 1.395 ms

 Execution Time: 173.729 ms

(32 rows)
```

## 1. Prediction before running
### My prediction
1. `orders2` will be reduced first because the query has a clear filter on it.
2. `order_items` and maybe `products` could contribute to row multiplication because they are not filtered and may be large.
3. `Hash Join` will likely be used between `orders2` and `order_items` because `order_items` is large.
4. `idx_products_category` will probably not be the star index for this query.

### Refined understanding
- `orders2` **is** the natural table to reduce first.
- The main row multiplication happens at **`orders2 -> order_items`**, because one order can have many items.
- `products` is mostly a lookup/enrichment join here, not the main multiplication source.
- `idx_products_category` is not the key index because `category_id` is used for **grouping**, not **filtering**. The join to `products` is on `p.id`, which is already supported by the primary key.

---

## 2. Plan shape before adding `idx_orders2_status_created`
### Main plan flow
- `Parallel Seq Scan` on `orders2`
- `Parallel Hash` built from filtered `orders2`
- `Parallel Seq Scan` on `order_items`
- `Parallel Hash Join` on `oi.order_id = o.id`
- `Seq Scan` on `products`
- `Hash` on `products`
- `Hash Join` on `oi.product_id = p.id`
- `Partial HashAggregate`
- `Sort`
- `Gather Merge`
- `Finalize GroupAggregate`

### What I observed
- PostgreSQL filtered `orders2` first conceptually, but by a **parallel sequential scan**
- it then built a hash table from filtered `orders2`
- it scanned all `order_items`
- then joined to `products`
- then aggregated by `category_id`

### What became clear
The main expensive part was not only filtering `orders2`.  
The query still had to:
- scan all `order_items`
- expand rows through the join
- join to `products`
- aggregate afterward

---

## 3. Plan shape after adding `idx_orders2_status_created`
### Index added
```sql
CREATE INDEX idx_orders2_status_created
    ON orders2 (status, created_at DESC);
```

### What changed
- `orders2` access changed from:
  - `Parallel Seq Scan`
  to:
  - `Bitmap Index Scan` + `Parallel Bitmap Heap Scan`

### What did **not** change much
- `order_items` was still scanned in full
- hash joins were still used
- aggregation pipeline still dominated later work
- total runtime stayed similar

### Main lesson
Improving the filtered parent table does not guarantee a big total speedup when:
- the child table is still scanned broadly
- the join multiplies rows
- aggregation still does heavy work

---

## 4. What `Hash` means
### My question
What is `Hash` in the execution plan?

### Answer
`Hash` is the step where PostgreSQL builds an in-memory hash table from one input so another input can probe it efficiently.

### Simple mental model
- `Hash` = build the dictionary
- `Hash Join` = use the dictionary to match rows

### In this query
- PostgreSQL built a hash table from filtered `orders2`
- `order_items` probed that hash by `oi.order_id = o.id`
- PostgreSQL also built a hash table from `products`
- the joined rows probed that hash by `oi.product_id = p.id`

---

## 5. Why total runtime stayed similar
### My question
Why did the index on `orders2(status, created_at)` not improve the whole query much?

### Answer
Because only the access path for `orders2` improved.

The query still had to do heavy work in later stages:
- scan all `order_items`
- expand rows after the join
- join to `products`
- aggregate by `category_id`

So the dominant cost moved away from the filtered parent table.

### Final understanding
A local improvement on one table does not always become a big end-to-end improvement if other stages dominate the plan.

---

## 6. Mini thinking question and my answers
### Question
For this Stage 3 query, what would likely help **more** than indexing `products(category_id)`?

1. better filter/selectivity on `orders2`
2. making `products` lookup faster by category
3. making `order_items` smaller to scan
4. pre-aggregating category sales

### My answers
1. maybe no since it's already filtered and reduced enough  
2. maybe yes but not much because it's 1:1 match for `order_items`  
3. yes because 1.5M rows were observed, so narrowing will be good  
4. maybe yes because aggregate was also a main factor for performance  

### Comments on my answers
#### 1. Better filter/selectivity on `orders2`
**Refined answer:** yes, this can still help a lot **if** it reduces the number of matched orders much further.  
The key is not whether `orders2` is already filtered “somewhat,” but whether a stronger filter would shrink the downstream join enough to matter.

#### 2. Making `products` lookup faster by category
**Refined answer:** not much for this query.  
That is the weak option here, because `products` is joined by `p.id`, not filtered by `category_id`. The category value is mainly used later for grouping.

#### 3. Making `order_items` smaller to scan
**Refined answer:** yes, strong answer.  
`order_items` is the biggest scanned table here and is a major source of row expansion. Reducing how much of it must be touched would help a lot.

#### 4. Pre-aggregating category sales
**Refined answer:** yes, also a strong answer.  
Because the query ends in join + aggregation, pre-aggregation can remove repeated heavy work, especially if this is a common reporting query.

### Best overall take
The strongest answers are:
- **3. making `order_items` smaller to scan**
- **4. pre-aggregating category sales**
- and also **1. improving parent selectivity further**, if the business query allows it

---

## 7. Final summary
A good summary of Stage 3 is:

> In a multi-join aggregate query, improving the filtered parent table may not change total runtime much if the child scan, row multiplication, and aggregation pipeline dominate the cost. In this case, indexing `orders2(status, created_at)` improved only the parent access path, while the main heavy work still came from scanning `order_items`, joining large row sets, and aggregating by category.
