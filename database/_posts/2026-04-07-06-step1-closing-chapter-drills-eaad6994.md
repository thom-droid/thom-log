---
layout: post
title: "06. Step1 - Closing Chapter - Drills"
date: 2026-04-07 12:35:33 +0000
categories: [database]
tags: [database, booking-system, indexes]
permalink: /database/06-step1-closing-chapter-drills-eaad6994/
source_note: "study plan/Arc1 - Booking System/Part2 - Indexes/06. Step1 - Closing Chapter - Drills.md"
---

[Database]({{ '/database/' | relative_url }}) / Study archive

# Drill 1 


```sql 
EXPLAIN ANALYZE
SELECT id, customer_id, created_at, status
FROM orders2
WHERE customer_id = 1001
ORDER BY created_at DESC
LIMIT 20;
```

## My answer 

Considering the table has already the composite index (customer_id, created_at DESC),

PostgreSQL will use bitmap path. 
1. the optimizer will first filter the table by customer_id 
2. then it will create bitmap to fetch status data, before it looks at the heap.
3. then it orders by created_at in descending order limiting only 20 rows.

## My idea on index

Using covering index or composite index including status will help the optimizer access to the data better

for example ,
``` SQL
create index idx_test ON orders2 (customer_id , created_at DESC) include (id, status) 
```

but this contains all columns, so the trade-offs should be considered.

## Actual Plan
```
                                                             QUERY PLAN                                                             

------------------------------------------------------------------------------------------------------------------------------------

 Limit  (cost=27.99..28.00 rows=6 width=32) (actual time=0.205..0.207 rows=3 loops=1)

   ->  Sort  (cost=27.99..28.00 rows=6 width=32) (actual time=0.203..0.204 rows=3 loops=1)

         Sort Key: created_at DESC

         Sort Method: quicksort  Memory: 25kB

         ->  Bitmap Heap Scan on orders2  (cost=4.47..27.91 rows=6 width=32) (actual time=0.181..0.190 rows=3 loops=1)

               Recheck Cond: (customer_id = 1001)

               Heap Blocks: exact=3

               ->  Bitmap Index Scan on idx_cid_created  (cost=0.00..4.47 rows=6 width=0) (actual time=0.167..0.168 rows=3 loops=1)

                     Index Cond: (customer_id = 1001)

 Planning Time: 0.536 ms

 Execution Time: 0.243 ms

(11 rows)
```


--- 

# Drill 2 - Broad Filter + aggregate

```sql
EXPLAIN ANALYZE
SELECT status, COUNT(*)
FROM orders2
WHERE created_at >= '2025-01-01'
GROUP BY status;
```

## My answer to question
Will an index on created_at be enough to make this dramatically fast, or does aggregation dominate?

If it was the totally different case without any other indexes, and I had to guess just from looking at the given query, I would say that it depends because even though the index might help with reducing rows created later than 2025 but if the filtered rows are still massive, then grouping them and counting work can be dominant. 

# Actual plan
```
                                                                  QUERY PLAN                                                                   

-----------------------------------------------------------------------------------------------------------------------------------------------

 Finalize GroupAggregate  (cost=8930.36..8931.37 rows=4 width=16) (actual time=67.558..70.106 rows=4 loops=1)

   Group Key: status

   ->  Gather Merge  (cost=8930.36..8931.29 rows=8 width=16) (actual time=67.552..70.099 rows=12 loops=1)

         Workers Planned: 2

         Workers Launched: 2

         ->  Sort  (cost=7930.34..7930.35 rows=4 width=16) (actual time=41.591..41.592 rows=4 loops=3)

               Sort Key: status

               Sort Method: quicksort  Memory: 25kB

               Worker 0:  Sort Method: quicksort  Memory: 25kB

               Worker 1:  Sort Method: quicksort  Memory: 25kB

               ->  Partial HashAggregate  (cost=7930.26..7930.30 rows=4 width=16) (actual time=41.560..41.561 rows=4 loops=3)

                     Group Key: status

                     Batches: 1  Memory Usage: 24kB

                     Worker 0:  Batches: 1  Memory Usage: 24kB

                     Worker 1:  Batches: 1  Memory Usage: 24kB

                     ->  Parallel Seq Scan on orders2  (cost=0.00..7408.17 rows=104418 width=8) (actual time=0.027..25.498 rows=83291 loops=3)

                           Filter: (created_at >= '2025-01-01 00:00:00'::timestamp without time zone)

                           Rows Removed by Filter: 83375

 Planning Time: 0.322 ms

 Execution Time: 70.201 ms

(20 rows)
```

it firstly looks into the table with sequential scan, with filter created_at, removing 80k rows from around the total 240k rows that are initially found. Then it groups up with the key, resulting in 4 rows aggregated.

## My idea on index
Though it removes 80k unnecessary rows by seq scan, the returned rows for aggregation are small enough for execution, so it looks just fine as it is. But if it has to consider performance later, a composite index like (created_at DESC, status) might help.


---

# Drill 3 - Parent-child join with narrow parent filter

# Query
```SQL
EXPLAIN ANALYZE
SELECT o.id, oi.product_id, oi.quantity
FROM orders2 o
JOIN order_items oi ON oi.order_id = o.id
WHERE o.customer_id = 1001;
```

# Main question
Will this look more like:
- nested loop + child index probe
    or
- hash join + broad scan?

## My Answer
It will use hash join + broad scan because even though the parent table(orders2) are filtered and narrowed enough by the filter customer_id, the child table (order_item) has to still lookup every matching rows from the parent table. To make access to the child table faster, hash will be used. And also it will have to visit the heap to fetch data, and need to build bitmap to access and store fetched data efficiently.

# Actual plan
```
                                                                    QUERY PLAN                                                                    

--------------------------------------------------------------------------------------------------------------------------------------------------

 Gather  (cost=1004.60..21397.04 rows=18 width=20) (actual time=1.643..117.658 rows=5 loops=1)

   Workers Planned: 2

   Workers Launched: 2

   ->  Hash Join  (cost=4.60..20395.24 rows=8 width=20) (actual time=59.859..97.760 rows=2 loops=3)

         Hash Cond: (oi.order_id = o.id)

         ->  Parallel Seq Scan on order_items oi  (cost=0.00..18750.00 rows=625000 width=20) (actual time=0.062..58.761 rows=500000 loops=3)

         ->  Hash  (cost=4.53..4.53 rows=6 width=8) (actual time=0.043..0.044 rows=3 loops=3)

               Buckets: 1024  Batches: 1  Memory Usage: 9kB

               ->  Index Only Scan using idx_cid_created on orders2 o  (cost=0.42..4.53 rows=6 width=8) (actual time=0.037..0.038 rows=3 loops=3)

                     Index Cond: (customer_id = '1001'::bigint)

                     Heap Fetches: 0

 Planning Time: 0.740 ms

 Execution Time: 117.704 ms

(13 rows)
```

## My idea on index
index only scan on orders2 effectively narrows the rows to match, but the child table still iterates the full table since it does not know which rows are matched. So adding index on order_id to match quickly to the parent table will help.

```sql
CREATE INDEX idx_order_items_oi ON order_items (order_id)
```

---

# Drill 4 — Join + top-N latest rows

```sql
EXPLAIN ANALYZE
SELECT c.id, c.name, o.id, o.created_at
FROM customers c
JOIN orders2 o ON o.customer_id = c.id
WHERE c.grade = 'VIP'
ORDER BY o.created_at DESC
LIMIT 20;
```

## Main Question
Which index is more likely to be the star?
- customers(grade, id)
- or orders2(created_at DESC, customer_id)

## My Answer
Just by a glance at the query, it looks like filtering and reducing the parent table with grade that is 'VIP' first seems appealing. But then it has to join the child table and order, removing other rows except 20. 

Joining method, though it is likely to be the nested loop by narrowing down joined rows, ordering the rows again is more expensive than ordering the rows first and limit since the later will not have to discard the ordered result. Thus, index on orders2 (created_at DESC, customer_id) will be more proper in this case. 

---

# Drill 5 — Join + aggregation + row explosion

```sql
EXPLAIN ANALYZE
SELECT c.grade, COUNT(*)
FROM customers c
JOIN orders2 o ON o.customer_id = c.id
JOIN order_items oi ON oi.order_id = o.id
WHERE o.created_at >= '2025-01-01'
GROUP BY c.grade;
```

## Things to Think about
- one order has many order_items
- grouping key is on customers side
- filter is on orders side
- final groups are few
- intermediate rows may be huge

## Main question
Where is the likely bottleneck?
- customer access
- order filtering
- order_items scan
- aggregation

## My Answer
By design it is likely that customers are not bigger than orders2 and order_items. order is filtered by created date, it may or may not be bottle neck if orders2 contains so much data and they are not ordered by the date. But the order_items scan will mostly likely be the time needed the most since it's child table that can grow to the rows returned by orders2. aggregation, there 's not much we can do not as long as we reduce the rows to be aggregated.

## My idea on index 
By text, the order of the optimizer look into will be 
1. filter from o.created_at >= '2025-01-01'
2. join customers with orders2 from filtered
3. order_items then. it will be seq scan
4. aggregate and merge
So possible index i think is:
```sql
CREATE INDEX idx_orders2_t1 ON orders2 (created_at desc, customer_id);
CREATE INDEX idx_order_items_t1 ON order_items (order_id);
CREATE INDEX idx_order_items_t1 ON order_items (order_id);
```
